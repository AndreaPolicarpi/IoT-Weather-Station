import pandas as pd
import numpy as np
import random
import ast
from time import sleep
import datetime as dt

from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt

import csv 

file_name = "data/data.csv"
df = pd.read_csv(file_name, encoding='UTF-16 LE')
df['index'] = df.index
print("Number of rows and columns:", df.shape)

#INFLUXDB_ADDRESS = "192.168.1.71"
INFLUXDB_ADDRESS = "192.168.180.248"
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'weather_stations'

#MQTT_ADDRESS = "192.168.1.71"
MQTT_ADDRESS = "192.168.180.248"
MQTT_USER = 'nico'
MQTT_PASSWORD = 'psw'
MQTT_CLIENT_ID = "client"

sensor_id = "BolognaSensor"

INIT_FREQ = 1000

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))

mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect

mqtt_client.connect(MQTT_ADDRESS, 1883)

influxdb_client = InfluxDBClient(
    INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)




def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

_init_influxdb_database()


def choose_best_action(table,state):
  for action in table.columns:
    if table.loc[state,action] == max(table.loc[state]):
      return action

############################################################

def epsilon_greedy_action(table,state,epsilon = 0.1):
  seed = random.uniform(0,1)
  if seed < epsilon:
    return random.sample(set(Qtable.columns),1)[0]
  else:
    return choose_best_action(table,state)

############################################################

def state_transition(state,action):
    newstate = ast.literal_eval(state)
    x = newstate[0]
    y = newstate[1]

    if action == '+SR':
      return '[{},{}]'.format(x,max(y//2,250))

    elif action == '=SR':
      return state

    elif action == '-SR':
      return '[{},{}]'.format(x,min(y*2,1000))

    else:
      print('Wrong action')
      return state

############################################################

def update_state_based_on_quality(state,quality_error,th=0.2):

   newstate = ast.literal_eval(state)
   x = newstate[0]
   y = newstate[1]

   if quality_error > th:
     q = 0
   elif quality_error <= th and quality_error >= th/2:
     q = 1
   else:
     q = 2

   return '[{},{}]'.format(q,y) 

############################################################

def compute_reward(state):

   SR_0 = 250
   list_state = ast.literal_eval(state)
   q = list_state[0]
   SR = list_state[1]

   if q == 0:
     k = -1
   elif q == 1:
     k = 1.5
   else:
     k = 1

   return k*(SR//SR_0)

############################################################

def update_prev_Qtable_cell(Qtable,state,action,learning_rate=0.9,discount_factor=0.2):

  future_state = state_transition(state,action)

  contr1 = (1-learning_rate)*Qtable.loc[state,action]

  contr2 = learning_rate*compute_reward(future_state)

  contr3 = learning_rate*discount_factor*max([ Qtable.loc[future_state,future_action] for future_action in actions])

  return contr1 + contr2 + contr3

def train_on_measurement(curr_state, Qtable,curr_obs,prev_obs, epsilon=0.1,learning_rate=0.9,discount_factor=0.2,th=0.2 ):

  newstate = update_state_based_on_quality(curr_state,curr_obs,prev_obs,th)

  chosen_action = epsilon_greedy_action(Qtable,newstate,epsilon)

  Qtable.loc[newstate,chosen_action] = update_prev_Qtable_cell(Qtable,newstate,chosen_action,learning_rate,discount_factor)

  final_state = state_transition(newstate,chosen_action)

  return Qtable, final_state

states = [
          '[0,250]','[1,250]','[2,250]',
          '[0,500]','[1,500]','[2,500]',
          '[0,1000]','[1,1000]','[2,1000]'
          ]

      
actions = ['+SR','=SR','-SR']

Qtable = pd.DataFrame(data=0, index=states, columns=actions)

state = '[0,{}]'.format(INIT_FREQ)

EPOCHS = 500
lr = 0.9
disc_fact = 0.3
OBSERVATION_TIME = dt.timedelta(minutes=5)


for i in range(EPOCHS):

    values = influxdb_client.query("SELECT time, id, temperature, humidity FROM quanto ORDER BY desc LIMIT 2")

    list_values = []

    points = values.get_points()
    for point in points:
        list_values.append(point)

    df = pd.DataFrame(list_values, columns=[
                    'time', 'id', 'temperature', 'humidity'])

    df = df.sort_values("time", ascending=True, ignore_index=True)
    
    temp_before = df.iloc[0, 2]
    temp_after= df.iloc[1, 2]
    hum_before = df.iloc[0, 3]
    hum_after= df.iloc[1, 3]

    quality = np.abs(temp_after-temp_before) + np.abs(hum_after-hum_before)

    state = update_state_based_on_quality(state, quality)

    chosen_action = epsilon_greedy_action(Qtable, state, epsilon=0.2)

    new_state = state_transition(state, chosen_action)

    Qtable.loc[state, chosen_action] = update_prev_Qtable_cell(Qtable, state, chosen_action, learning_rate=lr, discount_factor= disc_fact)

    state = new_state

    print("TRAINING PHASE [{}/{}]: ".format(i, EPOCHS), state)
    mqtt_client.publish(sensor_id+"/freq", ast.literal_eval(state)[1])
    sleep(ast.literal_eval(state)[1]/1000)


counter_250ms = 0
counter_500ms = 0
counter_1000ms = 0

counter_state_zero = 0

DONE = False

start_time = dt.datetime.now()


while(True):

    values = influxdb_client.query("SELECT time, id, temperature, humidity FROM quanto WHERE id = \'{}\' ORDER BY desc LIMIT 2".format(sensor_id))

    list_values = []

    points = values.get_points()
    for point in points:
        list_values.append(point)

    df = pd.DataFrame(list_values, columns=[
                    'time', 'id', 'temperature', 'humidity'])

    df = df.sort_values("time", ascending=True, ignore_index=True)
    
    temp_before = df.iloc[0, 2]
    temp_after= df.iloc[1, 2]
    hum_before = df.iloc[0, 3]
    hum_after= df.iloc[1, 3]

    quality = np.abs(temp_after-temp_before) + np.abs(hum_after-hum_before)

    state = update_state_based_on_quality(state, quality)

    chosen_action = choose_best_action(Qtable, state)

    state = state_transition(state, chosen_action)

    if ast.literal_eval(state)[1] == 250:
      counter_250ms += 1
    if ast.literal_eval(state)[1] == 500:
      counter_500ms += 1
    if ast.literal_eval(state)[1] == 1000:
      counter_1000ms += 1

    if ast.literal_eval(state)[0] == 0:
      counter_state_zero += 1

    if (dt.datetime.now() - start_time) > OBSERVATION_TIME and DONE == False:

      saved_tr = (counter_250ms*4 + counter_500ms*2 + counter_1000ms)/(OBSERVATION_TIME.total_seconds()*4)

      total_state_counter = counter_250ms + counter_500ms + counter_1000ms
      degradation = counter_state_zero / total_state_counter

      data = [saved_tr, degradation, lr, disc_fact, OBSERVATION_TIME]
      with open('RL_evaluations.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)
        
      DONE = True
      

    print("RUNNING STATE: ", state)
    mqtt_client.publish(sensor_id+"/freq", ast.literal_eval(state)[1])
    sleep(ast.literal_eval(state)[1]/1000)