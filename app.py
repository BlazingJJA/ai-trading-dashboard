import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Trading Dashboard", layout="wide")
st.title("📈 AI Trading Dashboard")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🔎 Market Scanner", "📉 Chart", "💼 Portfolio"])

# =============================
# TAB 1 — MARKET SCANNER
# =============================
with tab1:
    st.header("Market Scanner")

    tickers_input = st.text_input(
        "Enter tickers (comma separated)",
        "AAPL,MSFT,TSLA,BTC-USD,ETH-USD"
    )

    period = st.selectbox("Select Period", ["1y","2y","5y","10y"])

    def get_signal(ticker):
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty:
            return "No Data"

        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        if df["SMA_50"].iloc[-1] > df["SMA_200"].iloc[-1]:
            return "BUY 🟢"
        elif df["SMA_50"].iloc[-1] < df["SMA_200"].iloc[-1]:
            return "SELL 🔴"
        else:
            return "NEUTRAL"

    if st.button("Run Scanner 🚀"):
        tickers = [t.strip() for t in tickers_input.split(",")]
        results = []

        for ticker in tickers:
            results.append([ticker, get_signal(ticker)])

        df_results = pd.DataFrame(results, columns=["Ticker", "Signal"])
        st.dataframe(df_results)

# =============================
# TAB 2 — SINGLE CHART
# =============================
with tab2:
    st.header("Single Asset Chart")

    ticker = st.text_input("Enter Ticker", "AAPL")

    if st.button("Run Chart"):
        df = yf.download(ticker, period="5y", auto_adjust=True)

        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(df["Close"], label="Price")
        ax.plot(df["SMA_50"], label="SMA 50")
        ax.plot(df["SMA_200"], label="SMA 200")
        ax.legend()
        st.pyplot(fig)

# =============================
# TAB 3 — PORTFOLIO TRACKER
# =============================
with tab3:
    st.header("💼 Portfolio Tracker")

    portfolio_input = st.text_area(
        "Enter holdings (Ticker, Shares per line)",
        "AAPL,10\nMSFT,5\nBTC-USD,0.2"
    )

    if st.button("Calculate Portfolio"):
        lines = portfolio_input.split("\n")

        portfolio_data = []
        total_value = 0

        for line in lines:
            ticker, shares = line.split(",")
            shares = float(shares)

            df = yf.download(ticker.strip(), period="1d", auto_adjust=True, progress=False)
            price = df["Close"].iloc[-1]

            value = price * shares
            total_value += value

            portfolio_data.append([ticker, shares, price, value])

        df_portfolio = pd.DataFrame(
            portfolio_data,
            columns=["Ticker","Shares","Price","Value"]
        )

        st.subheader("Portfolio Breakdown")
        st.dataframe(df_portfolio)

        st.metric("Total Portfolio Value", f"${total_value:,.2f}")

        # Pie chart allocation
        fig, ax = plt.subplots()
        ax.pie(df_portfolio["Value"], labels=df_portfolio["Ticker"], autopct="%1.1f%%")
        st.pyplot(fig)
