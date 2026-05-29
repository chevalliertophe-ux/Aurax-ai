from binance.client import Client
from config import API_KEY, API_SECRET
from pnl import add_trade
import time

client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

USDT_CAPITAL = 10

STOP_LOSS = 0.98
TAKE_PROFIT = 1.03
COOLDOWN = 60

position = None
entry_price = 0
last_trade = 0


# ================= PRICE =================

def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])


def get_prices(symbol):

    klines = client.get_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        limit=50
    )

    return [float(k[4]) for k in klines]


# ================= IA LIGHT SIGNAL =================

def ai_signal(prices):

    if len(prices) < 20:
        return "HOLD"

    short = sum(prices[-5:]) / 5
    mid = sum(prices[-10:]) / 10
    long = sum(prices[-20:]) / 20

    momentum = prices[-1] - prices[-2]

    if short > mid > long and momentum > 0:
        return "BUY"

    if short < mid < long and momentum < 0:
        return "SELL"

    return "HOLD"


# ================= BUY =================

def place_buy(symbol, qty, price):

    global position, entry_price, last_trade

    try:
        order = client.order_market_buy(
            symbol=symbol,
            quantity=qty
        )

        print("🟢 BUY:", symbol)

        add_trade("BUY", price, qty)

        position = symbol
        entry_price = price
        last_trade = time.time()

        return order

    except Exception as e:
        print("BUY ERROR:", e)
        return None


# ================= SELL =================

def place_sell(symbol, qty, price):

    global position, entry_price, last_trade

    try:
        order = client.order_market_sell(
            symbol=symbol,
            quantity=qty
        )

        print("🔴 SELL:", symbol)

        add_trade("SELL", price, qty)

        position = None
        entry_price = 0
        last_trade = time.time()

        return order

    except Exception as e:
        print("SELL ERROR:", e)
        return None


# ================= LOOP =================

def run():

    global position

    print("🔥 AURAX BOT RESET STARTED")

    while True:

        for symbol in SYMBOLS:

            price = get_price(symbol)
            prices = get_prices(symbol)

            qty = round(USDT_CAPITAL / price, 6)

            sig = ai_signal(prices)

            # 🟢 BUY
            if position is None and sig == "BUY":
                place_buy(symbol, qty, price)

            # 🔴 SELL
            elif position == symbol and sig == "SELL":
                place_sell(symbol, qty, price)

        time.sleep(10)


run()
