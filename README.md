# IoT-Weather-Station

Proof-of-concept of an IoT weather station pipeline. The system is composed of:

1) End devices: DHT22 temp/hum sensors connected to an ESP32;

2) MQTT Broker (Mosquitto), acting as a data bridge between ESP32 and database;

3) Data management system, represented by Influx and Grafana tools;

4) Data analytics, in charge of forecasting temperature and humidity by a LSTM, based on previous observations;

5) Reinforcement learning application, which aims to self-adjust the sampling rate of the sensor on the base of the measurements quality.
