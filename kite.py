import yfinance as yf
from kiteconnect import KiteConnect
import sqlite3
import time
from datetime import datetime

symbol = "GENTEX.BO"

# Replace these values with your actual API key and secret
api_key = 'your_api_key'
api_secret = 'your_api_secret'
access_token = 'your_access_token'

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# SQLite database setup
conn = sqlite3.connect('trades.db')
cursor = conn.cursor()

# Create a table for storing trades if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        order_type TEXT,
        quantity INTEGER,
        price REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()


def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum.iloc[-1]


def placeBuyOrder(symbol, price, quantity):
    order_id = kite.place_order(
        variety="regular",
        exchange="NSE",
        tradingsymbol=symbol,
        transaction_type="BUY",
        quantity=quantity,
        order_type="MARKET",
        product="MIS"
    )
    print("BUY:", quantity, symbol, "at", str(price), "| Order ID:", order_id)

    # Store the order in the database
    cursor.execute('''
        INSERT INTO trades (symbol, order_type, quantity, price)
        VALUES (?, ?, ?, ?)
    ''', (symbol, 'BUY', quantity, price))
    conn.commit()


def placeSellOrder(symbol, price, quantity):
    order_id = kite.place_order(
        variety="regular",
        exchange="NSE",
        tradingsymbol=symbol,
        transaction_type="SELL",
        quantity=quantity,
        order_type="MARKET",
        product="MIS"
    )
    print("SELL:", quantity, symbol, "at", str(price), "| Order ID:", order_id)

    # Store the order in the database
    cursor.execute('''
        INSERT INTO trades (symbol, order_type, quantity, price)
        VALUES (?, ?, ?, ?)
    ''', (symbol, 'SELL', quantity, price))
    conn.commit()


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def is_market_open():
    now = datetime.now().time()
    market_open = datetime.strptime("09:30", "%H:%M").time()
    market_close = datetime.strptime("15:00", "%H:%M").time()
    return market_open <= now <= market_close


def simulateRealTimeTrading(symbol, momentum_period, threshold):
    owned_stocks = {}
    balance = 10000
    while True:
        if is_market_open():
            history = yf.download(symbol, period="5d", interval="1m")
            latest_momentum = calculateMomentum(history, momentum_period)

            latest_data = history.iloc[-1]
            latest_price = latest_data["Close"]

            if latest_momentum > threshold:
                placeSellOrder(symbol, latest_price, owned_stocks[symbol])
                balance += latest_price * owned_stocks[symbol]
                del owned_stocks[symbol]
            elif latest_momentum < -threshold:
                if symbol not in owned_stocks and balance >= balance // latest_price:
                    quantity_traded = balance // latest_price
                    owned_stocks[symbol] = quantity_traded
                    placeBuyOrder(symbol, latest_price, quantity_traded)
                    balance -= latest_price * quantity_traded

            print("Balance: ", balance, " | Owned Stocks", owned_stocks)
        countdown(60)


simulateRealTimeTrading(symbol, momentum_period=1, threshold=0.001)

# Close the database connection when done
conn.close()
