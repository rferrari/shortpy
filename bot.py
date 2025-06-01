import discord
import os
import asyncio
import logging
from dotenv import load_dotenv
from data import (
    obter_moedas_com_capitalizacao,
    get_binance_client,
    get_recent_futures,
    get_klines
)
from analysis import (
    calculate_ema, 
    check_reversal,
    check_continuation, 
    calculate_rsi, 
    calculate_macd,
    calculate_signal_confidence,
    check_ema_crossover,
    generate_report
)
from positions import Position, PositionManager
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CANAL_ID = int(os.getenv('CANAL_ID'))

client_binance = get_binance_client(API_KEY, API_SECRET)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  # enable reaction events

position_manager = PositionManager()

# Color codes for embeds
COLOR_LONG = 0x2ecc71  # Green
COLOR_SHORT = 0xe74c3c  # Red

class BotShort(discord.Client):
    async def setup_hook(self):
        self.bg_task_monitor = asyncio.create_task(self.monitorar())
        self.bg_task_positions = asyncio.create_task(self.monitorar_posicoes())

    async def on_ready(self):
        logging.info(f"🟢 Bot online como {self.user}")

    async def monitorar(self):
        canal = await self.fetch_channel(CANAL_ID)
        analisados = set()

        min_cap = 200_000_000
        max_cap = 350_000_000

        while True:
            try:
                moedas_gecko = obter_moedas_com_capitalizacao(min_cap, max_cap)
                symbols_binance = get_recent_futures(client_binance)

                symbols_filtrados = []
                for moeda in moedas_gecko:
                    sym = moeda['symbol'].upper()
                    sym_usdt = sym + "USDT"
                    if sym_usdt in symbols_binance:
                        symbols_filtrados.append(sym_usdt)

                for symbol in symbols_filtrados:
                    if symbol in analisados:
                        continue

                    logging.info(f"🔍 Analisando símbolo em background: {symbol}")
                    try:
                        df_15m = get_klines(client_binance, symbol, interval='15m')
                        df_1h = get_klines(client_binance, symbol, interval='1h')
                        df_4h = get_klines(client_binance, symbol, interval='4h')

                        for df in (df_15m, df_1h, df_4h):
                            df = calculate_ema(df, 9)
                            df = calculate_ema(df, 21)
                            df = calculate_rsi(df)
                            df = calculate_macd(df)

                        confidence = calculate_signal_confidence(df_15m, df_1h, df_4h)

                        crossover_down, crossover_up = check_ema_crossover(df_15m)
                        reversal = check_reversal(df_15m)
                        continuation = check_continuation(df_15m)

                        # Apenas alerta se sinal bearish forte para SHORT
                        if confidence == 100 and (crossover_down or reversal) and not continuation:
                            # Montar dados para nova posição SHORT
                            high = df_15m['high'].max()
                            low = df_15m['low'].min()
                            last_close = df_15m['close'].iloc[-1]

                            stop_loss = high * 1.02
                            target_1 = last_close * 0.98
                            target_2 = last_close * 0.96
                            target_3 = last_close * 0.94  # novo target para 3 níveis

                            position = Position(
                                symbol=symbol,
                                direction="SHORT",
                                entry_price=last_close,
                                targets=[target_1, target_2, target_3],
                                stop_loss=stop_loss
                            )
                            position_manager.add_position(position)

                            embed = discord.Embed(
                                title=f"🚨 Nova posição SHORT: {symbol}",
                                description=(
                                    f"**Entrada:** {last_close:.4f}\n"
                                    f"**Stop Loss:** {stop_loss:.4f}\n"
                                    f"**Targets:** {target_1:.4f}, {target_2:.4f}, {target_3:.4f}\n\n"
                                    f"Motivo: Sinal 100% confirmado, crossover e reversão bearish."
                                ),
                                color=COLOR_SHORT,
                                timestamp=datetime.utcnow()
                            )
                            embed.set_footer(text="Confirme com ✅")

                            msg = await canal.send(embed=embed)
                            position.message = msg
                            await msg.add_reaction('✅')

                            analisados.add(symbol)
                        else:
                            logging.info(f"Sinal não bearish 100% para {symbol}, ignorado.")

                    except Exception as e:
                        logging.warning(f"⚠️ Erro ao analisar {symbol} no monitoramento: {e}")

                await asyncio.sleep(60)

            except Exception as e:
                logging.error(f"❌ Erro geral no monitoramento: {e}")
                await asyncio.sleep(10)

    async def monitorar_posicoes(self):
        canal = await self.fetch_channel(CANAL_ID)
        while True:
            try:
                positions = position_manager.get_positions()
                if not positions:
                    await asyncio.sleep(30)
                    continue

                for pos in positions:
                    if pos.closed:
                        continue
                    try:
                        df_15m = get_klines(client_binance, pos.symbol, interval='15m')
                        last_price = df_15m['close'].iloc[-1]

                        # Verifica se atingiu targets
                        target_hit = pos.check_targets(last_price)
                        if target_hit and target_hit != pos.last_reported_target:
                            gain_pct = ((pos.entry_price - target_hit) / pos.entry_price) * 100 if pos.direction == "SHORT" else ((target_hit - pos.entry_price) / pos.entry_price) * 100
                            text = (
                                f"🎯 **Target atingido:** {target_hit:.4f} para {pos.symbol}\n"
                                f"💰 Ganho parcial: {gain_pct:.2f}%"
                            )
                            pos.last_reported_target = target_hit
                            # Edita mensagem original com atualização
                            if pos.message:
                                embed = pos.message.embeds[0]
                                embed.add_field(name=f"Target {pos.targets.index(target_hit)+1} atingido", value=text, inline=False)
                                await pos.message.edit(embed=embed)
                            else:
                                await canal.send(text)

                        # Verifica stop loss
                        if pos.check_stop_loss(last_price):
                            pos.close(last_price)
                            loss_pct = ((pos.entry_price - last_price) / pos.entry_price) * 100 if pos.direction == "SHORT" else ((last_price - pos.entry_price) / pos.entry_price) * 100
                            text = (
                                f"🛑 **Stop Loss acionado para {pos.symbol}**\n"
                                f"Preço: {last_price:.4f}\n"
                                f"Perda: {loss_pct:.2f}%\n"
                                f"Posição fechada."
                            )
                            if pos.message:
                                embed = pos.message.embeds[0]
                                embed.color = 0x95a5a6  # cinza
                                embed.add_field(name="❌ Posição fechada (Stop Loss)", value=text, inline=False)
                                embed.set_footer(text=f"Fechada em {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                                await pos.message.edit(embed=embed)
                            else:
                                await canal.send(text)
                            position_manager.remove_position(pos.symbol)

                        # Verifica se todos targets atingidos para fechar posição
                        elif pos.last_reported_target == pos.targets[-1]:
                            pos.close(last_price)
                            gain_pct = ((pos.entry_price - last_price) / pos.entry_price) * 100 if pos.direction == "SHORT" else ((last_price - pos.entry_price) / pos.entry_price) * 100
                            text = (
                                f"✅ **Todos targets atingidos para {pos.symbol}**\n"
                                f"Preço fechamento: {last_price:.4f}\n"
                                f"Ganho total: {gain_pct:.2f}%\n"
                                f"Posição fechada."
                            )
                            if pos.message:
                                embed = pos.message.embeds[0]
                                embed.color = 0x27ae60  # verde escuro
                                embed.add_field(name="✅ Posição fechada (Targets atingidos)", value=text, inline=False)
                                embed.set_footer(text=f"Fechada em {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                                await pos.message.edit(embed=embed)
                            else:
                                await canal.send(text)
                            position_manager.remove_position(pos.symbol)

                    except Exception as e:
                        logging.warning(f"⚠️ Erro no monitoramento de posição {pos.symbol}: {e}")

                await asyncio.sleep(60)

            except Exception as e:
                logging.error(f"❌ Erro no monitoramento de posições: {e}")
                await asyncio.sleep(30)

bot = BotShort(intents=intents)
bot.run(DISCORD_TOKEN)
