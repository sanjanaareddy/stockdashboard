import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

st.title("Stock Dashboard")

# Sidebar for inputs
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

# Fetch stock data
data = yf.download(ticker, start=start_date, end=end_date)

# Check if data is available and plot
if data.empty:
    st.error("No data found for the given ticker and date range. Please try again.")
elif 'Adj Close' not in data.columns:
    st.error("Adjusted Close data not available for this ticker.")
else:
    fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
    st.plotly_chart(fig)

# Tabs for different data sections
pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# Pricing Data Tab
with pricing_data:
    st.header('Price Movements')
    data2 = data.copy()
    if 'Adj Close' in data2.columns:
        data2['% Change'] = data2['Adj Close'] / data2['Adj Close'].shift(1) - 1
        data2.dropna(inplace=True)
        st.write(data2)

        # Calculate and display annual return, standard deviation, and risk-adjusted return
        annual_return = data2['% Change'].mean() * 252 * 100
        st.write('Annual Return is ', annual_return, '%')
        stdev = np.std(data2['% Change']) * np.sqrt(252)
        st.write('Standard Deviation is ', stdev * 100, '%')
        st.write('Risk Adjusted Return is ', annual_return / (stdev * 100))
    else:
        st.warning("Adjusted Close data not available for price movement analysis.")

# Fundamental Data Tab
with fundamental_data:
    key = 'OW1639L63B5UCYYL'
    fd = FundamentalData(key, output_format='pandas')
    
    try:
        st.subheader('Balance Sheet')
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)
        
        st.subheader('Income Statement')
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)
        
        st.subheader('Cash Flow Statement')
        cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cf = cash_flow.T[2:]
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf)
    except Exception as e:
        st.error(f"Error fetching data from Alpha Vantage: {e}")

# News Tab
with news:
    st.header(f'News for {ticker}')
    try:
        sn = StockNews(ticker, save_news=False)
        df_news = sn.read_rss()

        # Display the top 10 news items if available
        for i in range(min(10, len(df_news))):
            st.subheader(f'News {i + 1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            st.write(f"Title Sentiment: {df_news['sentiment_title'][i]}")
            st.write(f"News Sentiment: {df_news['sentiment_summary'][i]}")
    except Exception as e:
        st.error(f"Error fetching news data: {e}")




