import pandas as pd
import re
import numpy as np
from typing import NamedTuple
import json

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping

from time import sleep
import time

INFLUXDB_ADDRESS = "192.168.252.248"
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'weather_stations'

influxdb_client = InfluxDBClient(
    INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


_init_influxdb_database()

model_temp = Sequential()
# Adding the first LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units=50, return_sequences=True,
          input_shape=(50, 1)))
model_temp.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units=50, return_sequences=True))
model_temp.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units=50, return_sequences=True))
model_temp.add(Dropout(0.2))
# Adding a fourth LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units=50))
model_temp.add(Dropout(0.2))
# Adding the output layer
model_temp.add(Dense(units=10))

# Compiling the RNN
model_temp.compile(optimizer='adam', loss='mean_squared_error')

model_temp.load_weights("weights_temp.h5")


model_hum = Sequential()
# Adding the first LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units=50, return_sequences=True,
          input_shape=(50, 1)))
model_hum.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units=50, return_sequences=True))
model_hum.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units=50, return_sequences=True))
model_hum.add(Dropout(0.2))
# Adding a fourth LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units=50))
model_hum.add(Dropout(0.2))
# Adding the output layer
model_hum.add(Dense(units=10))

# Compiling the RNN
model_hum.compile(optimizer='adam', loss='mean_squared_error')

model_hum.load_weights("weights_hum.h5")

while True:
    start_time = time.time()

    values = influxdb_client.query(
    "SELECT time, id, temperature, humidity FROM quanto ORDER BY desc LIMIT 50")


    # df = pd.DataFrame(columns=['time', 'id', 'temperature', 'humidity'])

    list_values = []

    points = values.get_points()
    for point in points:
        list_values.append(point)

    df = pd.DataFrame(list_values, columns=[
                    'time', 'id', 'temperature', 'humidity'])

    df = df.sort_values("time", ascending=True, ignore_index=True)

    sc_t = MinMaxScaler(feature_range = (0, 1))
    sc_h = MinMaxScaler(feature_range = (0, 1))
    scaled_temp = sc_t.fit_transform(df.iloc[:, 2:3].values)
    scaled_hum = sc_h.fit_transform(df.iloc[:, 3:4].values)

    x_temp = np.array(scaled_temp)
    x_temp = np.reshape(x_temp, (x_temp.shape[0], x_temp.shape[1], 1))
    x_hum = np.array(scaled_hum)
    x_hum = np.reshape(x_hum, (x_hum.shape[0], x_hum.shape[1], 1))

    predict_temp = model_temp.predict(x_temp)
    predict_temp = sc_t.inverse_transform(predict_temp)
    predict_hum = model_hum.predict(x_hum)
    predict_hum = sc_h.inverse_transform(predict_hum)


    import datetime as dt
    t1 = dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%S.%fZ')
    time_change = dt.timedelta(seconds=10)
    t = t1+ time_change
    print(df.iloc[-1,0])
    print(t)
    print("##################################")
    print("##################################")

    json_temp = [
            {
                "measurement": "predicted_temp",
                "time": dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%S.%fZ') + dt.timedelta(seconds=10),
                'tags': {
                    'id': df["id"][0],
                },
                'fields': {
                    'temperature_+1': float(predict_temp[0][0]),
                    'temperature_+2': float(predict_temp[0][1]),
                    'temperature_+3': float(predict_temp[0][2]),
                    'temperature_+4': float(predict_temp[0][3]),
                    'temperature_+5': float(predict_temp[0][4]),
                    'temperature_+6': float(predict_temp[0][5]),
                    'temperature_+7': float(predict_temp[0][6]),
                    'temperature_+8': float(predict_temp[0][7]),
                    'temperature_+9': float(predict_temp[0][8]),
                    'temperature_+10': float(predict_temp[0][9]),
                }
            }
    ]

    json_hum = [
            {
                "measurement": "predicted_hum",
                "time": dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%S.%fZ') + dt.timedelta(seconds=10),
                'tags': {
                    'id': df["id"][0],
                },
                'fields': {
                    'humidity_+1': float(predict_hum[0][0]),
                    'humidity_+2': float(predict_hum[0][1]),
                    'humidity_+3': float(predict_hum[0][2]),
                    'humidity_+4': float(predict_hum[0][3]),
                    'humidity_+5': float(predict_hum[0][4]),
                    'humidity_+6': float(predict_hum[0][5]),
                    'humidity_+7': float(predict_hum[0][6]),
                    'humidity_+8': float(predict_hum[0][7]),
                    'humidity_+9': float(predict_hum[0][8]),
                    'humidity_+10': float(predict_hum[0][9]),
                }
            }
    ]

    influxdb_client.write_points(json_temp)
    influxdb_client.write_points(json_hum)


    end_time = time.time()
    predict_time = end_time - start_time
    print("tempo per forecasting: ", predict_time)
    print("tempo di attesa: ", 1 - predict_time)
    sleep(max(1.0 - predict_time, 0))