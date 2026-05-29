from flask import Flask, render_template, jsonify
from binance.client import Client
from config import API_KEY, API_SECRET
import time

app = Flask(__name__)
client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1MINUTE

# ================= STATE =================

position = 0

# ================= DATA =================

def get_prices(limit=50):

    klines = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=limit
    )

    return [float(k[4]) for k in klines]

# ================= INDICATORS =================

def ema(values, period):

    k = 2 / (period + 1)
    ema_val = sum(values[:period]) / period

    for v in values[period:]:
        ema_val = v * k + ema_val * (1 - k)

    return ema_val


def rsi(values, period=14):

    gains = 0
    losses = 0

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]

        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    gains /= period
    losses /= period

    if losses == 0:
        return 100

    rs = gains / losses

    return 100 - (100 / (1 + rs))

# ================= SIGNAL =================

def get_signal(prices):

    r = rsi(prices)
    e9 = ema(prices, 9)
    e21 = ema(prices, 21)

    if r < 30 and e9 > e21:
        return "BUY", r, e9, e21

    if r > 70 and e9 < e21:
        return "SELL", r, e9, e21

    return "HOLD", r, e9, e21

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/status")
def status():

    prices = get_prices()
    price = prices[-1]

    sig, r, e9, e21 = get_signal(prices)

    return jsonify({
        "price": price,
        "signal": sig,
        "rsi": round(r, 2),
        "ema9": round(e9, 2),
        "ema21": round(e21, 2),
        "position": position,
        "bot": "ONLINE"
    })

# ================= START =================

if __name__ == "__main__":
    print("🔥 AURAX DASHBOARD BOT STARTED 🔥")
    app.run(host="0.0.0.0", port=5000)
