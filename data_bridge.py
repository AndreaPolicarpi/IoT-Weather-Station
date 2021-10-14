import re
from typing import NamedTuple
import json

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

#INFLUXDB_ADDRESS = "192.168.1.71"
INFLUXDB_ADDRESS = "192.168.200.248"
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'weather_stations'

#MQTT_ADDRESS = "192.168.1.71"
MQTT_ADDRESS = "192.168.200.248"
MQTT_PORT = 1883
MQTT_USER = 'nico'
MQTT_PASSWORD = 'psw'

MQTT_CLIENT_ID = 'ClientAdmin'
MQTT_TOPIC = "quanto"

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

def _send_sensor_data_to_influxdb(sensor_data):
    json_body = [
        {
            "measurement": "quanto",
            'tags': {
                'gps': sensor_data["gps"],
                'id': sensor_data["id"]
            },
            'fields': {
                'strength': sensor_data["strength"],
                'temperature': float(sensor_data["temperature"]),
                'humidity': float(sensor_data["humidity"])
            }
        }
    ]
    influxdb_client.write_points(json_body)
    
def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    sensor_data = json.loads(msg.payload)
    print("sensor_data")

    if sensor_data is not None:
        _send_sensor_data_to_influxdb(sensor_data)

def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, MQTT_PORT)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()