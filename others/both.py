#analysis.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_ema(df, period=21):
    logger.debug(f"Calculando EMA de período {period}...")
    df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    logger.debug("EMA calculada e adicionada ao DataFrame.")
    return df

def calculate_rsi(df, period=14):
    logger.debug(f"Calculando RSI de período {period}...")
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    logger.debug("RSI calculado e adicionado ao DataFrame.")
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    logger.debug("Calculando MACD...")
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    logger.debug("MACD calculado e adicionado ao DataFrame.")
    return df

def check_ema_crossover(df, short_period=9, long_period=21):
    short_ema = df[f'EMA_{short_period}'].iloc[-1]
    long_ema = df[f'EMA_{long_period}'].iloc[-1]
    prev_short_ema = df[f'EMA_{short_period}'].iloc[-2]
    prev_long_ema = df[f'EMA_{long_period}'].iloc[-2]

    crossover_down = prev_short_ema > prev_long_ema and short_ema < long_ema
    crossover_up = prev_short_ema < prev_long_ema and short_ema > long_ema

    logger.debug(f"EMA crossover check: crossover_down={crossover_down}, crossover_up={crossover_up}")
    return crossover_down, crossover_up

def check_reversal(df):
    high = df['high'].max()
    low = df['low'].min()
    fib_0618 = high - (high - low) * 0.618
    fib_05 = high - (high - low) * 0.5
    fib_0382 = high - (high - low) * 0.382
    last_close = df['close'].iloc[-1]
    ema_last = df['EMA_21'].iloc[-1]

    logger.debug(f"Checando reversão Fibonacci e EMA:")
    logger.debug(f"  Máximo: {high:.4f}, Mínimo: {low:.4f}, Fib 0.618: {fib_0618:.4f}, Fib 0.5: {fib_05:.4f}, Fib 0.382: {fib_0382:.4f}")
    logger.debug(f"  Último fechamento: {last_close:.4f}, Última EMA(21): {ema_last:.4f}")

    # More conditions for reversal
    cond_fib = last_close < fib_0618 or last_close < fib_05 or last_close < fib_0382
    cond_ema = last_close < ema_last

    if cond_fib and cond_ema:
        logger.debug("Condição de reversão detectada: TRUE")
        return True
    logger.debug("Condição de reversão não satisfeita: FALSE")
    return False

def check_continuation(df):
    close_last = df['close'].iloc[-1]
    close_prev = df['close'].iloc[-2]
    ema_last = df['EMA_21'].iloc[-1]

    logger.debug("Checando padrão de continuidade:")
    logger.debug(f"  Último fechamento: {close_last:.4f}, Fechamento anterior: {close_prev:.4f}, Última EMA(21): {ema_last:.4f}")

    if close_last > ema_last and close_last > close_prev:
        logger.debug("Condição de continuidade detectada: TRUE")
        return True
    logger.debug("Condição de continuidade não satisfeita: FALSE")
    return False

def calculate_signal_confidence(df_short, df_long, df_higher):
    """
    Calculate a confidence score (0-100) for the signal based on:
    - Confirmation in multiple timeframes
    - EMA crossover presence
    - RSI and MACD signals
    """
    confidence = 0

    # Short timeframe signals
    reversal_short = check_reversal(df_short)
    continuation_short = check_continuation(df_short)
    crossover_down, crossover_up = check_ema_crossover(df_short)
    rsi_short = df_short['RSI'].iloc[-1]
    macd_short = df_short['MACD'].iloc[-1]
    macd_signal_short = df_short['MACD_signal'].iloc[-1]

    # Long timeframe signals
    reversal_long = check_reversal(df_long)
    continuation_long = check_continuation(df_long)

    # Higher timeframe signals (e.g., 4h)
    reversal_high = check_reversal(df_higher)
    continuation_high = check_continuation(df_higher)

    logger.debug(f"RSI short timeframe: {rsi_short:.2f}")

    # Basic scoring rules:
    if reversal_short or continuation_short:
        confidence += 40

    # Confirmed by longer timeframe?
    if reversal_long or continuation_long:
        confidence += 30

    if reversal_high or continuation_high:
        confidence += 20

    # EMA crossover on short timeframe adds confidence
    if crossover_down or crossover_up:
        confidence += 10

    # RSI confirmation: Overbought (>70) or oversold (<30)
    if reversal_short and rsi_short < 40:
        confidence += 10
    if continuation_short and rsi_short > 60:
        confidence += 10

    # MACD confirmation (MACD above/below signal line)
    if (macd_short > macd_signal_short and continuation_short) or (macd_short < macd_signal_short and reversal_short):
        confidence += 10

    # Cap confidence at 100
    confidence = min(confidence, 100)

    logger.debug(f"Signal confidence score: {confidence}")
    return confidence

def generate_report(df_short, df_long, df_higher, symbol='N/A', detailed=False):
    confidence = calculate_signal_confidence(df_short, df_long, df_higher)

    if not detailed:
        if confidence >= 70:
            return f"📉 **Strong Signal Detected** (Confidence: {confidence}%)"
        elif confidence >= 40:
            return f"⚠️ **Moderate Signal** (Confidence: {confidence}%)"
        else:
            return f"❌ No significant signals (Confidence: {confidence}%)"

    high = df_short['high'].max()
    low = df_short['low'].min()
    last_close = df_short['close'].iloc[-1]
    ema_21 = df_short['EMA_21'].iloc[-1]
    rsi = df_short['RSI'].iloc[-1]
    macd = df_short['MACD'].iloc[-1]
    macd_signal = df_short['MACD_signal'].iloc[-1]
    crossover_down, crossover_up = check_ema_crossover(df_short)

    if check_reversal(df_short):
        direction = "SHORT"
        stop_loss = high * 1.02
        target_1 = last_close * 0.98
        target_2 = last_close * 0.96
    else:
        direction = "LONG"
        stop_loss = low * 0.98
        target_1 = last_close * 1.02
        target_2 = last_close * 1.04

    # Using ini-style formatting for that neat Discord code box
    report = (
        "```ini\n"
        # f"[ Multi-Timeframe Analysis Report ]\n"
        f"Symbol           = {df_short['symbol'].iloc[0] if 'symbol' in df_short.columns else 'N/A'}\n"
        f"Direction        = {'Bullish 📈 (Long)' if direction == 'LONG' else 'Bearish 📉 (Short)'}\n\n"
        f"Current Price    = {last_close:.4f}\n"
        f"EMA (21)         = {ema_21:.4f}\n"
        f"RSI              = {rsi:.2f}\n"
        f"MACD             = {macd:.4f} (Signal: {macd_signal:.4f})\n"
        f"EMA Crossover    = {'Bullish 🔺' if crossover_up else ('Bearish 🔻' if crossover_down else 'None ➖')}\n\n"
        f"Reversal Detected= {'Yes ✅' if check_reversal(df_short) else 'No ❌'}\n"
        f"Continuation     = {'Yes ✅' if check_continuation(df_short) else 'No ❌'}\n\n"
        f"Confidence Score = {confidence}%\n\n"
        f"Target 1         = {target_1:.4f}\n"
        f"Target 2         = {target_2:.4f}\n"
        f"Stop Loss        = {stop_loss:.4f}\n"
        "```"
    )
    return report
