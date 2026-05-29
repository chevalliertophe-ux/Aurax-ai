from flask import Flask, jsonify, render_template
from pnl import get_pnl
from binance.client import Client
from config import API_KEY, API_SECRET
import time

app = Flask(__name__)
client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

INTERVAL = Client.KLINE_INTERVAL_1MINUTE


def get_prices(symbol):
    klines = client.get_klines(
        symbol=symbol,
        interval=INTERVAL,
        limit=50
    )
    return [float(k[4]) for k in klines]


def analyze(symbol):

    prices = get_prices(symbol)

    price = prices[-1]

    return {
        "symbol": symbol,
        "price": price,
    }


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/api")
def api():

    markets = []

    for s in SYMBOLS:
        markets.append(analyze(s))

    return jsonify({
        "bot": "AURAX PRO ONLINE",
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "markets": markets,
        "pnl": get_pnl()
    })


if __name__ == "__main__":
    print("🔥 DASHBOARD PRO STARTED")
    app.run(host="0.0.0.0", port=5000)
