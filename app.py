import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Trading Dashboard", layout="wide")
st.title("📈 AI Trading Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔎 Scanner",
    "📉 Chart",
    "💼 Portfolio",
    "📊 Backtest",
    "🤖 AI Prediction"
])

# =============================
# TAB 1 — MARKET SCANNER
# =============================
with tab1:
    st.header("Market Scanner")

    tickers_input = st.text_input("Tickers", "AAPL,MSFT,TSLA,BTC-USD,ETH-USD")
    period = st.selectbox("Period", ["1y","2y","5y","10y"])

    def get_signal(ticker):
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        if df["SMA_50"].iloc[-1] > df["SMA_200"].iloc[-1]:
            return "BUY 🟢"
        elif df["SMA_50"].iloc[-1] < df["SMA_200"].iloc[-1]:
            return "SELL 🔴"
        else:
            return "NEUTRAL"

    if st.button("Run Scanner"):
        tickers = [t.strip() for t in tickers_input.split(",")]
        results = [[t, get_signal(t)] for t in tickers]
        st.dataframe(pd.DataFrame(results, columns=["Ticker","Signal"]))

# =============================
# TAB 2 — CHART
# =============================
with tab2:
    ticker = st.text_input("Ticker for Chart", "AAPL")
    if st.button("Run Chart"):
        df = yf.download(ticker, period="5y", auto_adjust=True)
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(df["Close"], label="Price")
        ax.plot(df["SMA_50"], label="SMA50")
        ax.plot(df["SMA_200"], label="SMA200")
        ax.legend()
        st.pyplot(fig)

# =============================
# TAB 3 — PORTFOLIO
# =============================
with tab3:
    st.header("Portfolio Tracker")

    portfolio_input = st.text_area("Ticker, Shares per line", "AAPL,10\nMSFT,5\nBTC-USD,0.2")

    if st.button("Calculate Portfolio"):
        lines = portfolio_input.split("\n")
        data = []
        total = 0

        for line in lines:
            ticker, shares = line.split(",")
            shares = float(shares)

            price = yf.download(ticker.strip(), period="1d", auto_adjust=True)["Close"].iloc[-1]
            value = price * shares
            total += value

            data.append([ticker, shares, price, value])

        dfp = pd.DataFrame(data, columns=["Ticker","Shares","Price","Value"])
        st.dataframe(dfp)
        st.metric("Total Value", f"${total:,.2f}")

# =============================
# TAB 4 — BACKTEST ENGINE
# =============================
with tab4:
    st.header("Strategy Backtest")

    ticker = st.text_input("Ticker", "AAPL")
    start_capital = st.number_input("Starting Capital", 1000)

    if st.button("Run Backtest"):

        df = yf.download(ticker, period="5y", auto_adjust=True)

        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        df["Position"] = 0
        df.loc[df["SMA_50"] > df["SMA_200"], "Position"] = 1

        df["Market Return"] = df["Close"].pct_change()
        df["Strategy Return"] = df["Market Return"] * df["Position"].shift(1)

        df["Equity"] = (1 + df["Strategy Return"]).cumprod() * start_capital

        final_value = df["Equity"].iloc[-1]
        profit = final_value - start_capital

        st.metric("Final Portfolio Value", f"${final_value:,.2f}")
        st.metric("Total Profit", f"${profit:,.2f}")

        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(df["Equity"], label="Strategy Equity")
        ax.legend()
        st.pyplot(fig)
# =============================
# AI PRICE PREDICTION (ML MODEL)
# =============================
with tab5:
    st.header("🤖 AI Price Prediction")

    ticker_ai = st.text_input("Enter Stock / Crypto / Forex ticker", "AAPL")

    if st.button("Run AI Prediction"):

        import numpy as np
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.model_selection import train_test_split

        df = yf.download(ticker_ai, period="5y", auto_adjust=True)

        # Feature engineering
        df["Return"] = df["Close"].pct_change()
        df["SMA_10"] = df["Close"].rolling(10).mean()
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["Volatility"] = df["Return"].rolling(10).std()
        df.dropna(inplace=True)

        # Predict tomorrow's close
        df["Target"] = df["Close"].shift(-1)
        df.dropna(inplace=True)

        features = ["Close","SMA_10","SMA_50","Volatility"]
        X = df[features]
        y = df["Target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, shuffle=False, test_size=0.2
        )

        model = GradientBoostingRegressor()
        model.fit(X_train, y_train)

        last_row = X.iloc[-1:].values
        prediction = model.predict(last_row)[0]
        current_price = df["Close"].iloc[-1]

        change_pct = ((prediction - current_price) / current_price) * 100

        st.metric("Current Price", f"${current_price:.2f}")
        st.metric("Predicted Next Close", f"${prediction:.2f}")
        st.metric("Predicted Change", f"{change_pct:.2f}%")
        