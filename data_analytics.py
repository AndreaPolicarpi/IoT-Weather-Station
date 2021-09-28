import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

file_name = "data/data.csv"
data = pd.read_csv(file_name, encoding='UTF-16 LE')

print(data)

def create_lstm_model(units):
    lstm_model = tf.keras.models.Sequential([
        # Shape [batch, time, features] => [batch, time, lstm_units]
        tf.keras.layers.LSTM(units, return_sequences=True),
        # Shape => [batch, time, features]
        tf.keras.layers.Dense(10)
    ])
    return lstm_model

model = create_lstm_model(50)

FORECASTING_WINDOW = 10
PAST_WINDOW = 50

def create_dataset(column, data):

    x = np.zeros(PAST_WINDOW)
    y = np.zeros(FORECASTING_WINDOW)

    series = data[column]

    for i in range(len(series)-FORECASTING_WINDOW-PAST_WINDOW):
        temp_x = series[i:(i+PAST_WINDOW)]
        temp_y = series[(i+PAST_WINDOW): (i+PAST_WINDOW+FORECASTING_WINDOW)]

        x = np.vstack((x, temp_x))
        y = np.vstack((y, temp_y))

    x = np.delete(x, (0), axis=0)
    y = np.delete(y, (0), axis=0)

    x = x[:, np.newaxis]
    y = y[:, np.newaxis]

    return x, y

humidity_x, humidity_y = create_dataset("humidity", data)
temperature_x, temperature_y = create_dataset("temperature", data)
print("###################################")
print(humidity_x.shape)
print(humidity_y.shape)
print("###################################")

model.compile(
    loss="mse",
    optimizer="sgd",
    metrics=[tf.keras.metrics.MeanSquaredError()]
)

model.fit(humidity_x,humidity_y, batch_size=64, epochs=1)

result = model.predict(humidity_x)
print(result[0], humidity_y[0])