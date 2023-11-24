import yfinance as yf
import time

symbol = "GTNTEX.BO"


def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum.iloc[-1]


def placeBuyOrder(symbol, price, quantity):
    print("BUY:", quantity, symbol, "at", str(price))
    # Add your logic to execute a buy order


def placeSellOrder(symbol, price, quantity):
    print("SELL:", quantity, symbol, "at", str(price))
    # Add your logic to execute a sell order
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def simulateRealTimeTrading(symbol, momentum_period, threshold):
    owned_stocks={}
    balance = 10000
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
            quantity_traded = balance//latest_price
            if balance > latest_price * quantity_traded and quantity_traded>0: 
                owned_stocks[symbol] = quantity_traded
                placeBuyOrder(symbol, latest_price, quantity_traded)
                balance -= latest_price * quantity_traded
            

        print("Balance: ", balance, " | Owned Stocks", owned_stocks )
        print("================================")
        countdown(60)


simulateRealTimeTrading(symbol, momentum_period=1, threshold=0.003)
