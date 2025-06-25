# import libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date
from PIL import Image

# Title
app_name = 'Stock Market Forecasting App Analysis Results'
st.title(app_name)
st.subheader('This app is created to forecast the stock market price of the selected company')

# Add an image from a local file
image1 = Image.open('images.jpg')
st.image(image1, caption='Stock Market Image')

# Sidebar
st.sidebar.header('Select the parameters from below')

# Take input from the user of the app about the start and end date
start_date = st.sidebar.date_input('Start date', date(2020, 1, 1))
end_date = st.sidebar.date_input('End date', date(2020, 12, 31))

# Add ticker symbol list
ticker_list = ["AAPL", "MSFT", "GOOG", "GOOGL", "META", "TSLA", "NVDA", "ADBE", "PYPL", "INTC", "CMCSA", "NFLX", "PEP"]
ticker = st.sidebar.selectbox('Select the company', ticker_list)

# Fetch data from user input using yfinance library
data = yf.download(ticker, start=start_date, end=end_date)

# Check if data is empty
if data.empty:
    st.error(f"No data found for {ticker} between {start_date} and {end_date}")
else:
    # Add data as a column to the dataframe
    data['Date'] = data.index
    data.reset_index(drop=True, inplace=True)

    st.write('Data from', start_date, 'to', end_date)
    st.write(data)

    # # Plot the data
    # st.header("Data visualization")
    # fig = px.line(data, x='Date', y='Close', title='Closing Price of the Stock Market', width=1000, height=600)
    # st.plotly_chart(fig)

    # Add a selectbox to select data from columns
    column = st.selectbox('Select the column to be used for forecasting', data.columns[1:])

    # Subset the data and ensure it's 1-dimensional
    selected_data = data[['Date', column]]
    selected_data = selected_data.dropna()  # Drop any NaN values
    st.write("Selected data")
    st.write(selected_data)

    # Convert the column to a 1-dimensional array if needed
    if selected_data[column].ndim > 1:
        selected_data[column] = selected_data[column].squeeze()

    # Plot the selected data
    fig2 = px.line(selected_data, x='Date', y=column, title=f'{column} of the Stock Market', width=1000, height=600)
    st.plotly_chart(fig2)