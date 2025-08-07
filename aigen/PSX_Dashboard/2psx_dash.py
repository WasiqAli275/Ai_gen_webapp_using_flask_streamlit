import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import datetime
from datetime import timedelta
import ta

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Sample API configuration (replace with actual PSX API endpoints)
API_BASE_URL = "https://api.psx.com.pk/v1"  # Replace with actual PSX API base URL
PSX_SYMBOLS = ['KSE100', 'ENGRO', 'HBL', 'UBL', 'PTC', 'OGDC', 'POL', 'FABL']  # Sample PSX symbols

# Create the layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("Pakistan Stock Exchange Dashboard", className="text-center text-primary mb-4"), width=12)
    ]),
    
    # API Key Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("API Configuration"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("API Key:"),
                            dbc.Input(
                                id="api-key-input", 
                                type="password", 
                                placeholder="Enter your PSX API key",
                                persistence=True,
                                persistence_type='session'
                            ),
                        ], width=8),
                        dbc.Col([
                            dbc.Button(
                                "Save API Key", 
                                id="save-api-key-btn", 
                                color="primary", 
                                className="mt-4"
                            ),
                        ], width=4),
                    ]),
                    dbc.Alert(
                        id="api-status", 
                        children="API Key Status: Not Set", 
                        color="warning", 
                        className="mt-3"
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Controls Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Dashboard Controls"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select Symbol:"),
                            dcc.Dropdown(
                                id="symbol-dropdown",
                                options=[{'label': s, 'value': s} for s in PSX_SYMBOLS],
                                value='KSE100',
                                clearable=False
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Select Time Range:"),
                            dcc.Dropdown(
                                id="time-range-dropdown",
                                options=[
                                    {'label': '1 Week', 'value': 7},
                                    {'label': '1 Month', 'value': 30},
                                    {'label': '3 Months', 'value': 90},
                                    {'label': '6 Months', 'value': 180},
                                    {'label': '1 Year', 'value': 365}
                                ],
                                value=90,
                                clearable=False
                            ),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Refresh Data", 
                                id="refresh-data-btn", 
                                color="success", 
                                className="mt-3"
                            ),
                        ], width=12),
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Data Status
    dbc.Row([
        dbc.Col([
            dbc.Alert(
                id="data-status", 
                children="Data Status: Not Loaded", 
                color="secondary", 
                className="text-center"
            )
        ], width=12)
    ], className="mb-2"),
    
    # Charts Section
    dbc.Row([
        # Candlestick Chart
        dbc.Col([
            dcc.Loading(
                id="loading-candlestick",
                children=[dcc.Graph(id="candlestick-chart")],
                type="circle"
            )
        ], width=12, lg=8),
        
        # RSI Chart
        dbc.Col([
            dcc.Loading(
                id="loading-rsi",
                children=[dcc.Graph(id="rsi-chart")],
                type="circle"
            )
        ], width=12, lg=4),
    ], className="mb-4"),
    
    # MACD Chart
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-macd",
                children=[dcc.Graph(id="macd-chart")],
                type="circle"
            )
        ], width=12)
    ]),
    
    # Hidden div to store the API key
    html.Div(id="api-key-storage", style={'display': 'none'}),
    
    # Interval component for auto-refresh (every 5 minutes)
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

# Helper function to fetch data from PSX API
def fetch_psx_data(api_key, symbol, days):
    # This is a mock function - replace with actual API call
    # In a real implementation, you would use:
    # headers = {'Authorization': f'Bearer {api_key}'}
    # response = requests.get(f"{API_BASE_URL}/stocks/{symbol}?period={days}", headers=headers)
    # data = response.json()
    
    # For demonstration, we'll generate mock data
    end_date = datetime.datetime.now()
    start_date = end_date - timedelta(days=days)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only
    
    # Generate mock OHLC data
    base_price = np.random.uniform(100, 500)
    price_changes = np.random.normal(0, 0.02, len(date_range))
    prices = [base_price]
    
    for change in price_changes[1:]:
        prices.append(prices[-1] * (1 + change))
    
    ohlc_data = []
    for i, date in enumerate(date_range):
        if i > 0:
            open_price = prices[i-1]
            close_price = prices[i]
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
            volume = np.random.randint(10000, 500000)
        else:
            open_price = close_price = high_price = low_price = prices[i]
            volume = np.random.randint(10000, 500000)
            
        ohlc_data.append({
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(ohlc_data)

# Callback to save API key
@app.callback(
    Output("api-key-storage", "children"),
    Output("api-status", "children"),
    Output("api-status", "color"),
    Input("save-api-key-btn", "n_clicks"),
    State("api-key-input", "value"),
    prevent_initial_call=True
)
def save_api_key(n_clicks, api_key):
    if not api_key:
        return "", "API Key Status: Not Set", "warning"
    
    # In a real app, you would validate the API key here
    # For demo, we'll just accept any non-empty string
    return api_key, "API Key Status: Saved Successfully", "success"

# Callback to update all charts
@app.callback(
    [Output("candlestick-chart", "figure"),
     Output("rsi-chart", "figure"),
     Output("macd-chart", "figure"),
     Output("data-status", "children"),
     Output("data-status", "color")],
    [Input("refresh-data-btn", "n_clicks"),
     Input("interval-component", "n_intervals")],
    [State("api-key-storage", "children"),
     State("symbol-dropdown", "value"),
     State("time-range-dropdown", "value")],
    prevent_initial_call=True
)
def update_charts(n_clicks, n_intervals, api_key, symbol, days):
    ctx = callback_context
    if not ctx.triggered:
        return {}, {}, {}, "Data Status: Not Loaded", "secondary"
    
    # Check if API key is set
    if not api_key:
        return {}, {}, {}, "Data Status: API Key Required", "danger"
    
    try:
        # Fetch data from PSX API
        df = fetch_psx_data(api_key, symbol, days)
        
        if df.empty:
            return {}, {}, {}, "Data Status: No Data Available", "warning"
        
        # Calculate technical indicators
        df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # Create candlestick chart
        candlestick_fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        candlestick_fig.update_layout(
            title=f'{symbol} - Price Chart',
            xaxis_title='Date',
            yaxis_title='Price (PKR)',
            template='plotly_dark',
            height=500
        )
        
        # Create RSI chart
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='cyan')
        ))
        
        # Add overbought/oversold levels
        rsi_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        rsi_fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        
        rsi_fig.update_layout(
            title='Relative Strength Index (RSI)',
            xaxis_title='Date',
            yaxis_title='RSI',
            template='plotly_dark',
            height=300
        )
        
        # Create MACD chart
        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ))
        macd_fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='orange')
        ))
        
        # MACD histogram
        colors = np.where(df['MACD_Hist'] < 0, 'red', 'green')
        macd_fig.add_trace(go.Bar(
            x=df['date'],
            y=df['MACD_Hist'],
            name='Histogram',
            marker_color=colors
        ))
        
        macd_fig.update_layout(
            title='MACD Indicator',
            xaxis_title='Date',
            yaxis_title='Value',
            template='plotly_dark',
            height=300
        )
        
        return candlestick_fig, rsi_fig, macd_fig, f"Data Status: Loaded Successfully ({symbol})", "success"
    
    except Exception as e:
        return {}, {}, {}, f"Data Status: Error - {str(e)}", "danger"

if __name__ == '__main__':
    app.run_server(debug=True)