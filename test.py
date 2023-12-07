import argparse
import yfinance as yf
import time
import sqlite3
import requests
from datetime import datetime

URL = "https://script.google.com/macros/s/AKfycbytwAIEyFIjHaQlMQTZc3H6jhJ0GBsGBid-jGLPQKCUJwWysPiXyC66U3CvYvQKO05stQ/exec"


def adapt_datetime(ts):
    return ts.isoformat()

def create_database(symbol):
    conn = sqlite3.connect(f'{symbol}_trading_data.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Register the custom adapter for datetime
    sqlite3.register_adapter(datetime, adapt_datetime)

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
    return conn, cursor


def save_trade(symbol, action, quantity, price, cursor):
    timestamp = datetime.now()
    cursor.execute('''
        INSERT INTO trades (symbol, action, quantity, price, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, action, quantity, price, timestamp))
    conn.commit()


def send_email(symbol, action, quantity, rate, balance):
    response = requests.get(URL + f"?stock={symbol}&action={action}&quantity={quantity}&rate={rate}&balance={balance}")
    print(response)


def calculate_momentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum.iloc[-1]


def place_buy_order(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    save_trade(symbol, 'BUY', quantity, price, cursor)
    # Add your logic to execute a buy order


def place_sell_order(symbol, price, quantity, ):
    print("SELL:", quantity, symbol, "at", str(price))
    save_trade(symbol, 'SELL', quantity, price, cursor)
    # Add your logic to execute a sell order


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def simulate_real_time_trading(symbol, momentum_period, threshold, initial_capital, cursor):
    owned_stocks = {}
    balance = initial_capital
    while True:
        history = yf.download(symbol, period="2d", interval="1m")
        latest_momentum = calculate_momentum(history, momentum_period)

        latest_data = history.iloc[-1]
        latest_price = round(latest_data["Close"], 2)
        print("Latest Price: ", latest_price, " | Latest Momentum: ", latest_momentum)
        

        if latest_momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                place_sell_order(symbol, latest_price, owned_stocks[symbol])
                balance += round(latest_price * owned_stocks[symbol], 2)
                send_email(symbol, "SELL", owned_stocks[symbol], latest_price, balance)
                owned_stocks[symbol] = 0

        elif latest_momentum < -threshold:
            quantity_traded = int(balance // latest_price)
            if balance > latest_price * quantity_traded and quantity_traded > 0:
                owned_stocks[symbol] = quantity_traded
                place_buy_order(symbol, latest_price, quantity_traded)
                balance -= round(latest_price * quantity_traded, 2)
                send_email(symbol, "BUY", owned_stocks[symbol], latest_price, balance)

        

        print("Balance: ", balance, " | Owned Stocks", owned_stocks)
        print("================================")
        countdown(60)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Real-time stock trading simulation.')
    parser.add_argument('--symbol', type=str,default="GTNTEX.BO", help='Stock symbol to simulate trading for.')
    parser.add_argument('--threshold', type=float, default=0.0125, help='Momentum threshold for trading.')
    parser.add_argument('--initial-capital', type=float, default=1000, help='Initial capital for trading.')
    args = parser.parse_args()
    return args.symbol, args.threshold, args.initial_capital


if __name__ == "__main__":
    # symbol, threshold, initial_capital = parse_arguments()
    symbol = "SACHEMT.BO"
    threshold = 0.019
    initial_capital = 1000
    conn, cursor = create_database(symbol)
    try:
        simulate_real_time_trading(symbol, momentum_period=1, threshold=threshold, initial_capital=initial_capital,cursor=cursor)
    except KeyboardInterrupt:
        # Close the database connection when the program is interrupted
        conn.close()
        print('Exiting')

# python realtimeEmail.py GTNTEX.BO --threshold 0.0165
# python realtimeEmail.py SACHEMT.BO --threshold 0.019