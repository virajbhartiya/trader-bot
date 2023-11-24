import yfinance as yf
import time
import sqlite3
from datetime import datetime

symbol = "GTNTEX.BO"

# Connect to SQLite database
conn = sqlite3.connect('trading_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        action TEXT,
        quantity INTEGER,
        price REAL,
        timestamp DATETIME
    )
''')
conn.commit()


def saveTrade(symbol, action, quantity, price):
    timestamp = datetime.now()
    cursor.execute('''
        INSERT INTO trades (symbol, action, quantity, price, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, action, quantity, price, timestamp))
    conn.commit()


def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum.iloc[-1]


def placeBuyOrder(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    saveTrade(symbol, 'BUY', quantity, price)


def placeSellOrder(symbol, price, quantity):
    print("SELL:", quantity, symbol, "at", str(price))
    saveTrade(symbol, 'SELL', quantity, price)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def simulateRealTimeTrading(symbol, momentum_period, threshold):
    owned_stocks = {}
    balance = 10319.100274085999
    while True:

        history = yf.download(symbol, period="2d", interval="1m")
        latest_momentum = calculateMomentum(history, momentum_period)

        latest_data = history.iloc[-1]
        latest_price = latest_data["Close"]
        print("Latest Price: ", latest_price, " | Latest Momentum: ", latest_momentum)

        if latest_momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                placeSellOrder(symbol, latest_price, owned_stocks[symbol])
                balance += latest_price * owned_stocks[symbol]
                owned_stocks[symbol] = 0

        elif latest_momentum < -threshold:
            quantity_traded = balance // latest_price
            if balance > latest_price * quantity_traded and quantity_traded > 0:
                owned_stocks[symbol] = quantity_traded
                placeBuyOrder(symbol, latest_price, quantity_traded)
                balance -= latest_price * quantity_traded

        print("Balance: ", balance, " | Owned Stocks", owned_stocks)
        print("================================")
        countdown(60)


try:
    simulateRealTimeTrading(symbol, momentum_period=1, threshold=0.003)
except KeyboardInterrupt:
    # Close the database connection when the program is interrupted
    conn.close()
