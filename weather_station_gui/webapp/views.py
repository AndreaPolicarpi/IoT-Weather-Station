from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    pass
    #query che restituisce gli unique ID con relativa posizione gps
    return HttpResponse(data_list)

def sensor_info(request, id_sensor):
    #query che restituisce le rows del sensore preso in esame
    return HttpResponse(info_Sensor)

def add_sensor(request):
    pass
    # metodo per aggiungere un nuovo sensore alla rete

def change_sensor_parameter(request, id_sensor, changes):
    pass
    # metodo per modificare i parametri di uno specifico sensore