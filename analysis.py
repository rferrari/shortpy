import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_ema(df, period=21):
    logger.debug(f"Calculando EMA de período {period}...")
    df['EMA'] = df['close'].ewm(span=period, adjust=False).mean()
    logger.debug("EMA calculada e adicionada ao DataFrame.")
    return df

def check_reversal(df):
    high = df['high'].max()
    low = df['low'].min()
    fib_0618 = high - (high - low) * 0.618
    last_close = df['close'].iloc[-1]
    ema_last = df['EMA'].iloc[-1]

    logger.debug(f"Checando reversão Fibonacci:")
    logger.debug(f"  Máximo: {high:.4f}, Mínimo: {low:.4f}, Fib 0.618: {fib_0618:.4f}")
    logger.debug(f"  Último fechamento: {last_close:.4f}, Última EMA: {ema_last:.4f}")

    if last_close < fib_0618 and last_close < ema_last:
        logger.debug("Condição de reversão detectada: TRUE")
        return True
    logger.debug("Condição de reversão não satisfeita: FALSE")
    return False

def check_continuation(df):
    close_last = df['close'].iloc[-1]
    close_prev = df['close'].iloc[-2]
    ema_last = df['EMA'].iloc[-1]

    logger.debug("Checando padrão de continuidade:")
    logger.debug(f"  Último fechamento: {close_last:.4f}, Fechamento anterior: {close_prev:.4f}, Última EMA: {ema_last:.4f}")

    if close_last > ema_last and close_last > close_prev:
        logger.debug("Condição de continuidade detectada: TRUE")
        return True
    logger.debug("Condição de continuidade não satisfeita: FALSE")
    return False
