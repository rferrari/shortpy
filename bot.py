#main bot.py
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

# 🔧 Logging configurado (terminal + arquivo)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        # logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 📦 Carrega variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CANAL_ID = int(os.getenv('CANAL_ID'))

# 🔗 Inicializa cliente Binance
client_binance = get_binance_client(API_KEY, API_SECRET)

# ⚙️ Intents do Discord
intents = discord.Intents.default()
intents.message_content = True

# 🤖 Classe principal do bot
class BotShort(discord.Client):
    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.monitorar())

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

                        # Recalculate explicitly (you can wrap this logic into a helper if needed)
                        df_15m = calculate_macd(calculate_rsi(calculate_ema(calculate_ema(df_15m, 9), 21)))
                        df_1h  = calculate_macd(calculate_rsi(calculate_ema(calculate_ema(df_1h, 9), 21)))
                        df_4h  = calculate_macd(calculate_rsi(calculate_ema(calculate_ema(df_4h, 9), 21)))

                        confidence = calculate_signal_confidence(df_15m, df_1h, df_4h)

                        crossover_down, crossover_up = check_ema_crossover(df_15m)
                        reversal = check_reversal(df_15m)
                        continuation = check_continuation(df_15m)

                        # Only send alert if bearish (short) signal:
                        if confidence >= 70 and (crossover_down or reversal) and not continuation:
                            report = generate_report(df_15m, df_1h, df_4h, detailed=True)

                            # Add the direction explicitly here
                            report = report.replace("Direction = N/A", "Direction = Bearish 📉 (Short)")

                            await canal.send(f"📉 *Alerta SHORT para `{symbol}`*\n{report}")
                            analisados.add(symbol)
                        else:
                            logging.info(f"Sinal não bearish para {symbol}, ignorado.")

                    except Exception as e:
                        logging.warning(f"⚠️ Erro ao analisar {symbol} no monitoramento: {e}")

                await asyncio.sleep(60)

            except Exception as e:
                logging.error(f"❌ Erro geral no monitoramento: {e}")
                await asyncio.sleep(10)


# 🚀 Executa o bot
bot = BotShort(intents=intents)
bot.run(DISCORD_TOKEN)
