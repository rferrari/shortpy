
from binance.client import Client
import time
import datetime
import requests  # <- nova lib pra mandar pro Discord

# CONFIGURAÇÕES

DISCORD_WEBHOOK_URL = 'TUA_WEBHOOK_URL_AQUI'
ALVO = 100000  # valor de alerta em dólares

# Cliente Binance
client = Client(API_KEY, API_SECRET)

# Função hora
def agora():
    return datetime.datetime.now().strftime("%H:%M:%S")

# Função pra mandar mensagem pro Discord
def manda_discord(msg):
    data = {"content": msg}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"[{agora()}] Alerta enviado no Discord 🚀")
    except Exception as e:
        print(f"[{agora()}] Erro ao mandar Discord: {e}")

# Loop principal
alerta_enviado = False  # garante que só envia 1 vez

while True:
    try:
        ticker = client.get_symbol_ticker(symbol='BTCUSDT')
        preco = float(ticker['price'])
        print(f"[{agora()}] Preço do BTC: {preco:.2f} USD")

        if preco >= ALVO and not alerta_enviado:
            mensagem = f"🚨 O BTC bateu {preco:.2f} USD! 🚀🚀🚀"
            manda_discord(mensagem)
            alerta_enviado = True

        time.sleep(10)

    except Exception as e:
        print(f"[{agora()}] Deu ruim: {e}")
        time.sleep(10)
