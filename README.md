# 📉 Crypto SHORT Signal Discord Bot

This is a **Discord bot** that scans the crypto futures market on Binance for potential **SHORT trading signals**, based on **Fibonacci retracements**, **EMA**, and **price action patterns**. It filters assets by market capitalization using CoinGecko, performs analysis, and posts alerts to a Discord channel for manual confirmation.

---

## 🚀 What It Does

- Connects to Binance Futures and CoinGecko APIs.
- Filters coins with a market cap between `$100M` and `$950M`.
- Matches these with available perpetual futures on Binance.
- Retrieves recent price data (`15m` interval).
- Calculates **Exponential Moving Average (EMA)**.
- Applies two signal strategies:
  - **Reversal detection** (based on Fibonacci 0.618 retracement + EMA).
  - **Continuation detection** (based on price momentum + EMA).
- Posts a message in a Discord channel when a signal is detected.
- Waits for a manual `ok` confirmation from any user to simulate trade execution.

---

# How the Trading Signal Bot Works: Overview for Financial Analysts

This bot continuously monitors selected cryptocurrencies (or assets) and generates trading signals based on technical analysis. It’s designed to help identify potential **buy** or **sell** opportunities by analyzing price movements using well-known financial indicators and multi-timeframe confirmation.

---

## 1. Data Collection: Gathering Price Information

- The bot collects recent price data — including **open, high, low, and close prices** — over multiple timeframes (e.g., short-term like 5-15 minutes, medium-term like 1 hour, and longer-term like 4 hours).
- This multi-timeframe approach helps understand both immediate and broader market trends.

---

## 2. Step One — Calculating Key Technical Indicators

For each timeframe, the bot calculates:

- **EMA (Exponential Moving Average):** Highlights recent price trends by smoothing out price fluctuations. The bot uses EMA with periods like 9, 21, etc., to detect short and longer-term trends.
- **RSI (Relative Strength Index):** Measures momentum to spot if the asset is overbought (potential sell) or oversold (potential buy).
- **MACD (Moving Average Convergence Divergence):** Shows momentum changes and trend direction by comparing two EMAs and their difference.

---

## 3. Step Two — Identifying Signals on Each Timeframe

The bot looks for two primary types of signals:

- **Reversal Signals:** Indicate potential turning points where price might change direction. These are detected using:
  - Fibonacci retracement levels (common price pullback points)
  - Price relation to EMA (price crossing below EMA suggests a reversal down, or vice versa)
- **Continuation Signals:** Suggest that the current trend is strong and likely to continue, confirmed when:
  - Price closes above EMA and is rising compared to the previous close (for bullish continuation).

---

## 4. Step Three — EMA Crossover Confirmation

- The bot checks if the short-term EMA crosses over the longer-term EMA, a classic signal:
  - **Bullish crossover:** short-term EMA crosses above long-term EMA → potential buy signal.
  - **Bearish crossover:** short-term EMA crosses below long-term EMA → potential sell signal.

---

## 5. Step Four — Multi-Timeframe Signal Confirmation

- To increase confidence, the bot verifies whether reversal or continuation signals appear **consistently across multiple timeframes**.
- A signal appearing on short, medium, and higher timeframes is stronger and more reliable.

---

## 6. Step Five — Scoring the Signal Confidence

The bot assigns a **confidence score (0-100%)** to the signal based on:

- Presence of reversal or continuation signals on short, long, and higher timeframes.
- EMA crossover occurrence.
- RSI levels supporting the signal (e.g., oversold RSI confirms a reversal buy).
- MACD momentum agreeing with the direction.

A higher score means a stronger, more reliable signal.

---

## 7. Step Six — Generating the Trading Report

Based on the confidence score and signal direction, the bot creates a summary report that includes:

- Whether the signal is **strong**, **moderate**, or **not significant**.
- Suggested trade **direction** (Bullish/Long or Bearish/Short).
- Current price and key indicator values (EMA, RSI, MACD).
- Suggested **profit targets** and **stop loss** levels for risk management.

---

## Summary: Why the Bot’s Signals Are Reliable

- **Uses well-established technical indicators** (EMA, RSI, MACD, Fibonacci retracements) widely trusted in financial analysis.
- **Confirms signals across multiple timeframes**, reducing false positives and improving trade timing.
- Combines momentum, trend, and price-level analysis to give a **holistic view**.
- Provides a **confidence score** to help prioritize signals.

---

This structured approach helps the bot generate actionable trading signals based on solid financial analysis principles, tailored for various market conditions.

---

## 🛠️ Setup & Installation

### Requirements

- Python 3.8+
- Binance API Key
- Discord Bot Token
- `.env` file with the following:

```env
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
DISCORD_TOKEN=your_discord_bot_token
CANAL_ID=your_discord_channel_id
````

### Install Dependencies

```bash
pip install -r requirements.txt
```

Create a `requirements.txt` file containing:

```
discord.py
python-dotenv
requests
pandas
binance
```

### Run the Bot

```bash
python bot.py
```

The bot logs information to both the console and a `bot.log` file.

---

## 📊 Strategy Breakdown

### Reversal Strategy

* Checks if the current price is below both:

  * The **0.618 Fibonacci retracement** level from recent high/low.
  * The **21-period EMA**.
* If both are true, a possible **reversal SHORT** opportunity is flagged.

### Continuation Strategy

* Confirms upward movement if:

  * The last close is above both the previous close and the EMA.
* Used to identify **momentum-based short setups**.

---

## 💬 Manual Confirmation

Once a signal is posted to Discord:

* A message is sent asking for confirmation: `"ok"`
* If someone replies with `ok` within 30 seconds, it simulates a trade confirmation.

---

## 🧪 Customize & Expand

This bot is a **starting point** for your own custom crypto signal engine.

### 🔧 Suggested Modifications:

* Add **LONG signal detection**.
* Connect to a **real trading API** to execute orders automatically.
* Improve signal algorithms or add more indicators.
* Support other exchanges or data sources.
* Create a frontend dashboard or alerts via other platforms.

---

## 📝 Contribution

Feel free to fork, modify, and test the signals. Pull requests and suggestions are welcome!

---

## 📜 License

MIT License © 2025 Adam Vibe Code

