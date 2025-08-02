import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import yfinance as yf
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="PSX Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

class PSXDashboard:
    def __init__(self):
        self.major_stocks = [
            'HBL', 'UBL', 'BAFL', 'MCB', 'NBP',  # Banks
            'OGDC', 'PPL', 'PSO', 'SNGP', 'SSGC',  # Oil & Gas
            'ENGRO', 'FFC', 'EFERT', 'FATIMA',  # Fertilizer
            'LUCK', 'MLCF', 'CHCC', 'DGKC',  # Cement
            'TRG', 'SYS', 'NETSOL', 'AVN',  # Technology
            'NESTLE', 'UNILEVER', 'ICI', 'COLG',  # FMCG
            'HUBC', 'KEL', 'KAPCO', 'LOTTE'  # Power & Others
        ]
        
        self.sectors = {
            'Banking': ['HBL', 'UBL', 'BAFL', 'MCB', 'NBP'],
            'Oil & Gas': ['OGDC', 'PPL', 'PSO', 'SNGP', 'SSGC'],
            'Fertilizer': ['ENGRO', 'FFC', 'EFERT', 'FATIMA'],
            'Cement': ['LUCK', 'MLCF', 'CHCC', 'DGKC'],
            'Technology': ['TRG', 'SYS', 'NETSOL', 'AVN'],
            'FMCG': ['NESTLE', 'UNILEVER', 'ICI', 'COLG'],
            'Power': ['HUBC', 'KEL', 'KAPCO', 'LOTTE']
        }

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_sample_market_data(_self):
        """Generate sample PSX market data for demonstration"""
        np.random.seed(42)
        
        # Market indices data
        indices_data = {
            'KSE-100': {'value': 41500 + np.random.randint(-500, 500), 'change': np.random.uniform(-2, 2)},
            'KSE-30': {'value': 15200 + np.random.randint(-200, 200), 'change': np.random.uniform(-2, 2)},
            'KMI-30': {'value': 54800 + np.random.randint(-800, 800), 'change': np.random.uniform(-2, 2)}
        }
        
        # Stock data
        stocks_data = []
        for stock in _self.major_stocks:
            base_price = np.random.uniform(50, 500)
            change_pct = np.random.uniform(-5, 5)
            volume = np.random.randint(100000, 10000000)
            
            stocks_data.append({
                'Symbol': stock,
                'Price': round(base_price, 2),
                'Change': round(base_price * change_pct / 100, 2),
                'Change%': round(change_pct, 2),
                'Volume': volume,
                'High': round(base_price * 1.05, 2),
                'Low': round(base_price * 0.95, 2),
                'Market_Cap': round(base_price * np.random.randint(1000000, 50000000) / 1000000, 2)
            })
        
        return indices_data, pd.DataFrame(stocks_data)

    def generate_historical_data(self, symbol, days=30):
        """Generate sample historical data for charts"""
        np.random.seed(hash(symbol) % 2**32)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic price movement
        base_price = np.random.uniform(100, 400)
        prices = [base_price]
        
        for i in range(1, days):
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 10))  # Minimum price of 10
        
        # Generate OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            high = price * np.random.uniform(1.0, 1.05)
            low = price * np.random.uniform(0.95, 1.0)
            volume = np.random.randint(100000, 2000000)
            
            data.append({
                'Date': date,
                'Open': round(price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(price, 2),
                'Volume': volume
            })
        
        return pd.DataFrame(data)

    def calculate_technical_indicators(self, df):
        """Calculate basic technical indicators"""
        # Simple Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        
        # RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        return df

    def create_candlestick_chart(self, df, symbol):
        """Create candlestick chart with technical indicators"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'{symbol} Price Chart', 'Volume', 'RSI'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"
            ),
            row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['SMA_5'], name='SMA 5', line=dict(color='orange', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['SMA_20'], name='SMA 20', line=dict(color='red', width=1)),
            row=1, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='lightblue'),
            row=2, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=3, col=1
        )
        
        # RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(
            title=f'{symbol} Technical Analysis',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True
        )
        
        return fig

def main():
    dashboard = PSXDashboard()
    
    # Header
    st.markdown('<h1 class="main-header">📈 Pakistan Stock Exchange (PSX) Trading Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Get market data
    with st.spinner("Loading market data..."):
        indices_data, stocks_df = dashboard.get_sample_market_data()
    
    # Market Indices Section
    st.header("📊 Market Indices")
    col1, col2, col3 = st.columns(3)
    
    for i, (index_name, data) in enumerate(indices_data.items()):
        col = [col1, col2, col3][i]
        change_color = "positive" if data['change'] >= 0 else "negative"
        change_symbol = "+" if data['change'] >= 0 else ""
        
        with col:
            st.metric(
                label=index_name,
                value=f"{data['value']:,.0f}",
                delta=f"{change_symbol}{data['change']:.2f}%"
            )
    
    # Market Summary
    st.header("📈 Market Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stocks", len(stocks_df))
    with col2:
        gainers = len(stocks_df[stocks_df['Change%'] > 0])
        st.metric("Gainers", gainers, delta=f"{gainers/len(stocks_df)*100:.1f}%")
    with col3:
        losers = len(stocks_df[stocks_df['Change%'] < 0])
        st.metric("Losers", losers, delta=f"{losers/len(stocks_df)*100:.1f}%")
    with col4:
        avg_volume = stocks_df['Volume'].mean()
        st.metric("Avg Volume", f"{avg_volume:,.0f}")
    
    # Top Gainers and Losers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top Gainers")
        top_gainers = stocks_df.nlargest(5, 'Change%')[['Symbol', 'Price', 'Change%']]
        st.dataframe(
            top_gainers,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.subheader("📉 Top Losers")
        top_losers = stocks_df.nsmallest(5, 'Change%')[['Symbol', 'Price', 'Change%']]
        st.dataframe(
            top_losers,
            use_container_width=True,
            hide_index=True
        )
    
    # Sector Performance
    st.header("🏭 Sector Performance")
    
    sector_perfor