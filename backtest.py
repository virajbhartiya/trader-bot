import yfinance as yf
import matplotlib.pyplot as plt

SYMBOL = "GTNTEX.BO"
INITIAL_BALANCE = 2000

PERIOD = "2d"
INTERVAL = "1m"

MOMENTUM_PERIOD = 1
THRESHOLD = 0.0125


# SYMBOL = "GTNTEX.BO"
# MOMENTUM_PERIOD = 1
# THRESHOLD = 0.003


# MOMENTUM_PERIOD = 1
# THRESHOLD = 0.0096
# SYMBOL = "JINDHOT.BO"


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
    df = yf.download(symbol, period=PERIOD, interval=INTERVAL)
    df["Momentum"] = calculateMomentum(df, momentum_period)
    balance = INITIAL_BALANCE
    ordersExecuted = 0
    owned_stocks = {}
    owned_stocks[SYMBOL] = 0
    df["Action"] = None
    lastPrice = 0
    for index, row in df.iterrows():
        current_price = round(row["Close"],2)
        momentum = row["Momentum"]
        lastPrice = current_price
        if momentum > threshold:
            if symbol in owned_stocks and owned_stocks[symbol] > 0:
                placeSellOrder(symbol, current_price,owned_stocks[symbol])
                balance += current_price * owned_stocks[symbol] - 15
                owned_stocks[symbol] = 0
                df.at[index, "Action"] = "SELL"

        elif momentum < -threshold:
            quantity_traded = int(balance//current_price)
            if balance > current_price * quantity_traded and quantity_traded>0: 
                placeBuyOrder(symbol, current_price, quantity_traded)
                balance -= current_price * quantity_traded
                if symbol in owned_stocks:
                    owned_stocks[symbol] += quantity_traded
                else:
                    owned_stocks[symbol] = quantity_traded
                df.at[index, "Action"] = "BUY"
                ordersExecuted +=1
    
    balance += owned_stocks[symbol] * lastPrice
    print("========================================")
    print("Final balance: ",round(balance,2))
    print("Profit/Loss: ", round(balance-INITIAL_BALANCE,2))
    print(f"Profit/Loss Percentage: {round(((balance-INITIAL_BALANCE)/INITIAL_BALANCE)*100,2)}%")
    print("Total Orders Executed: ", ordersExecuted)
    print("========================================")
    # plotStockPerformance(df, balance)


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

    # # Plot profit/loss
    # if balance != 0:
    #     plt.annotate(
    #         f"Profit/Loss: {balance:.2f}",
    #         (df.index[-1], df["Close"].iloc[-1]),
    #         xytext=(df.index[-1], df["Close"].iloc[-1] + 100),
    #         arrowprops=dict(facecolor="black", arrowstyle="->"),
    #     )

    plt.show()


backtest(SYMBOL, momentum_period=MOMENTUM_PERIOD, threshold=THRESHOLD)