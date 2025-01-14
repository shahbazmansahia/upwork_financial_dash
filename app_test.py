# from .'smart-money-concepts_old'.Extend.SHSL import detect_swing_highs_lows
# from SHSL import detect_swing_highs_lows
import sqlite3
import plotly.graph_objs as go
import pandas as pd  # don't forget to import pandas too!
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import datetime
import time
import sys
import os

# for detecting swing highs and lows
abs_path = os.path.abspath('./smart-money-concepts_old/Extend')
sys.path.insert(0, abs_path)
from SHSL import detect_swing_highs_lows

# Connect to your SQLite database
conn = sqlite3.connect('market_data.db', check_same_thread=False)

# Define a function to fetch data from the database
app = Dash(__name__)


def get_data(ticker):
    query = """SELECT * FROM market_data WHERE ticker=?"""
    cursor = conn.cursor()
    cursor.execute(query, (ticker,))
    rows = cursor.fetchall()
    data = pd.DataFrame(rows)
    data.columns = ["ticker", "datetime", "open", "high", "low", "close", "volume"]
    return data


# print(f"data fetched: {get_data('NQ_4H.csv')}")
# Define the layout of your app
app.layout = html.Div([
    dcc.Dropdown(
        id='ticker-dropdown',
        options=[{'label': ticker, 'value': ticker}
                 for ticker in get_data('NQ_4H.csv')['ticker'].unique()],
        value=get_data('NQ_4H.csv')['ticker'].unique()[0]
    ),
    dcc.Graph(id='market-data-graph')
])

data_dict = {}
for ticker in get_data('NQ_4H.csv')['ticker'].unique():
    data_dict[ticker] = get_data(ticker)

# Define a callback function to update the graph based on the selected ticker


# @app.callback(
#     Output('market-data-graph', 'figure'),
#     [Input('ticker-dropdown', 'value')]
# )
# def update_graph(ticker):
#     data = get_data(ticker).set_index('datetime')[['close']]
#     fig = go.Figure(data=[go.Scatter(x=data.index, y=data['close'])])
#     return fig
@app.callback(
    Output('market-data-graph', 'figure'),
    [Input('ticker-dropdown', 'value')]
)
def update_graph(ticker):
    if ticker not in data_dict:
        data = get_data(ticker)
    else:
        data = data_dict[ticker]

    data.columns = [str.capitalize(column) for column in data.columns]
    fig = go.Figure(data=[go.Candlestick(x=data['Datetime'],
                                         open=data['Open'],
                                         close=data['Close'],
                                         high=data['High'],
                                         low=data['Low']
                                         )])
    data = detect_swing_highs_lows(data)

    return fig


# run the app
if __name__ == '__main__':
    app.run_server(debug=False)
    time.sleep(15)
