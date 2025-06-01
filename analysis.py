#analysis.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_ema(df, period=21):
    # EMA (Exponential Moving Average) gives more weight to recent prices to identify trends.
    # Here, we calculate EMA for the given period (default 21), smoothing price data to see trend direction.
    df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    # RSI (Relative Strength Index) measures momentum to identify overbought or oversold conditions.
    # RSI oscillates between 0 and 100:
    # Above 70 = overbought (possible sell signal)
    # Below 30 = oversold (possible buy signal)
    delta = df['close'].diff()  # Price changes between periods
    gain = delta.where(delta > 0, 0)  # Gains on up days
    loss = -delta.where(delta < 0, 0)  # Losses on down days
    avg_gain = gain.rolling(window=period).mean()  # Average gain over period
    avg_loss = loss.rolling(window=period).mean()  # Average loss over period
    rs = avg_gain / avg_loss  # Relative strength
    df['RSI'] = 100 - (100 / (1 + rs))  # Normalize to 0-100 scale
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    # MACD (Moving Average Convergence Divergence) indicates trend direction and momentum.
    # It is the difference between two EMAs (fast and slow) and a signal line (EMA of MACD).
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow  # MACD line: momentum indicator
    df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()  # Signal line for MACD crossovers
    return df

def check_ema_crossover(df, short_period=9, long_period=21):
    # EMA crossover is a classic trend-following signal:
    # - When short-term EMA crosses above long-term EMA → bullish signal (price likely rising)
    # - When short-term EMA crosses below long-term EMA → bearish signal (price likely falling)
    short_ema = df[f'EMA_{short_period}'].iloc[-1]
    long_ema = df[f'EMA_{long_period}'].iloc[-1]
    prev_short_ema = df[f'EMA_{short_period}'].iloc[-2]
    prev_long_ema = df[f'EMA_{long_period}'].iloc[-2]

    crossover_down = prev_short_ema > prev_long_ema and short_ema < long_ema  # Bearish crossover
    crossover_up = prev_short_ema < prev_long_ema and short_ema > long_ema    # Bullish crossover

    return crossover_down, crossover_up

def check_reversal(df):
    # Check for potential price reversal zones using Fibonacci retracement levels and EMA:
    # Fibonacci levels (0.618, 0.5, 0.382) are common retracement points where price might reverse.
    # If price is below these retracement levels and below EMA(21), it suggests a bearish reversal.
    high = df['high'].max()
    low = df['low'].min()
    fib_0618 = high - (high - low) * 0.618
    fib_05 = high - (high - low) * 0.5
    fib_0382 = high - (high - low) * 0.382
    last_close = df['close'].iloc[-1]
    ema_last = df['EMA_21'].iloc[-1]

    cond_fib = last_close < fib_0618 or last_close < fib_05 or last_close < fib_0382
    cond_ema = last_close < ema_last

    # Both conditions need to be met to flag a reversal signal
    if cond_fib and cond_ema:
        return True
    return False

def check_continuation(df):
    # Check if price is continuing an upward trend:
    # Price closing above EMA(21) and above previous close indicates bullish momentum.
    close_last = df['close'].iloc[-1]
    close_prev = df['close'].iloc[-2]
    ema_last = df['EMA_21'].iloc[-1]

    if close_last > ema_last and close_last > close_prev:
        return True
    return False

def calculate_signal_confidence(df_short, df_long, df_higher):
    """
    This function quantifies how strong a trading signal is, based on multiple technical factors:
    - Signals confirmed across multiple timeframes (short, long, higher) add reliability.
    - EMA crossovers add confidence that a trend is shifting.
    - RSI conditions: Oversold (<40) reinforces reversal; Overbought (>60) reinforces continuation.
    - MACD positioning relative to its signal line helps confirm momentum.
    The final score (0-100) measures overall confidence in the signal.
    """
    confidence = 0

    reversal_short = check_reversal(df_short)
    continuation_short = check_continuation(df_short)
    crossover_down, crossover_up = check_ema_crossover(df_short)
    rsi_short = df_short['RSI'].iloc[-1]
    macd_short = df_short['MACD'].iloc[-1]
    macd_signal_short = df_short['MACD_signal'].iloc[-1]

    reversal_long = check_reversal(df_long)
    continuation_long = check_continuation(df_long)

    reversal_high = check_reversal(df_higher)
    continuation_high = check_continuation(df_higher)

    # Assign points to each confirmed signal, prioritizing multi-timeframe agreement
    if reversal_short or continuation_short:
        confidence += 40
    if reversal_long or continuation_long:
        confidence += 30
    if reversal_high or continuation_high:
        confidence += 20

    if crossover_down or crossover_up:
        confidence += 10

    # Add points for RSI confirming overbought/oversold conditions that support the reversal or continuation signals
    if reversal_short and rsi_short < 40:
        confidence += 10
    if continuation_short and rsi_short > 60:
        confidence += 10

    # Add points if MACD supports the signal momentum
    if (macd_short > macd_signal_short and continuation_short) or (macd_short < macd_signal_short and reversal_short):
        confidence += 10

    # Limit confidence to 100%
    confidence = min(confidence, 100)

    return confidence

def generate_report(df_short, df_long, df_higher, symbol='N/A', detailed=False):
    # Generates a human-readable summary of the technical analysis, including:
    # - Overall confidence score
    # - Direction of expected price movement (Bullish/Long or Bearish/Short)
    # - Current price and key indicator values
    # - Targets for profit-taking and stop loss levels
    confidence = calculate_signal_confidence(df_short, df_long, df_higher)

    if not detailed:
        # Provide a quick summary signal strength:
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

    # Determine trade direction based on reversal signals
    if check_reversal(df_short):
        direction = "SHORT"  # Expecting price drop; bearish position
        stop_loss = high * 1.02  # Stop loss above recent high for risk control
        target_1 = last_close * 0.98  # First profit target ~2% below entry
        target_2 = last_close * 0.96  # Second profit target ~4% below entry
    else:
        direction = "LONG"  # Expecting price rise; bullish position
        stop_loss = low * 0.98  # Stop loss below recent low
        target_1 = last_close * 1.02  # First profit target ~2% above entry
        target_2 = last_close * 1.04  # Second profit target ~4% above entry

    # Format the detailed report (e.g., for Discord message)
    report = (
        "```ini\n"
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