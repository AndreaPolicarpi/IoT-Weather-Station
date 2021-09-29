import math
import matplotlib.pyplot as plt
import keras
import pandas as pd
import numpy as np
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

from pickle import dump


file_name = "data/data.csv"
df = pd.read_csv(file_name, encoding='UTF-16 LE')
df['index'] = df.index
print("Number of rows and columns:", df.shape)
TRAINING_SIZE = 18000
TEST_SIZE = 2000

FORECASTING_WINDOW = 30
PAST_WINDOW = 60

#MODEL TEMPERATURE

training_set_temp = df.iloc[:TRAINING_SIZE, 6:7].values
test_set_temp = df.iloc[TRAINING_SIZE:TRAINING_SIZE+TEST_SIZE, 6:7].values

# Feature Scaling
sc_t = MinMaxScaler(feature_range = (0, 1))
training_set_scaled_temp = sc_t.fit_transform(training_set_temp)
dump(sc_t, open('res/scaler_t.pkl', 'wb'))
#training_set_scaled = training_set

# Creating a data structure with 60 time-steps and 1 output
X_train_temp = []
y_train_temp = []

for i in range(PAST_WINDOW, len(training_set_temp) - FORECASTING_WINDOW):
    X_train_temp.append(training_set_scaled_temp[i-PAST_WINDOW:i, 0])
    y_train_temp.append(training_set_scaled_temp[i:(i+FORECASTING_WINDOW), 0])

X_train_temp, y_train_temp = np.array(X_train_temp), np.array(y_train_temp)
X_train_temp = np.reshape(X_train_temp, (X_train_temp.shape[0], X_train_temp.shape[1], 1))


# Feature Scaling
test_set_scaled_temp = sc_t.fit_transform(test_set_temp)
#training_set_scaled = training_set

# Creating a data structure with 60 time-steps and 1 output
X_test_temp = []
y_test_temp = []

for i in range(PAST_WINDOW, len(test_set_temp) - FORECASTING_WINDOW):
    X_test_temp.append(test_set_scaled_temp[i-PAST_WINDOW:i, 0])
    y_test_temp.append(test_set_scaled_temp[i: (i+FORECASTING_WINDOW), 0])

X_test_temp, y_test_temp = np.array(X_test_temp), np.array(y_test_temp)
X_test_temp = np.reshape(X_test_temp, (X_test_temp.shape[0], X_test_temp.shape[1], 1))

model_temp = Sequential()
#Adding the first LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train_temp.shape[1], 1)))
model_temp.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 50, return_sequences = True))
model_temp.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 50, return_sequences = True))
model_temp.add(Dropout(0.2))
# Adding a fourth LSTM layer and some Dropout regularisation
model_temp.add(LSTM(units = 50))
model_temp.add(Dropout(0.2))
# Adding the output layer
model_temp.add(Dense(units = FORECASTING_WINDOW))

# Compiling the RNN
model_temp.compile(optimizer = 'adam', loss = 'mean_squared_error')

# Fitting the RNN to the Training set
model_temp.fit(X_train_temp, y_train_temp, epochs = 10, batch_size = 32, validation_data = (X_test_temp, y_test_temp))

model_temp.save_weights("res/weights_temp.h5")

# Getting the predicted stock price of 2017
dataset_train_temp = df.iloc[:TRAINING_SIZE, 6:7]
dataset_test_temp = df.iloc[TRAINING_SIZE:TRAINING_SIZE+TEST_SIZE, 6:7]

dataset_total_temp = pd.concat((dataset_train_temp, dataset_test_temp), axis = 0)

inputs_temp = dataset_total_temp[len(dataset_total_temp) - len(dataset_test_temp) - PAST_WINDOW:].values
inputs_temp = inputs_temp.reshape(-1,1)
inputs_temp = sc_t.transform(inputs_temp)
X_test_temp = []

for i in range(PAST_WINDOW, len(test_set_temp)):
    X_test_temp.append(inputs_temp[i-PAST_WINDOW:i, 0])

X_test_temp = np.array(X_test_temp)
X_test_temp = np.reshape(X_test_temp, (X_test_temp.shape[0], X_test_temp.shape[1], 1))

print(X_test_temp.shape)
# (459, 60, 1)
print("#################################")
print(X_train_temp.shape[1])
print("#################################")
predicted_temp = model_temp.predict(X_test_temp)
predicted_temp = sc_t.inverse_transform(predicted_temp)
print("#################################")
print(predicted_temp)
print("#################################")

#MODEL HUMIDITY

training_set_hum = df.iloc[:TRAINING_SIZE, 3:4].values
test_set_hum = df.iloc[TRAINING_SIZE:TRAINING_SIZE+TEST_SIZE, 3:4].values

