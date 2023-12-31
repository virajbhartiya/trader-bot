from kiteconnect import KiteConnect
import configparser
import time
import sqlite3
from datetime import datetime, timedelta

# Load API credentials from a configuration file
config = configparser.ConfigParser()
config.read('config.ini')  # Replace 'config.ini' with the path to your configuration file

api_key = config['Zerodha']['api_key']
api_secret = config['Zerodha']['api_secret']
access_token = config['Zerodha']['access_token']

# Initialize Kite API
kite = KiteConnect(api_key=api_key)

# Set access token
kite.set_access_token(access_token)

symbol = "GTNTEX"

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
    momentum = (history["close"] / history["close"].shift(period)) - 1
    return momentum.iloc[-1]


def placeBuyOrder(symbol, price, quantity):
    order_info = kite.place_order(
        tradingsymbol=symbol,
        exchange="BSE",  # Replace with the appropriate exchange
        transaction_type="BUY",
        quantity=quantity,
        order_type="MARKET",
        product="CNC",
    )
    print("BUY:", quantity, symbol, "at", str(price))
    saveTrade(symbol, 'BUY', quantity, price)


def placeSellOrder(symbol, price, quantity):
    order_info = kite.place_order(
        tradingsymbol=symbol,
        exchange="BSE",  # Replace with the appropriate exchange
        transaction_type="SELL",
        quantity=quantity,
        order_type="MARKET",
        product="CNC",
    )
    print("SELL:", quantity, symbol, "at", str(price))
    saveTrade(symbol, 'SELL', quantity, price)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def tradeRealtime(symbol, momentum_period, threshold, historical_days):
    owned_stocks = {}
    balance = 10319.100274085999
    end_date = datetime.now()
    start_date = end_date - timedelta(days=historical_days)

    while True:

        # Fetch historical data from Kite Connect API
        history = kite.historical_data(
            instrument_token="YOUR_INSTRUMENT_TOKEN",  # Replace with the actual instrument token
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d'),
            interval="minute",
        )

        latest_momentum = calculateMomentum(history, momentum_period)

        latest_data = history[-1]
        latest_price = latest_data["close"]
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
    historical_days = int(input("Enter the number of days for historical data: "))
    tradeRealtime(symbol, momentum_period=1, threshold=0.003, historical_days=historical_days)
except KeyboardInterrupt:
    # Close the database connection when the program is interrupted
    conn.close()
