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
from analysis import calculate_ema, check_reversal, check_continuation

# 🔧 Logging configurado (terminal + arquivo)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
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

        min_cap = 100_000_000  # 100 milhões
        max_cap = 950_000_000  # 150 milhões

        while True:
            try:
                # Pega moedas do CoinGecko com market cap entre min_cap e max_cap
                moedas_gecko = obter_moedas_com_capitalizacao(min_cap, max_cap)
                logging.debug(f"🔍 {len(moedas_gecko)} moedas filtradas por market cap no CoinGecko")

                # Pega símbolos dos futuros perpétuos na Binance
                symbols_binance = get_recent_futures(client_binance)
                logging.debug(f"🔍 {len(symbols_binance)} símbolos de futuros na Binance")

                # Filtra os símbolos disponíveis que estão nas duas listas
                symbols_filtrados = []
                for moeda in moedas_gecko:
                    sym = moeda['symbol'].upper()
                    sym_usdt = sym + "USDT"
                    if sym_usdt in symbols_binance:
                        symbols_filtrados.append(sym_usdt)

                logging.debug(f"🔍 {len(symbols_filtrados)} símbolos filtrados para análise")

                for symbol in symbols_filtrados:
                    logging.debug(f"⏭ Analisando: {symbol}")
                    if symbol in analisados:
                        logging.debug(f"⏭ Já analisado: {symbol}")
                        continue

                    df = get_klines(client_binance, symbol)
                    df = calculate_ema(df)

                    if check_reversal(df) or check_continuation(df):
                        logging.info(f"📉 Sinal de SHORT detectado: {symbol}")
                        mensagem = await canal.send(
                            f"📉 Sinal de SHORT detectado em `{symbol}`\nResponder com `ok` para confirmar entrada."
                        )

                        def check(msg):
                            return msg.channel == canal and msg.content.lower() == "ok"

                        try:
                            resposta = await self.wait_for("message", timeout=30.0, check=check)
                            logging.info(f"✅ Ordem confirmada via Discord para {symbol}")
                            await canal.send(f"✅ Ordem executada: SHORT em {symbol} por confirmação manual.")
                        except asyncio.TimeoutError:
                            logging.info(f"⌛ Nenhuma confirmação para {symbol}, pulando.")
                            await canal.send(f"⏳ Ninguém respondeu. Continuando monitoramento de `{symbol}`.")

                        analisados.add(symbol)

                await asyncio.sleep(60)

            except Exception as e:
                logging.error(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(10)

# 🚀 Executa o bot
bot = BotShort(intents=intents)
bot.run(DISCORD_TOKEN)
