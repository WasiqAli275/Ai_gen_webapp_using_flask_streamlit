import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

# Set page configuration
st.set_page_config(
    page_title="PSX Quantum Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    body {
        background-color: #0a0e27;
        color: #e0e6ed;
        font-family: 'Orbitron', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    
    .stTitle {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.5rem;
        background: linear-gradient(90deg, #00d9ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stMetric {
        background-color: #1e293b;
        border-radius: 0.5rem;
        padding: 1rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stDataFrame {
        background-color: #1e293b;
        border-radius: 0.5rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
    }
    
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    .css-1v0mbdj {
        background-color: #1e293b;
    }
    
    .css-1v0mbdj:hover {
        background-color: #334155;
    }
    
    .css-1cypcdb {
        background-color: #1e293b;
    }
    
    .css-1cypcdb:hover {
        background-color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='stTitle'>PSX QUANTUM DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("### Real-time Pakistan Stock Exchange Analytics with AI-Powered Insights")

# Sidebar
st.sidebar.markdown("## Dashboard Controls")
st.sidebar.markdown("---")

# Stock selection
st.sidebar.markdown("### Select Stock")
stocks = {
    "OGDC": "Oil & Gas Development Company",
    "HBL": "Habib Bank Limited",
    "UBL": "United Bank Limited",
    "ENGRO": "Engro Corporation",
    "PSO": "Pakistan State Oil",
    "MCB": "MCB Bank Limited",
    "BAFL": "Bank Alfalah",
    "PTC": "Pakistan Telecommunication",
    "FFC": "Fauji Fertilizer Company",
    "LUCK": "Lucky Cement",
    "DGKC": "DG Khan Cement",
    "NML": "Nishat Mills Limited",
    "FABL": "Faysal Bank Limited",
    "KEL": "K-Electric Limited",
    "PPL": "Pakistan Petroleum Limited"
}

selected_stock = st.sidebar.selectbox("Choose a stock", list(stocks.keys()), format_func=lambda x: f"{x} - {stocks[x]}")

# Time period selection
st.sidebar.markdown("### Time Period")
time_period = st.sidebar.radio("Select timeframe", ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year"])

# Technical indicators
st.sidebar.markdown("### Technical Indicators")
show_macd = st.sidebar.checkbox("MACD", value=True)
show_rsi = st.sidebar.checkbox("RSI", value=True)
show_bollinger = st.sidebar.checkbox("Bollinger Bands", value=False)
show_volume = st.sidebar.checkbox("Volume", value=True)

# Refresh button
refresh = st.sidebar.button("Refresh Data")

# Simulated data fetching function
def fetch_stock_data(symbol, period):
    # In a real implementation, this would scrape PSX website or use an API
    # For demo purposes, we'll generate synthetic data
    
    end_date = datetime.now()
    
    if period == "1 Day":
        start_date = end_date - timedelta(days=1)
        interval = "5m"
    elif period == "1 Week":
        start_date = end_date - timedelta(weeks=1)
        interval = "30m"
    elif period == "1 Month":
        start_date = end_date - timedelta(days=30)
        interval = "1h"
    elif period == "3 Months":
        start_date = end_date - timedelta(days=90)
        interval = "1d"
    elif period == "6 Months":
        start_date = end_date - timedelta(days=180)
        interval = "1d"
    else:  # 1 Year
        start_date = end_date - timedelta(days=365)
        interval = "1d"
    
    # Generate synthetic data
    dates = pd.date_range(start=start_date, end=end_date, freq=interval)
    
    # Base price with some randomness
    base_price = np.random.uniform(100, 500)
    
    # Generate price movements
    price_changes = np.random.normal(0, 0.02, size=len(dates))
    prices = [base_price]
    
    for change in price_changes[1:]:
        prices.append(prices[-1] * (1 + change))
    
    # Create OHLC data
    data = {
        'Date': dates,
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Close': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'Volume': [int(np.random.uniform(10000, 500000)) for _ in prices]
    }
    
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    
    return df

# Calculate technical indicators
def calculate_indicators(df):
    # MACD
    ema_12 = df['Close'].ewm(span=12).mean()
    ema_26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema_12 - ema_26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['Middle_Band'] = df['Close'].rolling(window=20).mean()
    df['Upper_Band'] = df['Middle_Band'] + 2 * df['Close'].rolling(window=20).std()
    df['Lower_Band'] = df['Middle_Band'] - 2 * df['Close'].rolling(window=20).std()
    
    return df

# Fetch and process data
with st.spinner("Fetching market data..."):
    stock_data = fetch_stock_data(selected_stock, time_period)
    stock_data = calculate_indicators(stock_data)
    
    # Get latest data
    latest = stock_data.iloc[-1]
    prev_close = stock_data.iloc[-2]['Close']
    change = latest['Close'] - prev_close
    change_pct = (change / prev_close) * 100

# Display key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Current Price",
        value=f"PKR {latest['Close']:.2f}",
        delta=f"{change:.2f} ({change_pct:.2f}%)"
    )

with col2:
    st.metric(
        label="Volume",
        value=f"{latest['Volume']:,}"
    )

with col3:
    st.metric(
        label="Market Cap",
        value=f"PKR {np.random.uniform(10, 100):.1f}B"
    )

with col4:
    st.metric(
        label="52W Range",
        value=f"PKR {np.random.uniform(80, 120):.0f} - {np.random.uniform(180, 220):.0f}"
    )

# Create candlestick chart with indicators
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=[0.5, 0.15, 0.15, 0.2]
)

# Candlestick chart
fig.add_trace(
    go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close'],
        name="Price",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff3366'
    ),
    row=1, col=1
)

# Bollinger Bands
if show_bollinger:
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Upper_Band'],
            line=dict(color='#00d9ff', width=1),
            name="Upper Band",
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Lower_Band'],
            line=dict(color='#00d9ff', width=1),
            fill="tonexty",
            fillcolor="rgba(0, 217, 255, 0.1)",
            name="Lower Band",
            showlegend=False
        ),
        row=1, col=1
    )

