````markdown
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

MIT License © 2025 YourName

```

Just copy this entire block as-is to your `README.md`! Let me know if you want me to generate a `requirements.txt` or anything else.
```
