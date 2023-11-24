import yfinance as yf
import matplotlib.pyplot as plt

symbol = "SITINET.BO"


def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum


def placeBuyOrder(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    # Add your logic to execute a buy order


def placeSellOrder(symbol, price, quantity):
    print("SELL:", quantity,  symbol, "at", str(price))
    # Add your logic to execute a sell order


def backtest(symbol, momentum_period, threshold):
    df = yf.download(symbol, period="1mo", interval="15m")
    df["Momentum"] = calculateMomentum(df, momentum_period)
    balance = 5000
    owned_stocks = {}
    df["Action"] = None
    bought_today = False  # Track if stock was bought today

    for index, row in df.iterrows():
        current_price = row["Close"]
        momentum = row["Momentum"]

        if bought_today:
            bought_today = False  # Reset the flag for the next iteration
            continue  # Skip this iteration to enforce the one-day delay

        if momentum > threshold:
            if symbol in owned_stocks:
                placeSellOrder(symbol, current_price, owned_stocks[symbol])
                balance += current_price * owned_stocks[symbol]
                del owned_stocks[symbol]
                df.at[index, "Action"] = "SELL"
        elif momentum < -threshold:
            if symbol not in owned_stocks:
                quantity_traded = balance // current_price
                placeBuyOrder(symbol, current_price, quantity_traded)
                balance -= current_price * quantity_traded
                if symbol in owned_stocks:
                    owned_stocks[symbol] += quantity_traded
                else:
                    owned_stocks[symbol] = quantity_traded
                df.at[index, "Action"] = "BUY"
                bought_today = True  # Set the flag to indicate that stock was bought today

    print(balance)
    plotStockPerformance(df, balance)


def plotStockPerformance(df, balance):
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

    # Plot profit/loss
    if balance != 0:
        plt.annotate(
            f"Profit/Loss: {balance:.2f}",
            (df.index[-1], df["Close"].iloc[-1]),
            xytext=(df.index[-1], df["Close"].iloc[-1] + 100),
            arrowprops=dict(facecolor="black", arrowstyle="->"),
        )

    plt.show()


backtest(symbol, momentum_period=1, threshold=0.001)
