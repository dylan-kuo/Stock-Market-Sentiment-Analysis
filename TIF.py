"""
CS677 Data Science with Python
Final Project : Sentiment Analysis & Stock Price 
@author: Tzupin Kuo
"""

from pandas_datareader import data as web
import numpy as np 
import pandas as pd
import plotly.graph_objects as go
from plotly import offline
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt


def get_stock(ticker, start_date, end_date, s_window, l_window):
    try:
        df = web.get_data_yahoo(ticker, start=start_date, end=end_date)
        df['Return'] = df['Adj Close'].pct_change()
        df['Return'].fillna(0, inplace=True)
        df['Overnight_Return'] = (df['Open'] / df['Adj Close'].shift() - 1).fillna(0)
        df['Date'] = df.index
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year 
        df['Day'] = df['Date'].dt.day
        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
            df[col] = df[col].round(2)
        df['Weekday'] = df['Date'].dt.weekday_name  
        df['Week_Number'] = df['Date'].dt.strftime('%U')
        df['Year_Week'] = df['Date'].dt.strftime('%Y-%U')
        df['Short_MA'] = df['Adj Close'].rolling(window=s_window, min_periods=1).mean()
        df['Long_MA'] = df['Adj Close'].rolling(window=l_window, min_periods=1).mean()        
        col_list = ['Date', 'Year', 'Month', 'Day', 'Weekday', 
                    'Week_Number', 'Year_Week', 'Open', 
                    'High', 'Low', 'Close', 'Volume', 'Adj Close',
                    'Return', 'Overnight_Return', 'Short_MA', 'Long_MA']
        df = df[col_list]
        return df
    except Exception as error:
        print(error)
        return None


if __name__ == "__main__":
    
    # GET STOCK INFO
    #ticker = 'LVMUY' # LVMH
    ticker = 'TIF'  # Tiffany & Co
    start_date='2019-01-01'
    end_date='2019-12-31'
    s_window = 14
    l_window = 50    
    df = get_stock(ticker, start_date, end_date, s_window, l_window)
    
    
    # GET TWEETS & SENTIMENT INFO    
    keyword = "#TiffanyAndCo"
    t_df= pd.read_csv(keyword + ".csv", sep=";", error_bad_lines=False)
    
    # SUM UP THE NUMBER OF DIFFERENT SENTIMENTS
    # vader scores
    t_df['v_is_pos'] = np.where(t_df['v_com'] > 0.05, 1, 0)
    t_df['v_is_neu'] = np.where((t_df['v_com'] <= 0.05) & (t_df['v_com'] >= -0.05) , 1, 0)
    t_df['v_is_neg'] = np.where(t_df['v_com'] < 0, 1, 0)
    
    # textblob scores
    t_df['tb_is_pos'] = np.where(t_df['tb_score'] > 0, 1, 0)
    t_df['tb_is_neu'] = np.where(t_df['tb_score'] == 0, 1, 0)
    t_df['tb_is_neg'] = np.where(t_df['tb_score'] < 0, 1, 0)
    t_df['date']= pd.to_datetime(t_df['date']) #convert dtype of date (object) to datetime
    mask = (t_df['date'] >= '2019-1-1') & (t_df['date'] < '2019-12-06') # Deleted tweets not in 2019
    t_df = t_df.loc[mask]
    t_df = t_df.reset_index(drop=True)
    #t_df.to_csv('tweets_1.csv', header=True)
    
    # GROUP THE DATA BY DATE AND CALCULATE THE NUMBER OF EACH CATEGORY OF SENTIMENTS {pos, neu, neg}
    f = {'v_is_pos': 'sum', 'v_is_neu': 'sum', 'v_is_neg': 'sum', 
         'tb_is_pos': 'sum', 'tb_is_neu': 'sum', 'tb_is_neg': 'sum'}
    t_df2 = t_df.groupby([t_df.date.dt.strftime('%Y-%m-%d')]).agg(f)
    t_df2.index = pd.to_datetime(t_df2.index)    
    df = df.loc[t_df2.index]
    df['Date'] = t_df2.index
    #t_df2.to_csv('tweets_2.csv' , encoding='utf-8')    
            
    # DRAW CANDLESTICK CHARTS
    trace_tweets_neg = go.Bar(x=t_df2.index, y=t_df2['v_is_neg'], 
                          name='Negative', marker={'color': 'red'})
    trace_tweets_pos = go.Bar(x=t_df2.index, y=t_df2['v_is_pos'], 
                          name='Positive',  marker={'color': 'mediumseagreen'})    
    trace_price = go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'], name='Stock: TIF')
    
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02
    )      
    
    # Add traces
    fig.add_trace(trace_price, row=1, col=1)
    fig.add_trace(trace_tweets_neg, row=2, col=1)
    fig.add_trace(trace_tweets_pos, row=2, col=1)    
    
    fig.update_layout(title_text="Sentiment Analysis (Vader) & Stock Price : Tiffany & Co. (ticker: TIF)",
                      xaxis_rangeslider_visible=False,
                      font=dict(
                              family='Courier New, monospace',
                              size=18,
                              color='#7f7f7f')                      
    )
                      
    # Update xaxis/yaxis properties
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
                 
    offline.plot(fig)
    
    
    # find correlation
    plt.matplotlib.style.use('ggplot')
    x = df['Adj Close'].values
    y1 = t_df2['v_is_pos'].values
    y2 = t_df2['v_is_neg'].values
    plt.scatter(x, y1, c='mediumseagreen', label='positive')
    plt.scatter(x, y2, c='red', label='negative')
    plt.xlabel('price')
    plt.ylabel('number')
    plt.title('Scatterplot for tweets of #lvmh and close price')
    plt.legend()
    plt.show()
    
    df_corr = pd.DataFrame({'v_pos': t_df2['v_is_pos'].values,
                           'v_neg': t_df2['v_is_neg'].values,
                           'price': df['Adj Close'].values})
    print(df_corr.corr())