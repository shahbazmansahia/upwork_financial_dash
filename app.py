from flask import Flask, render_template

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
import sqlite3
import os
import re
import plotly
import cufflinks as cf

app = Flask(__name__)

conn = sqlite3.connect('market_data.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS market_data (
    ticker TEXT,
    datetime TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER
)
''')
conn.commit()

# cursor.execute('ALTER TABLE market_data RENAME COLUMN datetime TO timestamp;')
# conn.commit()

cf.go_offline()


data_dir = './smart-money-concepts_old/updates/Data/'


def fetch_data(ticker):
    """
    Function stub that fetches data
    TODO: add functionality to collect data using API and provided ticker value

    :ticker: ticker to fetch data for. eg: "IBM" 
    :return: market data for given ticker value
    """
    pass


def fetch_data_local():
    """
    Placeholder function that fetches local data for now

    :return: dictionary with filename as key and dataframe as value
    """
    data_dir = './smart-money-concepts_old/updates/Data/'

    regex = r'\w*.csv'
    csv_filenames = [i for i in os.listdir(data_dir) if re.match(regex, i)]
    csv_filenames
    data_files = [pd.read_csv(data_dir + i) for i in csv_filenames]
    data = dict(zip(csv_filenames, data_files))
    for k, v in data:
        data[v]['ticker'] = k
    # for i in os.listdir(data_dir):
    #    if (i)
    return data


def fetch_data_local(ticker):
    """
    Placeholder function that fetches local data for now

    :ticker: index value for fetching local files. 
    :return: dictionary with filename as key and dataframe as value
    """
    data_dir = './smart-money-concepts_old/updates/Data/'
    data_files = pd.read_csv(data_dir + ticker)
    # data = dict([ticker], data_files)
    # for k,v in data:
    #    data[v]['ticker'] = k
    # for i in os.listdir(data_dir):
    #    if (i)
    data_files['ticker'] = ticker
    return data_files


# for getting lastest timestamp using sql
# NOTE: make sure timestamp values are typecasted properly in db!

def get_latest_timestamp(ticker):
    """
        gets the latest timestamp from the given data
        NOTE: If using local files, the 'ticker' value will be the filename
        :ticker: ticker to be used to access data point; for example it will be 'IBM' for IBM's ticker. This is entirely reliant on an external API to fetch the data
        :return: returns most recent (largest) timestamp value from table or None
    """
    query = """SELECT MAX(timestamp) FROM market_data WHERE ticker = ?"""
    cursor.execute(query, (ticker, ))
    result = cursor.fetchone()[0]
    return result

# for storing data to db


def store_data_to_db(data, latest_timestamp=None):
    """
        stores the data (usually recently fetched) into our sql database

        :data:       the fetched data
        :latest:     the most recent timestamp from data
        :timestamp:  the most recent timestamp from data already stored in database
    """

    if data is not None:
        data = data.rename(columns={'datetime': 'timestamp'})
        if latest_timestamp:
            data = data[data['timestamp'] > latest_timestamp]

        if not data.empty:
            data.to_sql('market_data', conn, if_exists='append', index=False)
            print(f"Data for {data['ticker'].iloc[0]} stored successfully.")
        else:
            print(f"No New data to store.")
    else:
        print(f"No data to store.")


@app.route('/')
def index():

    init_db()

    # Fetch data from database
    # cursor.execute('SELECT * FROM market_data')
    # rows = cursor.fetchall()

    return render_template('index.html', rows=rows)


def init_db():
    tickers = ["NQ_4H.csv"]  # insert tickers you want market data for
    for ticker in tickers:
        # latest_timestamp = get_latest_timestamp(ticker)
        data = fetch_data_local(ticker)
        # store_data_to_db(data, latest_timestamp)
        store_data_to_db(data)


if __name__ == '__main__':
    app.run(debug=True)
