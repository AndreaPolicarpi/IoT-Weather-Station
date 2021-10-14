from django.urls import path

from . import views
import re


urlpatterns = [
    # ex: /webapp/
    path('', views.index, name='index'),
    # ex: /webapp/addSensor
    path('addsensor', views.add_sensor, name='addsensor'),
    path('missingsensor/<str:sensor_id>', views.missing_sensor, name='missingsensor'),
    path('<str:sensor_id>/<str:changes>/<str:change_value>', views.change_sensor_parameter, name='changes'),
    # ex: /polls/ID1
    path('<str:sensor_id>/', views.sensor_info, name='info'),
]