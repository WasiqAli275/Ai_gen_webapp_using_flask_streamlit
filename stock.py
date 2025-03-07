# import libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from PIL import Image


# Title
app_name = 'Stock Market Forcasting App Analysis results'
st.title(app_name)
st.subheader('This app is created to forcast the stock market price of the seledted company')
# add an image from an onlnie recource
st.image("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Ffree-photos-vectors%2Fstock-market&psig=AOvVaw0EqIoi-d0GLMiKq4afgZ_T&ust=1741444426437000&source=images&cd=vfe&opi=89978449&ved=0CBcQjhxqFwoTCMDS8aCY-IsDFQAAAAAdAAAAABAE")
st.image("https://www.freepik.com/premium-photo/3d-rendering-stock-indexes-virtual-space-economic-growth-recession_20067081.htm#fromView=keyword&page=1&position=7&uuid=4ea8946b-247a-473a-8b44-20822eaf5292&query=Stock+Market")
image1 = Image.open('images.jpg')
st.write(image1)

# take input from the user of app about the start and end date

# sidebar
st.sidebar.header('select the paremater from below')

start_date = st.sidebar.date_input('Start date', date(2020, 1, 1))
end_date = st.sidebar.date_input('End Date', date(2020, 12, 31))
# add ticker symbol list
ticker_list = ['AAPL', 'MSFT', "GOOG", "GOOGL", 'META', 'TSLA', 'NVDA', 'ADBE', 'PYPL', 'INTC', 'CNCSA', 'NFLX', 'PEP']
ticker = st.sidebar.selectbox('Select the company', ticker_list)

# fetch data from user input using Yfinance liberary
data = yf.download(ticker, start=start_date,end=end_date)
# add data as a column to the dataframe
data.insert(0, "Date", data.index, True)
data.reset_index(drop=True, inplace=True)

st.write('Data from', start_date, 'to', end_date)
st.write(data)

# plot the data
st.header("Data visualization")
fig = px.line(data, x='Date', y=data.columns, title='closing price of the stock market')
st.plotly_chart(fig)
