# -*- coding: utf-8 -*-
'''

Home Depot  HD
Delta       DAL
Southern Co SO
UPS         UPS
Coke        KO

'''
import sqlite3
from datetime import date, timedelta
import yahoo_fin.stock_info as si
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import LSTM
from keras.layers import Dense, Dropout
import pandas as pd
import json
from flask import Flask
from flask import jsonify
#from matplotlib import pyplot as plt
#from sklearn.preprocessing import StandardScaler
#import seaborn as sns
import tensorflow as tf
from flask_cors import CORS,cross_origin

app = Flask(__name__)
cors = CORS(app)
#                   Prepare needed lists

yesterdays_price_close_list = []
tomorrows_close_price_list = []
#yesterdays_prediction_list = []
#close_2_days_ago_list = []


#                Load model into memory
def get_model():
    global model
    model = tf.keras.models.load_model('stock_predict_model.h5', compile=False)
    print(" * Model loaded!") 
get_model()


#                Set historical dates to read 
today = date.today()
yesterday = today - timedelta(days = 1)
tomorrow = today + timedelta(days = 1)
start_date = today -timedelta(days = 200)

  
#                Load price data and make prediction
stocks_to_scan = ['HD', 'DAL', 'SO', 'UPS', 'KO']
for stock_symbol in stocks_to_scan:
    df = si.get_data(stock_symbol, start_date=start_date, end_date=today)
    df.drop(['ticker'],axis=1, inplace=True)
    df=df.dropna()
    df_last_index = len(df)-1
    yesterdays_price_close = df.iloc[df_last_index]['close'].round(2)
    yesterdays_price_close_list.append(yesterdays_price_close)
#    close_2_days_ago = df.iloc[df_last_index-2]['close'].round(2)
#    close_2_days_ago_list.append(close_2_days_ago)
#    print('Yesterdays price close: ' + str(yesterdays_price_close))


#                   Basic Feature Engineering
    Slope5 = []
    Slope15 = []
    for i in range(0, len(df)):
        Slope5.append((df.iloc[i]['close']) - (df.iloc[i-5]['close']))
        Slope15.append((df.iloc[i]['close']) - (df.iloc[i-15]['close']))
    df['slope5'] = Slope5
    df['slope15'] = Slope15
    df['5 MA'] = df['close'].rolling(5).mean()
    df['25 MA'] = df['close'].rolling(25).mean()
    df.dropna(inplace=True)
    df['open'] = df['open'].pct_change()
    df['high'] = df['high'].pct_change()
    df['low'] = df['low'].pct_change()
    df['close'] = df['close'].pct_change()
    df['adjclose'] = df['adjclose'].pct_change()
    df['volume'] = df['volume'].pct_change()
    df['5 MA'] = df['5 MA'].pct_change()
    df['25 MA'] = df['25 MA'].pct_change()
    df.dropna(inplace=True)
    cols = list(df)[0:11]
    df_for_training = df[cols].astype(float) 
    df_for_training2 = df_for_training.to_numpy()
    
    
    
    trainX = []


    n_future = 1
    n_past = 14


    for i in range(n_past, len(df_for_training2) - n_future +1):
        trainX.append(df_for_training2[i - n_past:i, 0:df_for_training.shape[1]])
    
    trainX = np.array(trainX) 

    temp_var = trainX[-n_future]

    fcast = model.predict(trainX[-n_future:]) #forecast
    forecast = fcast[0,0]
    tomorrows_close_price = (yesterdays_price_close + (yesterdays_price_close * forecast)).round(2)
    tomorrows_close_price_list.append(tomorrows_close_price)
#    yesterdays_prediction_list = tomorrows_close_price_list[:]
    
list_of_stocks = ['HD', 'DAL', 'SO', 'UPS', 'KO']
prediction_symbols = ['HDpred', 'DALpred', 'SOpred', 'UPSpred', 'KOpred'] # predicted stock price
last_close_symbols = ['HDlc', 'DALlc', 'SOlc', 'UPSlc', 'KOlc'] # most recent close 
    
    
db = sqlite3.connect("stockpreds.sqlite")
db.execute("CREATE TABLE IF NOT EXISTS stockpreds(symbol TEXT, yesterdays_close FLOAT, tomorrows_close FLOAT)")
db.executemany("INSERT INTO stockpreds(symbol, yesterdays_close, tomorrows_close) VALUES(?, ?, ?)", zip(list_of_stocks, yesterdays_price_close_list, tomorrows_close_price_list))

db.commit()
db.close()
