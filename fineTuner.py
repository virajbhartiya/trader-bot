import argparse
import yfinance as yf
import matplotlib.pyplot as plt
import itertools
import numpy as np
import time
from tqdm import tqdm

def download_historical_data(symbol, period, interval):
    return yf.download(symbol, period=period, interval=interval)

def calculate_momentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum

def place_buy_order(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    # Add your logic to execute a buy order

def place_sell_order(symbol, price, quantity):
    print("SELL:", quantity, symbol, "at", str(price))
    # Add your logic to execute a sell order

def backtest(symbol, momentum_period, threshold, df, initial_capital):
    df["Momentum"] = calculate_momentum(df, momentum_period)
    balance = initial_capital
    orders_executed = 0
    owned_stocks = {}
    df["Action"] = None
    last_price = 0
    owned_stocks[symbol] = 0
    for index, row in df.iterrows():
        current_price = round(row["Close"], 2)
        momentum = row["Momentum"]
        last_price = current_price
        if momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                # place_sell_order(symbol, current_price, owned_stocks[symbol])
                balance += current_price * owned_stocks[symbol] - 15
                owned_stocks[symbol] = 0
                df.at[index, "Action"] = "SELL"
        elif momentum < -threshold:
            quantity_traded = int(balance // current_price)
            if balance > current_price * quantity_traded and quantity_traded > 0:
                # place_buy_order(symbol, current_price, quantity_traded)
                balance -= current_price * quantity_traded
                if symbol in owned_stocks:
                    owned_stocks[symbol] += quantity_traded
                else:
                    owned_stocks[symbol] = quantity_traded
                df.at[index, "Action"] = "BUY"
                orders_executed += 1
    balance += owned_stocks[symbol] * last_price
    return round(balance - initial_capital, 2)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Backtest stock trading strategy.')
    parser.add_argument('symbol', type=str, help='Stock symbol to backtest.')
    parser.add_argument('--initial-capital', type=float, default=1000, help='Initial capital for backtesting.')
    parser.add_argument('--period', type=str, default="1d", help='Historical data period (e.g., "1d", "1mo", "1y").')
    parser.add_argument('--interval', type=str, default="1m", help='Historical data interval (e.g., "1m", "1h", "1d").')
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    symbol = args.symbol

    momentum_period_range = [1]
    threshold_range = np.arange(0.1, 0.0009, -0.0001).round(4).tolist()

    start_time = time.time()

    best_profit = float('-inf')
    best_combination = None
    historical_data = download_historical_data(symbol, args.period, args.interval)

    iteration_count = 0
    progress_bar = tqdm(total=len(threshold_range) * len(momentum_period_range))
    for combination in itertools.product(momentum_period_range, threshold_range):
        momentum_period, threshold = combination
        profit = backtest(symbol, momentum_period, threshold, historical_data.copy(), args.initial_capital)
        iteration_count += 1
        progress_bar.update(1)
        if profit > best_profit:
            best_profit = profit
            best_combination = combination
    progress_bar.close()

    # Plot the performance of the best combination
    momentum_period, threshold = best_combination
    df = historical_data.copy()
    df["Momentum"] = calculate_momentum(df, momentum_period)
    backtest(symbol, momentum_period, threshold, df, args.initial_capital)

    elapsed_time = time.time() - start_time

    print("======================================")
    print(f"Symbol: {symbol}")
    print(f"Combinations Tested: {len(threshold_range) * len(momentum_period_range)}")
    print(f"Best Combination: {best_combination}")
    print(f"Initial Investment: {args.initial_capital}")
    print(f"Calculation Period: {args.period}")
    print(f"Calculation Interval: {args.interval}")
    print(f"Best Profit: {best_profit}")
    print(f"Profit Percentage: {round((best_profit) * 100 / args.initial_capital, 2)}%")
    print(f"Elapsed Time: {round(elapsed_time, 2)} seconds")
    print("======================================")

if __name__ == "__main__":
    main()
