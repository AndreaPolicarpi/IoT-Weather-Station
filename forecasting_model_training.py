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


file_name = "data.csv"
df = pd.read_csv(file_name, encoding='UTF-16 LE')
df['index'] = df.index
print("Number of rows and columns:", df.shape)
TRAINING_SIZE = 8000
TEST_SIZE = 2000

training_set = df.iloc[:TRAINING_SIZE, 6:7].values
test_set = df.iloc[TRAINING_SIZE:TRAINING_SIZE+TEST_SIZE, 6:7].values

FORECASTING_WINDOW = 10
PAST_WINDOW = 50

# Feature Scaling
sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = sc.fit_transform(training_set)
#training_set_scaled = training_set
# Creating a data structure with 60 time-steps and 1 output
X_train = []
y_train = []
for i in range(PAST_WINDOW, len(training_set)):
    X_train.append(training_set_scaled[i-PAST_WINDOW:i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))


# Feature Scaling
test_set_scaled = sc.fit_transform(test_set)
#training_set_scaled = training_set
# Creating a data structure with 60 time-steps and 1 output
X_test = []
y_test = []
for i in range(PAST_WINDOW, len(test_set)):
    X_test.append(test_set_scaled[i-PAST_WINDOW:i, 0])
    y_test.append(test_set_scaled[i, 0])
X_test, y_test = np.array(X_test), np.array(y_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))



model = Sequential()
#Adding the first LSTM layer and some Dropout regularisation
model.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
model.add(Dropout(0.2))
# Adding a second LSTM layer and some Dropout regularisation
model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.2))
# Adding a third LSTM layer and some Dropout regularisation
model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.2))
# Adding a fourth LSTM layer and some Dropout regularisation
model.add(LSTM(units = 50))
model.add(Dropout(0.2))
# Adding the output layer
model.add(Dense(units = 1))

# Compiling the RNN
model.compile(optimizer = 'adam', loss = 'mean_squared_error')

# Fitting the RNN to the Training set
model.fit(X_train, y_train, epochs = 20, batch_size = 32, validation_data = (X_test, y_test))

# Getting the predicted stock price of 2017
dataset_train = df.iloc[:len(training_set), 6:7]
dataset_test = df.iloc[len(training_set):, 6:7]
dataset_total = pd.concat((dataset_train, dataset_test), axis = 0)
inputs = dataset_total[len(dataset_total) - len(dataset_test) - PAST_WINDOW:].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)
X_test = []
for i in range(PAST_WINDOW, len(test_set)):
    X_test.append(inputs[i-PAST_WINDOW:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
print(X_test.shape)
# (459, 60, 1)

predicted_weather = model.predict(X_test)
predicted_weather = sc.inverse_transform(predicted_weather)

# Visualising the results
plt.figure(figsize=(12,4))
plt.plot(dataset_test.values, color = "red", label = "Real weather")
plt.plot(predicted_weather, color = "blue", label = "Predicted weather")
plt.xticks(np.arange(0,len(test_set),100))
plt.title('Weather Prediction')
plt.xlabel('Time')
plt.ylabel('Actual Weather')
plt.legend()
plt.show()