# Volume chart
if show_volume:
    colors = ['#00ff88' if row['Close'] >= row['Open'] else '#ff3366' for _, row in stock_data.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=stock_data.index,
            y=stock_data['Volume'],
            name="Volume",
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )

# MACD chart
if show_macd:
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['MACD'],
            line=dict(color='#00d9ff', width=1.5),
            name="MACD",
            showlegend=False
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Signal'],
            line=dict(color='#ff9900', width=1.5),
            name="Signal",
            showlegend=False
        ),
        row=3, col=1
    )
    
    colors = ['#00ff88' if val >= 0 else '#ff3366' for val in stock_data['MACD_Histogram']]
    
    fig.add_trace(
        go.Bar(
            x=stock_data.index,
            y=stock_data['MACD_Histogram'],
            name="Histogram",
            marker_color=colors,
            opacity=0.7
        ),
        row=3, col=1
    )

# RSI chart
if show_rsi:
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['RSI'],
            line=dict(color='#ff00ff', width=1.5),
            name="RSI",
            showlegend=False
        ),
        row=4, col=1
    )
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line=dict(color='red', width=1, dash='dash'), row=4, col=1)
    fig.add_hline(y=30, line=dict(color='green', width=1, dash='dash'), row=4, col=1)

# Update layout
fig.update_layout(
    title=f"{selected_stock} - {stocks[selected_stock]}",
    title_font=dict(size=20, family="Orbitron", color="#e0e6ed"),
    xaxis_rangeslider_visible=False,
    plot_bgcolor='rgba(15, 23, 42, 0.8)',
    paper_bgcolor='rgba(15, 23, 42, 0)',
    font=dict(color="#e0e6ed", family="Orbitron"),
    margin=dict(l=20, r=20, t=50, b=20),
    height=900,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Update y-axis labels
fig.update_yaxes(title_text="Price (PKR)", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)
fig.update_yaxes(title_text="MACD", row=3, col=1)
fig.update_yaxes(title_text="RSI", row=4, col=1)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Market news section
st.markdown("---")
st.markdown("## Market News & Analysis")

# Simulated news feed
news_data = [
    {
        "title": "PSX Index Reaches All-Time High",
        "source": "Financial Times",
        "time": "2 hours ago",
        "summary": "Pakistan Stock Exchange benchmark index crosses 50,000 points for the first time in history."
    },
    {
        "title": "OGDC Announces Major Gas Discovery",
        "source": "Dawn",
        "time": "5 hours ago",
        "summary": "Oil and Gas Development Company discovers new gas reserves in Sindh province."
    },
    {
        "title": "SBP Maintains Interest Rate at 22%",
        "source": "The News",
        "time": "1 day ago",
        "summary": "State Bank of Pakistan keeps policy rate unchanged in latest monetary policy announcement."
    },
    {
        "title": "Cement Sector Shows Strong Growth",
        "source": "Business Recorder",
        "time": "1 day ago",
        "summary": "Cement companies report 15% increase in dispatches due to infrastructure projects."
    }
]

for news in news_data:
    with st.expander(f"**{news['title']}** - {news['source']} ({news['time']})"):
        st.markdown(news['summary'])

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8;">
        <p>PSX Quantum Dashboard v1.0 | Data updates every 5 minutes</p>
        <p>Disclaimer: This is a demonstration dashboard. For real-time trading, use official financial platforms.</p>
    </div>
    """,
    unsafe_allow_html=True
)