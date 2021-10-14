from django.conf import settings

from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import json

import logging
logger = logging.getLogger(__name__)

myGlobalMessagePayload = "Sensor not avaible"

def get_influxdb_client():
    """Returns an ``InfluxDBClient`` instance."""
    client = InfluxDBClient(
        settings.INFLUXDB_ADDRESS,
        settings.INFLUXDB_PORT,
        settings.INFLUXDB_USERNAME,
        settings.INFLUXDB_PASSWORD,
        settings.INFLUXDB_DATABASE,
    )
    return client

def init_MQTT_client(sensor_id):
    mqtt_client = mqtt.Client(client_id=sensor_id)
    mqtt_client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(settings.MQTT_ADDRESS, 1883)

    return mqtt_client

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))

def on_message(client, userdata, msg):
    global myGlobalMessagePayload
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    myGlobalMessagePayload = json.loads(msg.payload)
    print(myGlobalMessagePayload)