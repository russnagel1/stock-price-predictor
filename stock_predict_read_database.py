# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 10:29:39 2021

@author: Russ
"""

import sqlite3 
from datetime import date, timedelta
# Create lists necessary to build dictionary to send to website
list_of_stocks = ['HD', 'DAL', 'SO', 'UPS', 'KO']
prediction_symbols = ['HDpred', 'DALpred', 'SOpred', 'UPSpred', 'KOpred'] # predicted stock price
last_close_symbols = ['HDlc', 'DALlc', 'SOlc', 'UPSlc', 'KOlc'] # most recent close 
yesterdays_price_close_list = []
tomorrows_close_price_list = []

# Create dictionaries necessary to build dictionary to send to website
prediction_dict = {}
yesterdays_close_dict = {}

# Define date variables for json string
today = date.today()
yesterday = today - timedelta(days = 1)
tomorrow = today + timedelta(days = 1)
start_date = today -timedelta(days = 200)

# Open database and read into variable called data_list. Then build lists needed for dictionaries 
db = sqlite3.connect("stockpreds.sqlite")
cursor = db.cursor()
cursor.execute("SELECT * FROM stockpreds")
data_list = (cursor.fetchall())
print(data_list)
for symbol, yesterdays_close, tomorrows_close in data_list:
    yesterdays_price_close_list.append(yesterdays_close)
    tomorrows_close_price_list.append(tomorrows_close)

# close database
cursor.close()
db.close()


# Prepare json string to send to website
for i in range(len(list_of_stocks)):
    prediction_dict[prediction_symbols[i]] = tomorrows_close_price_list[i]
    yesterdays_close_dict[last_close_symbols[i]] = yesterdays_price_close_list[i]


prediction_dict.update(yesterdays_close_dict)
prediction_dict["yesterday"] = str(yesterday)
prediction_dict["tomorrow"] = str(tomorrow)
