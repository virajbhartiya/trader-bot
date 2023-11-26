import yfinance as yf
import matplotlib.pyplot as plt
import itertools
import numpy as np
import time
from tqdm import tqdm

SYMBOL = "GTNTEX.BO"
INITIAL_BALANCE = 2000

PERIOD = "2d"
INTERVAL = "1m"

momentum_period_range = [1]
threshold_range = np.arange(0.1, 0.0009, -0.0001).round(4).tolist()

def downloadHistoricalData(symbol):
    return yf.download(symbol, period=PERIOD, interval=INTERVAL)

def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum

def placeBuyOrder(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    # Add your logic to execute a buy order

def placeSellOrder(symbol, price, quantity):
    print("SELL:", quantity,  symbol, "at", str(price))
    # Add your logic to execute a sell order

def backtest(symbol, momentum_period, threshold, df):
    df["Momentum"] = calculateMomentum(df, momentum_period)
    balance = INITIAL_BALANCE
    ordersExecuted = 0
    owned_stocks = {}
    df["Action"] = None
    lastPrice = 0
    owned_stocks[symbol] = 0
    for index, row in df.iterrows():
        current_price = round(row["Close"], 2)
        momentum = row["Momentum"]
        lastPrice = current_price
        if momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                # placeSellOrder(symbol, current_price, owned_stocks[symbol])
                balance += current_price * owned_stocks[symbol] - 15
                owned_stocks[symbol] = 0
                df.at[index, "Action"] = "SELL"
        elif momentum < -threshold:
            quantity_traded = int(balance // current_price)
            if balance > current_price * quantity_traded and quantity_traded > 0:
                # placeBuyOrder(symbol, current_price, quantity_traded)
                balance -= current_price * quantity_traded
                if symbol in owned_stocks:
                    owned_stocks[symbol] += quantity_traded
                else:
                    owned_stocks[symbol] = quantity_traded
                df.at[index, "Action"] = "BUY"
                ordersExecuted += 1
    balance += owned_stocks[symbol] * lastPrice
    return round(balance-INITIAL_BALANCE, 2)

start_time = time.time()

best_profit = float('-inf')
best_combination = None
historical_data = downloadHistoricalData(SYMBOL)

iterationCount = 0
progress_bar = tqdm(total=len(threshold_range) * len(momentum_period_range))
for combination in itertools.product(momentum_period_range, threshold_range):
    momentum_period, threshold = combination
    profit = backtest(SYMBOL, momentum_period, threshold, historical_data.copy())
    iterationCount +=1
    progress_bar.update(1)
    if profit > best_profit:
        best_profit = profit
        best_combination = combination
progress_bar.close()

# Plot the performance of the best combination
momentum_period, threshold = best_combination
df = historical_data.copy()
df["Momentum"] = calculateMomentum(df, momentum_period)
backtest(SYMBOL, momentum_period, threshold, df)

elapsed_time = time.time() - start_time

print("======================================")
print(f"Symbol: {SYMBOL}")
print(f"Combinations Tested: {len(threshold_range) * len(momentum_period_range)}")
print(f"Best Combination: {best_combination}")
print(f"Inital Investment: {INITIAL_BALANCE}")
print(f"Calculation Period: {PERIOD}")
print(f"Best Profit: {best_profit}")
print(f"Profit Percentage: {round((best_profit)*100/INITIAL_BALANCE,2)}%")
print(f"Elapsed Time: {round(elapsed_time, 2)} seconds")
print("======================================")
