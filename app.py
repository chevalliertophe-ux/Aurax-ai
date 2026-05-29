from flask import Flask, jsonify, request, render_template, session, redirect
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = "aurax_pro_secret_key"

DB = "users.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        plan TEXT
    )
    """)

    # compte demo
    c.execute("INSERT OR IGNORE INTO users (username, password, plan) VALUES (?, ?, ?)",
              ("demo", "demo", "free"))

    conn.commit()
    conn.close()

init_db()

# ================= MARKET =================
prices = {
    "BTC": 73000,
    "ETH": 3800,
    "SOL": 170,
    "BNB": 620,
    "XRP": 0.52,
    "ADA": 0.61,
    "DOGE": 0.18,
    "AVAX": 42,
    "DOT": 8.5,
    "LINK": 18
}

# ================= AI ENGINE =================
def ai_engine():
    signals = {}
    buy = 0
    sell = 0

    for coin in prices:
        move = random.uniform(-3, 3)
        prices[coin] += move

        if move > 1:
            signal = "BUY"
            buy += 1
        elif move < -1:
            signal = "SELL"
            sell += 1
        else:
            signal = "HOLD"

        signals[coin] = {
            "signal": signal,
            "price": round(prices[coin], 4)
        }

    market = "NEUTRAL"
    if buy > sell:
        market = "BULLISH"
    elif sell > buy:
        market = "BEARISH"

    return {
        "coins": signals,
        "market": market,
        "ai_score": random.randint(70, 98)
    }

# ================= DB =================
def get_user(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT username, password, plan FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, plan) VALUES (?, ?, ?)",
                  (username, password, "free"))
        conn.commit()
    except:
        pass
    conn.close()

# ================= ROUTES =================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    create_user(data["username"], data["password"])
    return jsonify({"status": "ok"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = get_user(data["username"])

    if user and user[1] == data["password"]:
        session["user"] = user[0]
        session["plan"] = user[2]

        return jsonify({
            "status": "ok",
            "user": user[0],
            "plan": user[2]
        })

    return jsonify({"status": "error"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def home():
    if "user" not in session:
        return render_template("login.html")

    return render_template("index.html",
                           user=session["user"],
                           plan=session["plan"])

@app.route("/signals")
def signals():
    if "user" not in session:
        return jsonify({"error": "not logged in"})
    return jsonify(ai_engine())

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return jsonify({"error": "not logged in"})

    return jsonify({
        "user": session["user"],
        "plan": session["plan"],
        "data": ai_engine()
    })

# ================= RUN (PRO / DEPLOY READY) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
