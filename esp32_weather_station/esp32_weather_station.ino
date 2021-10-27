
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
const char* mqttServer = "192.168.180.248";

const int mqttPort = 1883;
const char* mqttUser = "nico";
const char* mqttPassword = "psw";
const char* clientID = "BolognaSensor"; // MQTT client

float MIN_TEMP = 25.0;
float MAX_TEMP = 35.0;
float MIN_HUM = 40.0;
float MAX_HUM = 60.0;

String ID = clientID;
String gps_coord = "44.500, 11.344";

const char* maxtemp_topic = "BolognaSensor/max_temp";
const char* mintemp_topic = "BolognaSensor/min_temp";
const char* maxhum_topic = "BolognaSensor/max_hum";
const char* minhum_topic = "BolognaSensor/min_hum";
const char* freq_topic = "BolognaSensor/freq";
const char* check_topic = "BolognaSensor/check";
const char* feedback_topic = "BolognaSensor/feedback";



//#####################################################################

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
//PubSubClient client(mqtt_server, 1883, wifiClient);
PubSubClient client(wifiClient);

//#####################################################################

void callback(char* topic, byte* payload, unsigned int length) {
  long startTime = millis();
  Serial.println("############## SONO DENTRO ##############");
  char buff[length];
  int i;
  for (i = 0; i < length; i++)
  {
    buff[i] = payload[i];
  }
  buff[i] = '\0';
  const char *p_payload = buff;


  if ( String(topic) == check_topic ) {
    Serial.print("#######IF ESTERNO#######");

    StaticJsonDocument<256> doc2;
    doc2["maxtemp"] = MAX_TEMP;
    doc2["mintemp"] = MIN_TEMP;
    doc2["maxhum"] = MAX_HUM;
    doc2["minhum"] = MIN_HUM;
    doc2["freq"] = SAMPLE_FREQ;

    char out[128];
    int b = serializeJson(doc2, out);
    Serial.print("changes bytes = ");
    Serial.println(b, DEC);

    if (client.publish(feedback_topic, out)) {
      Serial.println("feedback sent!");
    }
  }


  if ( String(topic) == mintemp_topic ) {
    float got_float = atof(p_payload);
    MIN_TEMP = got_float;
    Serial.print("MIN_TEMP changed: ");
    Serial.println(MIN_TEMP);
  }

  if ( String(topic) == maxtemp_topic ) {
    float got_float = atof(p_payload);
    MAX_TEMP = got_float;
    Serial.print("MAX_TEMP changed: ");
    Serial.println(MAX_TEMP);
  }

  if ( String(topic) == minhum_topic ) {
    float got_float = atof(p_payload);
    MIN_HUM = got_float;
    Serial.print("MIN_HUM changed: ");
    Serial.println(MIN_HUM);
  }

  if ( String(topic) == maxhum_topic ) {
    float got_float = atof(p_payload);
    MAX_HUM = got_float;
    Serial.print("MAX_HUM changed: ");
    Serial.println(MAX_HUM);
  }

  if ( String(topic) == freq_topic ) {
    int got_int = atoi(p_payload);
    SAMPLE_FREQ = got_int;
    Serial.print("SAMPLE_FREQ changed: ");
    Serial.println(SAMPLE_FREQ);
  }

  long deltaTime = millis() - startTime;
  Serial.println("TEMPO DI RICEVIMENTO: ");
  Serial.println(deltaTime);
}

// Custom function to connect to the MQTT broker via WiFi
void connect_MQTT() {
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

  client.subscribe(mintemp_topic);
  client.subscribe(maxtemp_topic);
  client.subscribe(minhum_topic);
  client.subscribe(maxhum_topic);
  client.subscribe(freq_topic);
  client.subscribe(check_topic);
}

//#####################################################################

// Create AsyncWebServer object on port 80

float readDHTTemperature() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
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
    return h;
  }
}

//#######################################################################################


void setup() {

  pinMode(ledPin, OUTPUT);

  // Serial port for debugging purposes
  Serial.begin(115200);

  dht.begin();

  connect_MQTT();
}

void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    connect_MQTT();
  }

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
  Serial.print("SAMPLE_FREQ ATTUALE: ");
  Serial.println(SAMPLE_FREQ);

  if ( t < MIN_TEMP || t > MAX_TEMP || h < MIN_HUM || h > MAX_HUM ) {
    if ( t < MIN_TEMP || t > MAX_TEMP) {
      digitalWrite(ledPin, HIGH);
      Serial.println("----EXCEPTION MAX/MIN TEMPERATURE----");
    }
    if ( h < MIN_HUM || h > MAX_HUM ) {
      digitalWrite(ledPin, HIGH);
      Serial.println("----EXCEPTION MAX/MIN HUMIDITY----");
    }
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("---- NO EXCEPTION MAX/MIN----");
  }

  // MQTT can only transmit strings
  String hs = "Hum: " + String((float)h) + " % ";
  String ts = "Temp: " + String((float)t) + " C ";

  StaticJsonDocument<256> doc;
  doc["gps"] = gps_coord;
  doc["id"] = ID;
  doc["strength"] = strength;
  doc["temperature"] = t;
  doc["humidity"] = h;

  char out[128];
  int b = serializeJson(doc, out);
  Serial.print("bytes = ");
  Serial.println(b, DEC);

  if (client.publish("quanto", out)) {
    Serial.println("data sent!");
  }

  // client.disconnect();  // disconnect from the MQTT broker

  Serial.println("------------------------------------------------------------------------");
  delay(SAMPLE_FREQ);
}
