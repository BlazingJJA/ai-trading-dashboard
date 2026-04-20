import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Trading Dashboard", layout="wide")
st.title("📈 AI Trading Dashboard")

# -----------------------------
# SIDEBAR SCANNER
# -----------------------------
st.sidebar.header("🔎 Market Scanner")

tickers_input = st.sidebar.text_input(
    "Enter multiple tickers (comma separated)",
    "AAPL,MSFT,TSLA,BTC-USD,ETH-USD"
)

period = st.sidebar.selectbox("Select Period", ["1y","2y","5y","10y"])

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

if st.sidebar.button("Run Scanner 🚀"):
    tickers = [t.strip() for t in tickers_input.split(",")]
    results = []

    for ticker in tickers:
        signal = get_signal(ticker)
        results.append([ticker, signal])

    df_results = pd.DataFrame(results, columns=["Ticker", "Signal"])
    st.subheader("📊 Market Signals")
    st.dataframe(df_results)

# -----------------------------
# SINGLE STOCK CHART
# -----------------------------
st.header("📉 Single Asset Analysis")

ticker = st.text_input("Enter Ticker for Chart", "AAPL")

if st.button("Run Chart Analysis"):
    df = yf.download(ticker, period=period, auto_adjust=True)

    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["SMA_200"] = df["Close"].rolling(200).mean()

    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(df["Close"], label="Price")
    ax.plot(df["SMA_50"], label="SMA 50")
    ax.plot(df["SMA_200"], label="SMA 200")
    ax.legend()
    ax.set_title(f"{ticker} Trading Chart")

    st.pyplot(fig)
