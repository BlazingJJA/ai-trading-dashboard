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
# AI PRICE PREDICTION TAB
# =============================
with tab5:
    # =============================
# AI PRICE PREDICTION TAB (UPGRADED)
# =============================
with tab5:
    st.header("🤖 AI Stock Price Forecast")

    ticker = st.text_input("Enter Stock Ticker", "AAPL")
    forecast_days = st.slider("Days to Predict", 5, 30, 7)

    if st.button("Run AI Forecast"):
        import numpy as np
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.linear_model import LinearRegression

        df = yf.download(ticker, period="3y", auto_adjust=True)

        # Use only closing price
        data = df[["Close"]].copy()

        # Scale data
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(data)

        # Create sequences
        X = []
        y = []
        window = 60

        for i in range(window, len(scaled)):
            X.append(scaled[i-window:i])
            y.append(scaled[i])

        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], -1)

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Predict future prices
        last_window = scaled[-window:]
        preds = []

        current_window = last_window.copy()

        for _ in range(forecast_days):
            pred = model.predict(current_window.reshape(1, -1))
            preds.append(pred[0][0])
            current_window = np.append(current_window[1:], pred, axis=0)

        # Inverse scale predictions
        forecast = scaler.inverse_transform(np.array(preds).reshape(-1,1))

        # Create future dates
        future_dates = pd.date_range(df.index[-1], periods=forecast_days+1)[1:]

        # Plot
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(df.index[-200:], df["Close"].tail(200), label="Historical")
        ax.plot(future_dates, forecast, label="Forecast")
        ax.fill_between(future_dates,
                        forecast.flatten()*0.95,
                        forecast.flatten()*1.05,
                        alpha=0.2)

        ax.legend()
        st.pyplot(fig)

        st.subheader("Forecast Values")
        st.write(pd.DataFrame({"Date": future_dates, "Predicted Price": forecast.flatten()}))
