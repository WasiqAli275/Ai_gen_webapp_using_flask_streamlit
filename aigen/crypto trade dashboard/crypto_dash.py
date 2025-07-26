import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

def fetch_price(symbol):
    """
    Fetch the latest price for a cryptocurrency pair from Binance API.
    """
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    data = response.json()
    return float(data['price'])

def fetch_historical_data(symbol, interval='1h', limit=100):
    """
    Fetch historical kline/candlestick data for a crypto pair from Binance API.
    Returns a DataFrame with timestamp and closing price.
    """
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    # Create DataFrame and select relevant columns
    df = pd.DataFrame(data, columns=[
        'open_time','open','high','low','close','volume',
        'close_time','quote_asset_volume','trades','taker_buy_base',
        'taker_buy_quote','ignore'
    ])
    # Convert time columns to datetime
    df['timestamp'] = pd.to_datetime(df['close_time'], unit='ms')
    # Keep only timestamp and closing price
    df = df[['timestamp', 'close']].copy()
    df['close'] = df['close'].astype(float)
    return df

def compute_moving_average(df, window=10):
    """
    Compute a simple moving average on the close price.
    """
    df[f'sma_{window}'] = df['close'].rolling(window=window).mean()
    return df

def plot_price_chart(df, symbol):
    """
    Plot the historical closing price and moving average.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(df['timestamp'], df['close'], label='Close Price')
    if f'sma_10' in df:
        plt.plot(df['timestamp'], df['sma_10'], label='10-period SMA')
    plt.title(f'{symbol} Price Chart')
    plt.xlabel('Time')
    plt.ylabel('Price (USDT)')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    symbol = 'BTCUSDT'  # example trading pair
    # Fetch and process historical data
    df = fetch_historical_data(symbol, interval='1h', limit=100)
    df = compute_moving_average(df, window=10)
    # Display a price chart
    plot_price_chart(df, symbol)
    # Stream live prices in a simple loop
    try:
        print(f"Streaming live prices for {symbol} (Ctrl+C to stop):")
        while True:
            price = fetch_price(symbol)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} - {symbol}: {price:.2f} USDT")
            time.sleep(5)  # pause before next fetch
    except KeyboardInterrupt:
        print("\nStopped live price streaming.")

if __name__ == "__main__":
    main()
