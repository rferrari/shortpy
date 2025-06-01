# data.py
import requests
from binance.client import Client
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_binance_client(api_key, api_secret):
    logger.debug("Inicializando cliente Binance...")
    client = Client(api_key, api_secret)
    logger.debug("Cliente Binance inicializado com sucesso.")
    return client

def get_recent_futures(client):
    logger.debug("Buscando símbolos futuros PERPETUAIS na Binance...")
    info = client.futures_exchange_info()
    symbols = [s['symbol'] for s in info['symbols'] if s['contractType'] == 'PERPETUAL']
    logger.debug(f"Encontrados {len(symbols)} símbolos futuros.")
    return symbols
    
def get_klines(client, symbol, interval='15m', limit=100):
    logger.debug(f"Buscando candles para {symbol} (intervalo {interval}, limite {limit})...")
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    logger.debug(f"{len(klines)} candles recebidos para {symbol}.")

    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])

    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)

    # Add the symbol column here
    df['symbol'] = symbol

    logger.debug(f"DataFrame montado para {symbol} com {df.shape[0]} linhas.")
    return df


def obter_moedas_com_capitalizacao(min_cap, max_cap):
    logger.debug(f"Consultando moedas no CoinGecko com market cap entre {min_cap} e {max_cap} USD...")

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1
    }

    try:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        moedas = resposta.json()
        logger.debug(f"Recebidas {len(moedas)} moedas do CoinGecko.")
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar moedas no CoinGecko: {e}")
        return []

    moedas_filtradas = [
        moeda for moeda in moedas
        if moeda.get("market_cap") and min_cap <= moeda["market_cap"] <= max_cap
    ]

    logger.debug(f"{len(moedas_filtradas)} moedas filtradas no intervalo de capitalização definido.")
    logger.debug(f"Moedas filtradas: {[m['id'] for m in moedas_filtradas]}")

    return moedas_filtradas
