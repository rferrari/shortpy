import aiohttp
import asyncio
import pandas as pd
import logging

async def obter_moedas_com_capitalizacao(min_cap, max_cap):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1,
        'sparkline': 'false'  # <-- CORRIGIDO AQUI
    }

    moedas = []
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            params['page'] = page
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        logging.warning(f"⚠️ CoinGecko retornou status {resp.status}")
                        break
                    data = await resp.json()
                    if not isinstance(data, list):
                        logging.warning(f"⚠️ Resposta inesperada do CoinGecko: {data}")
                        break
                    for coin in data:
                        cap = coin.get('market_cap', 0)
                        if isinstance(cap, (int, float)) and min_cap <= cap <= max_cap:
                            moedas.append(coin)
            except Exception as e:
                logging.error(f"❌ Erro ao acessar CoinGecko: {e}")
                break

            page += 1
            if page > 5:
                break

    return moedas



# Example: Get recent futures symbols from Binance client
async def get_recent_futures(client_binance):
    # Assuming client_binance is an instance of python-binance async client or similar
    info = await client_binance.futures_exchange_info()
    symbols = [s['symbol'] for s in info['symbols'] if s['contractType'] == 'PERPETUAL']
    return symbols

# Example: Get candlestick data and convert to pandas DataFrame
def get_klines(client_binance, symbol, interval='15m', limit=100):
    # This function is sync because you call it synchronously in your bot_events
    # If you have async client, consider adapting
    klines = client_binance.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    # Convert types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    return df
