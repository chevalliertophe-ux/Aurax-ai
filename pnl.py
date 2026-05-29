balance = 10
trades = []

open_position = None


def add_trade(type_trade, price, qty):

    global balance, open_position

    trade = {
        "type": type_trade,
        "price": price,
        "qty": qty
    }

    trades.append(trade)

    # 🟢 BUY
    if type_trade == "BUY":
        open_position = {
            "entry": price,
            "qty": qty
        }
        balance -= price * qty

    # 🔴 SELL
    elif type_trade == "SELL" and open_position:

        profit = (price - open_position["entry"]) * qty
        balance += price * qty + profit

        open_position = None


def get_pnl():

    total_trades = len(trades)

    last_trade = trades[-1] if trades else None

    return {
        "balance": round(balance, 2),
        "trades": total_trades,
        "last_trade": last_trade,
        "position": open_position
    }
