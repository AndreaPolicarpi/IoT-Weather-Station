from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from . import utils
from django.template import loader
import json
from .models import Sensor
import time
from django.conf import settings

import paho.mqtt.subscribe as subscribe

def index(request, err = False):

    influxdb_client = utils.InfluxDBClient()
    id_values = influxdb_client.query('SHOW TAG VALUES  FROM "quanto" WITH KEY = "id"', database="weather_stations")
    list_id_values = []

    valid_sensor = list(Sensor.objects.all())
    valid_id = [s.sensor_id for s in valid_sensor]

    points = id_values.get_points()
    for point in points:
        if point['value'] in valid_id:
            location_res = influxdb_client.query('SHOW TAG VALUES  FROM "quanto" WITH KEY = "gps" where id = \'{}\''.format(point['value']), database="weather_stations")
            location = list(location_res.get_points())[0]['value'].replace(" ", "")
            point['lat'] = location.split(",")[0]
            point['long'] = location.split(",")[1]
            list_id_values.append(point)

    template = loader.get_template('webapp/index.html')
    context = {
        'list_id_values': list_id_values,
        'jsondata': json.dumps(list_id_values),
    }
    if err == True:
        context['error_message'] = "The ID of the new sensor is invalid."
    else:
        context['error_message'] = None

    print(context)

    return HttpResponse(template.render(context, request))

def sensor_info(request, sensor_id):
    #query che restituisce le rows del sensore preso in esame

    influxdb_client = utils.InfluxDBClient()
    mqtt_client = utils.init_MQTT_client(sensor_id)
    quanto_results = influxdb_client.query('SELECT * FROM quanto WHERE time >= now() - 5m AND "id" =\'{}\''.format(sensor_id), database="weather_stations")
    list_quanto = []

    points = quanto_results.get_points()
    for point in points:
        list_quanto.append(point)


    mqtt_client.loop_start() #start loop to process received messages
    print("subscribing ")
    mqtt_client.subscribe(sensor_id+"/feedback")#subscribe
    time.sleep(2)
    print("publishing ")
    mqtt_client.publish(sensor_id+"/check", "nodata")
    time.sleep(4)
    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop

    payload = utils.myGlobalMessagePayload
    utils.myGlobalMessagePayload = "Sensor not avaible"

    if payload == "Sensor not avaible":
        return HttpResponseRedirect(reverse("missingsensor", args=(sensor_id,)))

    template = loader.get_template('webapp/sensor_info.html')
    context = {
        'list_quanto': list_quanto,
        'jsondata': json.dumps(list_quanto),
        'payload': payload
        }   

    return HttpResponse(template.render(context, request))

def add_sensor(request):
    try:
        sensor = Sensor(sensor_id= request.POST['sensorID'])
        sensor.save()
        return redirect('index')
    except:
        return index(request, err=True)

def missing_sensor(request, sensor_id):

    template = loader.get_template('webapp/missing_sensor.html')
    context = {
        'sensor_id': sensor_id,
    }
    return HttpResponse(template.render(context, request))

def change_sensor_parameter(request, sensor_id, changes, change_value):

    print("####################   "+change_value+"    ##################################")

    mqtt_client = utils.init_MQTT_client(sensor_id)

    if changes == 'maxtemp':
        mqtt_client.publish(sensor_id+"/max_temp", change_value)
        time.sleep(1.5)

    if changes == 'mintemp':
        mqtt_client.publish(sensor_id+"/min_temp", change_value)
        time.sleep(1.5)

    if changes == 'maxhum':
        mqtt_client.publish(sensor_id+"/max_hum", change_value)
        time.sleep(1.5)

    if changes == 'minhum':
        mqtt_client.publish(sensor_id+"/min_hum", change_value)
        time.sleep(1.5)

    if changes == 'sampling':
        mqtt_client.publish(sensor_id+"/freq", change_value)
        time.sleep(1.5)


    mqtt_client.disconnect()
    return HttpResponseRedirect(reverse("info", args=(sensor_id,)))