# Feature Scaling
sc_h = MinMaxScaler(feature_range = (0, 1))
training_set_scaled_hum = sc_h.fit_transform(training_set_hum)
dump(sc_h, open('res/scaler_h.pkl', 'wb'))
#training_set_scaled = training_set

# Creating a data structure with 60 time-steps and 1 output
X_train_hum = []
y_train_hum = []

for i in range(PAST_WINDOW, len(training_set_hum) - FORECASTING_WINDOW):
    X_train_hum.append(training_set_scaled_hum[i-PAST_WINDOW:i, 0])
    y_train_hum.append(training_set_scaled_hum[i:(i+FORECASTING_WINDOW), 0])

X_train_hum, y_train_hum = np.array(X_train_hum), np.array(y_train_hum)
X_train_hum = np.reshape(X_train_hum, (X_train_hum.shape[0], X_train_hum.shape[1], 1))

# Feature Scaling
test_set_scaled_hum = sc_h.fit_transform(test_set_hum)
#training_set_scaled = training_set

# Creating a data structure with 60 time-steps and 1 output
X_test_hum = []
y_test_hum = []

for i in range(PAST_WINDOW, len(test_set_hum) - FORECASTING_WINDOW):
    X_test_hum.append(test_set_scaled_hum[i-PAST_WINDOW:i, 0])
    y_test_hum.append(test_set_scaled_hum[i: (i+FORECASTING_WINDOW), 0])

X_test_hum, y_test_hum = np.array(X_test_hum), np.array(y_test_hum)
X_test_hum = np.reshape(X_test_hum, (X_test_hum.shape[0], X_test_hum.shape[1], 1))

model_hum = Sequential()
#Adding the first LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train_hum.shape[1], 1)))
model_hum.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 50, return_sequences = True))
model_hum.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 50, return_sequences = True))
model_hum.add(Dropout(0.2))
# Adding a fourth LSTM layer and some Dropout regularisation
model_hum.add(LSTM(units = 50))
model_hum.add(Dropout(0.2))
# Adding the output layer
model_hum.add(Dense(units = FORECASTING_WINDOW))

# Compiling the RNN
model_hum.compile(optimizer = 'adam', loss = 'mean_squared_error')

# Fitting the RNN to the Training set
model_hum.fit(X_train_hum, y_train_hum, epochs = 10, batch_size = 32, validation_data = (X_test_hum, y_test_hum))

model_hum.save_weights("res/weights_hum.h5")

# Getting the predicted stock price of 2017
dataset_train_hum = df.iloc[:TRAINING_SIZE, 3:4]
dataset_test_hum = df.iloc[TRAINING_SIZE:TRAINING_SIZE+TEST_SIZE, 3:4]

dataset_total_hum = pd.concat((dataset_train_hum, dataset_test_hum), axis = 0)

inputs_hum = dataset_total_hum[len(dataset_total_hum) - len(dataset_test_hum) - PAST_WINDOW:].values
inputs_hum = inputs_hum.reshape(-1,1)
inputs_hum = sc_h.transform(inputs_hum)
X_test_hum = []

for i in range(PAST_WINDOW, len(test_set_hum)):
    X_test_hum.append(inputs_hum[i-PAST_WINDOW:i, 0])

X_test_hum = np.array(X_test_hum)
X_test_hum = np.reshape(X_test_hum, (X_test_hum.shape[0], X_test_hum.shape[1], 1))

print(X_test_hum.shape)
# (459, 60, 1)
print("#################################")
print(X_train_hum.shape[1])
print("#################################")
predicted_hum = model_hum.predict(X_test_hum)
predicted_hum = sc_h.inverse_transform(predicted_hum)
print("#################################")
print(predicted_hum)
print("#################################")

# Visualising the results
plt.figure(figsize=(12,4))
plt.plot(dataset_test_temp.values, color = "red", label = "Real weather")
plt.plot(predicted_temp[:,29], color = "blue", label = "Predicted weather")
plt.xticks(np.arange(0,len(test_set_temp),100))
plt.title('Weather Prediction')
plt.xlabel('Time')
plt.ylabel('Actual Weather')
plt.legend()
plt.show()

# Visualising the results
plt.figure(figsize=(12,4))
plt.plot(dataset_test_hum.values, color = "red", label = "Real weather")
plt.plot(predicted_hum[:,29], color = "blue", label = "Predicted weather")
plt.xticks(np.arange(0,len(test_set_hum),100))
plt.title('Weather Prediction')
plt.xlabel('Time')
plt.ylabel('Actual Weather')
plt.legend()
plt.show()