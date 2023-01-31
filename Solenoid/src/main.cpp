#include <Arduino.h>
#include <SPI.h>
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char *ssid = "MatchManager";   //  Wireless SSID/Password
const char *password = "MatchManagerPW";
const char *mqtt_server = "192.168.4.1";   //  MQTT Broker IP address

const char *MQTT_client_ID = "solenoidClient";
const char *solenoid_status = "solenoid_status";

const int solenoidPin = 2;   // Solenoid Pin

void setup_wifi()
{
  delay(10);
  // Start by connecting to a WiFi network
  Serial.print("Connecting to ");
  Serial.print(ssid);
  Serial.print(".");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.print("");
  Serial.print("WiFi connected. ");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

//
// MQTT callback that is called whenever a subscribed message is received
//
void callback(char *topic, byte *message, unsigned int length)
{
  String this_message;

  // Unpacking of MQTT Message
  for (int i = 0; i < length; i++)
  {
    this_message += (char)message[i];
  }

  // Only subscribed to one topic so only need to look at the message
  if(this_message == "energize")
     digitalWrite(solenoidPin, HIGH);
  else
    digitalWrite(solenoidPin, LOW);
}

void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(MQTT_client_ID))
    {
      Serial.println("connected");
      // Subscribe
      client.subscribe(solenoid_status);
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  pinMode(solenoidPin, OUTPUT);
}

void loop()
{
  if (!client.connected())
    reconnect();

  client.loop();

}