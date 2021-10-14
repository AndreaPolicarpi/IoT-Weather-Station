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

from pickle import load 

#INFLUXDB_ADDRESS = "192.168.1.71"
INFLUXDB_ADDRESS = "192.168.200.248"
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'weather_stations'

FORECASTING_WINDOW = 30

ID_SENSOR = 'ArezzoSensor'

influxdb_client = InfluxDBClient(
    INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


_init_influxdb_database()

model_temp = Sequential()
#Adding the first LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 64, return_sequences = True, input_shape=(60, 1)))
model_temp.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 32, return_sequences = True))
model_temp.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 32))
model_temp.add(Dropout(0.2))
# Adding the output layer
model_temp.add(Dense(units = FORECASTING_WINDOW))
# Compiling the RNN
model_temp.compile(optimizer='adam', loss='mean_squared_error')

model_temp.load_weights("res/weights_temp.h5")


model_hum = Sequential()
#Adding the first LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 64, return_sequences = True, input_shape=(60, 1)))
model_hum.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 32, return_sequences = True))
model_hum.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 32))
model_hum.add(Dropout(0.2))
# Adding the output layer
model_hum.add(Dense(units = FORECASTING_WINDOW))
# Compiling the RNN
model_hum.compile(optimizer='adam', loss='mean_squared_error')

model_hum.load_weights("res/weights_hum.h5")

while True:
    start_time = time.time()

    #values = influxdb_client.query(
    #"SELECT time, id, temperature, humidity FROM quanto ORDER BY desc LIMIT 50")

    values = influxdb_client.query(
    'SELECT MEAN("temperature"), MEAN("humidity") FROM "quanto" WHERE time >= now() - 70s AND "id" = \'{}\' GROUP BY time(1s)'.format(ID_SENSOR))

    # df = pd.DataFrame(columns=['time', 'id', 'temperature', 'humidity'])

    list_values = []

    points = values.get_points()
    for point in points:
        list_values.append(point)

    df = pd.DataFrame(list_values, columns=['time', 'mean', 'mean_1']
        ).rename(columns={'mean': 'temperature', 'mean_1': 'humidity'}).fillna(method="bfill")


    df = df.sort_values("time", ascending=True, ignore_index=True)

    #df['time'] = [pd.to_datetime(df.iloc[i, 0]) for i in range(len(df))]

    """series_t = pd.Series(df['temperature'].values, index= pd.to_datetime(df['time'].values))
    print(series_t)

    upsampled = series_t.resample('s')
    interpolated = upsampled.interpolate(method='spline', order=2)
    #interpolated = upsampled.interpolate(method='linear')
    print(interpolated)
    exit()"""

    sc_t =  load(open("res/scaler_t.pkl", "rb"))
    sc_h =  load(open("res/scaler_h.pkl", "rb"))

    scaled_temp = sc_t.fit_transform(df.iloc[:60, 1:2].values)
    scaled_hum = sc_h.fit_transform(df.iloc[:60, 2:3].values)

    x_temp = np.array(scaled_temp)
    x_temp = np.reshape(x_temp, (x_temp.shape[0], x_temp.shape[1], 1))
    x_hum = np.array(scaled_hum)
    x_hum = np.reshape(x_hum, (x_hum.shape[0], x_hum.shape[1], 1))

    predict_temp = model_temp.predict(x_temp)
    predict_temp = sc_t.inverse_transform(predict_temp)
    predict_hum = model_hum.predict(x_hum)
    predict_hum = sc_h.inverse_transform(predict_hum)


    import datetime as dt
    try:
        t = dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        t = dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%SZ')

    json_temp_10s = [
            {
                "measurement": "predicted_temp_10s",
                "time": t + dt.timedelta(seconds=10),
                'tags': {
                    'id': ID_SENSOR,
                },
                'fields': {
                    'temperature': float(predict_temp[0][9]),
                }
            }
    ]

    json_temp_20s = [
        {
            "measurement": "predicted_temp_20s",
            "time": t + dt.timedelta(seconds=20),
            'tags': {
                'id': ID_SENSOR,
            },
            'fields': {
                'temperature': float(predict_temp[0][19]),
            }
        }
    ]

    json_temp_30s = [
        {
            "measurement": "predicted_temp_30s",
            "time": t + dt.timedelta(seconds=30),
            'tags': {
                'id': ID_SENSOR,
            },
            'fields': {
                'temperature': float(predict_temp[0][29]),
            }
        }
    ]


    json_hum_10s = [
        {
            "measurement": "predicted_hum_10s",
            "time": t + dt.timedelta(seconds=10),
            'tags': {
                'id': ID_SENSOR,
            },
            'fields': {
                'humidity': float(predict_hum[0][9]),
            }
        }
    ]

    json_hum_20s = [
        {
            "measurement": "predicted_hum_20s",
            "time": dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%SZ') + dt.timedelta(seconds=20),
            'tags': {
                'id': ID_SENSOR,
            },
            'fields': {
                'humidity': float(predict_hum[0][19]),
            }
        }
    ]

    json_hum_30s = [
        {
            "measurement": "predicted_hum_30s",
            "time": dt.datetime.strptime(df.iloc[-1,0], '%Y-%m-%dT%H:%M:%SZ') + dt.timedelta(seconds=30),
            'tags': {
                'id': ID_SENSOR,
            },
            'fields': {
                'humidity': float(predict_hum[0][29]),
            }
        }
    ]



    influxdb_client.write_points(json_temp_10s)
    influxdb_client.write_points(json_temp_20s)
    influxdb_client.write_points(json_temp_30s)
    influxdb_client.write_points(json_hum_10s)
    influxdb_client.write_points(json_hum_20s)
    influxdb_client.write_points(json_hum_30s)


    end_time = time.time()
    predict_time = end_time - start_time
    print("tempo per forecasting: ", predict_time)
    print("tempo di attesa: ", 1 - predict_time)
    sleep(max(1.0 - predict_time, 0))