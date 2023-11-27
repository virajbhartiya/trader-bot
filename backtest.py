import argparse
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_momentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum

def place_buy_order(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    # Add your logic to execute a buy order

def place_sell_order(symbol, price, quantity):
    print("SELL:", quantity, symbol, "at", str(price))
    # Add your logic to execute a sell order

def backtest(symbol, momentum_period, threshold, initial_balance, period, interval):
    df = yf.download(symbol, period=period, interval=interval)
    df["Momentum"] = calculate_momentum(df, momentum_period)
    balance = initial_balance
    orders_executed = 0
    owned_stocks = {}
    owned_stocks[symbol] = 0
    df["Action"] = None
    last_price = 0
    for index, row in df.iterrows():
        current_price = round(row["Close"], 2)
        momentum = row["Momentum"]
        last_price = current_price
        if momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                place_sell_order(symbol, current_price, owned_stocks[symbol])
                balance += current_price * owned_stocks[symbol] - 15
                owned_stocks[symbol] = 0
                df.at[index, "Action"] = "SELL"
        elif momentum < -threshold:
            quantity_traded = int(balance // current_price)
            if balance > current_price * quantity_traded and quantity_traded > 0:
                place_buy_order(symbol, current_price, quantity_traded)
                balance -= current_price * quantity_traded
                if symbol in owned_stocks:
                    owned_stocks[symbol] += quantity_traded
                else:
                    owned_stocks[symbol] = quantity_traded
                df.at[index, "Action"] = "BUY"
                orders_executed += 1
    
    balance += owned_stocks[symbol] * last_price
    print("========================================")
    print("Final balance: ", round(balance, 2))
    print("Profit/Loss: ", round(balance - initial_balance, 2))
    print(f"Profit/Loss Percentage: {round(((balance - initial_balance) / initial_balance) * 100, 2)}%")
    print("Total Orders Executed: ", orders_executed)
    print("========================================")
    # plot_stock_performance(df)

def plot_stock_performance(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["Close"], label="Stock Price")
    plt.scatter(
        df[df["Action"] == "BUY"].index,
        df[df["Action"] == "BUY"]["Close"],
        color="green",
        label="Buy",
        marker="^",
        s=100,
    )
    plt.scatter(
        df[df["Action"] == "SELL"].index,
        df[df["Action"] == "SELL"]["Close"],
        color="red",
        label="Sell",
        marker="v",
        s=100,
    )
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title("Stock Performance")
    plt.legend()

    plt.show()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Backtest stock trading strategy.')
    parser.add_argument('symbol', type=str, help='Stock symbol to backtest.')
    parser.add_argument('--initial-balance', type=float, default=1000, help='Initial balance for backtesting.')
    parser.add_argument('--momentum-period', type=int, default=1, help='Momentum period for backtesting.')
    parser.add_argument('--threshold', type=float, default=0.0125, help='Momentum threshold for backtesting.')
    parser.add_argument('--period', type=str, default="2d", help='Historical data period (e.g., "1d", "1mo", "1y").')
    parser.add_argument('--interval', type=str, default="1m", help='Historical data interval (e.g., "1m", "1h", "1d").')
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    backtest(args.symbol, args.momentum_period, args.threshold, args.initial_balance, args.period, args.interval)

if __name__ == "__main__":
    main()
