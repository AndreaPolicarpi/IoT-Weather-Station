
// Import required libraries
#include "WiFi.h" // Enables the ESP32 to connect to the local network (via WiFi)
#include "PubSubClient.h" // Connect and publish to the MQTT broker
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <DHT.h>



int SAMPLE_FREQ = 1000;     // Sample Frequency

#define DHTPIN 27     // Digital pin connected to the DHT sensor
#define DHTTYPE    DHT22     // DHT 22 (AM2302)

int ledPin = 13;

//#######################################################################################
//#######################################################################################
//#######################################################################################

DHT dht(DHTPIN, DHTTYPE);

//#####################################################################

// network credentials

const char* ssid = "Redmi";
const char* password = "Nicola123";

// MQTT
const char* mqttServer = "192.168.252.248";
const int mqttPort = 1883;
const char* mqttUser = "nico";
const char* mqttPassword = "psw";
const char* humidity_topic = "home/livingroom/humidity";
const char* temperature_topic = "home/livingroom/temperature";
const char* gps_topic = "gps";
const char* id_topic = "id";
const char* strength_topic = "strength";
const char* clientID = "client_livingroom"; // MQTT client

float MIN_TEMP = 25.0;
float MAX_TEMP = 35.0;
float MIN_HUM = 40.0;
float MAX_HUM = 60.0;

String ID = "ID1";
String gps_coord = "41 53 25.36 - 12 29 32.70";


//#####################################################################

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
//PubSubClient client(mqtt_server, 1883, wifiClient);
PubSubClient client(wifiClient);

//#####################################################################

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println("############## SONO DENTRO ##############"); 
  char buff[length];
  int i;
  for (i = 0; i<length; i++) 
  {
    buff[i] = payload[i];
  }
  buff[i] = '\0';
  const char *p_payload = buff;
  
  float got_float = atof(p_payload);
    
  if ( String(topic) == "min_temp" ) {
    MIN_TEMP = got_float;
    Serial.print("MIN_TEMP changed: ");
    Serial.println(MIN_TEMP);   
  }
  
  if ( String(topic) == "max_temp" ) {
  MAX_TEMP = got_float;
  Serial.print("MAX_TEMP changed: ");
  Serial.println(MAX_TEMP);   
  }
  
  if ( String(topic) == "min_hum" ) {
  MIN_HUM = got_float;
  Serial.print("MIN_HUM changed: ");
  Serial.println(MIN_HUM);   
  }
  
  if ( String(topic) == "max_hum" ) {
  MAX_HUM = got_float;
  Serial.print("MAX_HUM changed: ");
  Serial.println(MAX_HUM);   
  }
}

// Custom function to connect to the MQTT broker via WiFi
void connect_MQTT(){
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");
 
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
 
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
 
    if (client.connect("ESP32Client", mqttUser, mqttPassword )) {
 
      Serial.println("connected");  
 
    } else {
 
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
 
    }
  }
 
  client.subscribe("min_temp");
  client.subscribe("max_temp");
  client.subscribe("min_hum");
  client.subscribe("max_hum");
}

//#####################################################################

// Create AsyncWebServer object on port 80

float readDHTTemperature() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  //float t = dht.readTemperature(true);
  // Check if any reads failed and exit early (to try again).
  if (isnan(t)) {    
    Serial.println("Failed to read from DHT sensor!");
    return 0.0;
  }
  else {
    //Serial.println(t);
    return t;
  }
}

float readDHTHumidity() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  if (isnan(h)) {
    Serial.println("Failed to read from DHT sensor!");
    return 0.0;
  }
  else {
    //Serial.println(h);
    return h;
  }
}

//#######################################################################################


void setup(){

  pinMode(ledPin, OUTPUT);   

  // Serial port for debugging purposes
  Serial.begin(115200);

  dht.begin();

  connect_MQTT();
}

void loop(){

  client.loop();  //listener for the callback
  
  float t = readDHTTemperature();
  float h = readDHTHumidity();
  long strength = WiFi.RSSI();

  Serial.println("----");
  Serial.println("Temperature: " + String(t));
  Serial.println("Humidity: " + String(h));
  Serial.println("Strength signal: " + String(strength));
  Serial.println("----");

    Serial.print("MIN_TEMP ATTUALE: ");
    Serial.println(MIN_TEMP); 
    Serial.print("MAX_TEMP ATTUALE: ");
    Serial.println(MAX_TEMP);
    Serial.print("MIN_HUM ATTUALE: ");
    Serial.println(MIN_HUM); 
    Serial.print("MAX_HUM ATTUALE: ");
    Serial.println(MAX_HUM);

  if ( t < MIN_TEMP || t > MAX_TEMP || h < MIN_HUM || h > MAX_HUM ){
    if ( t < MIN_TEMP || t > MAX_TEMP){
      digitalWrite(ledPin, HIGH);
      Serial.println("----EXCEPTION MAX/MIN TEMPERATURE----");
    }
    if ( h < MIN_HUM || h > MAX_HUM ){
      digitalWrite(ledPin, HIGH);
      Serial.println("----EXCEPTION MAX/MIN HUMIDITY----");
    }
  } else {
      digitalWrite(ledPin, LOW);
      Serial.println("---- NO EXCEPTION MAX/MIN----");
  }

  // MQTT can only transmit strings
  String hs="Hum: "+String((float)h)+" % ";
  String ts="Temp: "+String((float)t)+" C ";

  
  
//   // PUBLISH to the MQTT Broker (topic = Temperature, defined at the beginning)
//  if (client.publish(temperature_topic, String(t).c_str())) {
//    Serial.println("Temperature sent!");
//  }
//
//
//  // PUBLISH to the MQTT Broker (topic = Humidity, defined at the beginning)
//  if (client.publish(humidity_topic, String(h).c_str())) {
//    Serial.println("Humidity sent!");
//  }
//
//  // PUBLISH to the MQTT Broker (topic = gps, defined at the beginning)
//  if (client.publish(gps_topic, gps_coord.c_str())) {
//    Serial.println("GPS Coordinate sent!");
//  }
//
//  
//  // PUBLISH to the MQTT Broker (topic = id, defined at the beginning)
//  if (client.publish(id_topic, ID.c_str())) {
//    Serial.println("ID sent!");
//  }
//
//  // PUBLISH to the MQTT Broker (topic = strength, defined at the beginning)
//  if (client.publish(strength_topic, String(strength).c_str())) {
//    Serial.println("Strength sent!");
//  }

  StaticJsonDocument<256> doc;
  doc["gps"] = gps_coord;
  doc["id"] = ID;
  doc["strength"] = strength;
  doc["temperature"] = t;
  doc["humidity"] = h;

  char out[128];
  int b =serializeJson(doc, out);
  Serial.print("bytes = ");
  Serial.println(b,DEC);
  
  if (client.publish("quanto", out)) {
   Serial.println("data sent!");
  }

   // client.disconnect();  // disconnect from the MQTT broker

  Serial.println("------------------------------------------------------------------------");
  delay(SAMPLE_FREQ);
}
