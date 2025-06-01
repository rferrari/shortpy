import pandas as pd
import logging
from groq_ai import generate_ai_summary

logger = logging.getLogger(__name__)

def calculate_ema(df, period=21):
    df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    return df

def check_ema_crossover(df, short_period=9, long_period=21):
    short_ema, long_ema = df[f'EMA_{short_period}'].iloc[-1], df[f'EMA_{long_period}'].iloc[-1]
    prev_short, prev_long = df[f'EMA_{short_period}'].iloc[-2], df[f'EMA_{long_period}'].iloc[-2]
    return (
        prev_short > prev_long and short_ema < long_ema,  # Bearish crossover
        prev_short < prev_long and short_ema > long_ema   # Bullish crossover
    )

def check_reversal(df):
    high, low = df['high'].max(), df['low'].min()
    fib_levels = [high - (high - low) * r for r in (0.618, 0.5, 0.382)]
    last_close, ema_last = df['close'].iloc[-1], df['EMA_21'].iloc[-1]
    return (last_close < min(fib_levels)) and (last_close < ema_last)

def check_continuation(df):
    close_last, close_prev, ema_last = df['close'].iloc[-1], df['close'].iloc[-2], df['EMA_21'].iloc[-1]
    return close_last > ema_last and close_last > close_prev

def calculate_signal_confidence(df_short, df_long, df_higher):
    confidence = 0

    # Individual checks
    reversal_short = check_reversal(df_short)
    continuation_short = check_continuation(df_short)
    reversal_long = check_reversal(df_long)
    continuation_long = check_continuation(df_long)
    reversal_high = check_reversal(df_higher)
    continuation_high = check_continuation(df_higher)

    cross_down, cross_up = check_ema_crossover(df_short)

    rsi = df_short['RSI'].iloc[-1]
    macd = df_short['MACD'].iloc[-1]
    macd_sig = df_short['MACD_signal'].iloc[-1]

    # Weighted signal contribution
    if reversal_high or continuation_high:
        confidence += 20
    if reversal_long or continuation_long:
        confidence += 30
    if reversal_short or continuation_short:
        confidence += 40

    if cross_down or cross_up:
        confidence += 10
    if reversal_short and rsi < 40:
        confidence += 10
    if continuation_short and rsi > 60:
        confidence += 10
    if (macd > macd_sig and continuation_short) or (macd < macd_sig and reversal_short):
        confidence += 10

    return min(confidence, 100)

def generate_report(df_short, df_long, df_higher, symbol='N/A', detailed=False):
    confidence = calculate_signal_confidence(df_short, df_long, df_higher)

    if not detailed:
        if confidence >= 70:
            return f"📉 **Strong Signal Detected** (Confidence: {confidence}%)"
        elif confidence >= 40:
            return f"⚠️ **Moderate Signal** (Confidence: {confidence}%)"
        else:
            return f"❌ No significant signals (Confidence: {confidence}%)"

    high, low = df_short['high'].max(), df_short['low'].min()
    last_close = df_short['close'].iloc[-1]
    ema_21 = df_short['EMA_21'].iloc[-1]
    rsi = df_short['RSI'].iloc[-1]
    macd = df_short['MACD'].iloc[-1]
    macd_sig = df_short['MACD_signal'].iloc[-1]
    cross_down, cross_up = check_ema_crossover(df_short)

    direction = "SHORT" if check_reversal(df_short) else "LONG"
    stop_loss = high * 1.02 if direction == "SHORT" else low * 0.98
    target_1 = last_close * (0.98 if direction == "SHORT" else 1.02)
    target_2 = last_close * (0.96 if direction == "SHORT" else 1.04)

    report = (
        "```ini\n"
        f"Symbol           = {df_short.get('symbol', pd.Series(['N/A'])).iloc[0]}\n"
        f"Direction        = {'Bullish 📈 (Long)' if direction == 'LONG' else 'Bearish 📉 (Short)'}\n\n"
        f"Current Price    = {last_close:.4f}\n"
        f"EMA (21)         = {ema_21:.4f}\n"
        f"RSI              = {rsi:.2f}\n"
        f"MACD             = {macd:.4f} (Signal: {macd_sig:.4f})\n"
        f"EMA Crossover    = {'Bullish 🔺' if cross_up else ('Bearish 🔻' if cross_down else 'None ➖')}\n\n"
        f"Reversal Detected= {'Yes ✅' if check_reversal(df_short) else 'No ❌'}\n"
        f"Continuation     = {'Yes ✅' if check_continuation(df_short) else 'No ❌'}\n\n"
        f"Confidence Score = {confidence}%\n\n"
        f"Target 1         = {target_1:.4f}\n"
        f"Target 2         = {target_2:.4f}\n"
        f"Stop Loss        = {stop_loss:.4f}\n"
        "```"
    )

    try:
        prompt = generate_ai_analysis_prompt(symbol, confidence, direction, rsi, macd, macd_sig, cross_up, cross_down)
        report += f"\n💬 {generate_ai_summary(prompt)}"
    except Exception as e:
        logger.warning(f"AI analysis generation failed: {e}")

    return report

def generate_ai_analysis_prompt(symbol, confidence, direction, rsi, macd, macd_signal, crossover_up, crossover_down):
    trend = "uptrend" if direction == "LONG" else "downtrend"
    crossover = "EMA crossover indicating an uptrend" if crossover_up else (
        "EMA crossover indicating a downtrend" if crossover_down else "no EMA crossover"
    )
    return (
        f"Analysis for asset {symbol}:\n"
        f"- Likely direction: {trend}\n"
        f"- Signal confidence: {confidence}%\n"
        f"- Current RSI: {rsi:.2f}\n"
        f"- MACD: {macd:.4f}, Signal: {macd_signal:.4f}\n"
        f"- EMA condition: {crossover}\n\n"
        "Briefly explain to an experienced trader what this means. Then provide your final conclusion in a single sentence."
    )