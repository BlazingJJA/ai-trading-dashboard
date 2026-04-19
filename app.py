import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Trading Dashboard", layout="wide")

st.title("📈 AI Trading Dashboard")

col1, col2 = st.columns(2)
ticker = col1.text_input("Enter Stock Ticker", "AAPL")
period = col2.selectbox("Select Period", ["1y","2y","5y","10y"])

if st.button("Run Analysis 🚀"):

    with st.spinner("Downloading data..."):
        df = yf.download(ticker, period=period, auto_adjust=True)

    df = df.dropna()
    df = df[df["Volume"] > 0]

    # Indicators
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["SMA_200"] = df["Close"].rolling(200).mean()

    # Buy/Sell Signal
    df["Signal"] = 0
    df.loc[df["SMA_50"] > df["SMA_200"], "Signal"] = 1
    df.loc[df["SMA_50"] < df["SMA_200"], "Signal"] = -1

    st.subheader("Latest Market Data")
    st.dataframe(df.tail())

    # Chart
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(df["Close"], label="Price")
    ax.plot(df["SMA_50"], label="SMA 50")
    ax.plot(df["SMA_200"], label="SMA 200")
    ax.legend()
    ax.set_title(f"{ticker} Trading Chart")

    st.pyplot(fig)

    # Latest signal
    latest_signal = df["Signal"].iloc[-1]
    if latest_signal == 1:
        st.success("🟢 BUY SIGNAL")
    elif latest_signal == -1:
        st.error("🔴 SELL SIGNAL")
