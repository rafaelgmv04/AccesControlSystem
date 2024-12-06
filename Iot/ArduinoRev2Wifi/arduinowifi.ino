#include <WiFiNINA.h>
#include <Servo.h>
#include <SPI.h>


const char* ssid = "SSID";
const char* password = "PASSWORD";


#define ESP32_RX_PIN 0  // RX PIN of Arduino connected to ESP32-CAM TX PIN
#define ESP32_TX_PIN 1  // TX PIN of Arduino connected to ESP32-CAM RX PIN


const int port = 80;


#define pot A0
#define pinServo 10
Servo servo1;
const int pinled = 12;
const int trig = 7;
const int echo = 6;
bool closed = true;
bool someoneHere = false;
bool opening = false;

WiFiServer server(port);

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  pinMode(echo, INPUT);
  pinMode(trig, OUTPUT);
  pinMode(pinled, OUTPUT);
  pinMode(pot, INPUT);
  servo1.attach(pinServo);
  servo1.write(0);


  connectToWiFi();


  server.begin();
  Serial.println("Server iniciated.");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("New client connected.");
    String request = "";
    while (client.available()) {
      char c = client.read();
      request += c;
    }

    Serial.println("Request:");
    Serial.println(request);

    // proccess the request
    if (request.startsWith("POST /commandGate")) {
      processRequest(request);
    }


    client.stop();
    Serial.println("Client disconnected.");
  }

  // verify if someone is near the gate if it is not opening
  if (!opening) {
    if (readSensor()) {
      Serial.println("Sensor detected someone.");
    }
  }
}

void processRequest(const String& request) {

  int bodyIndex = request.indexOf("\r\n\r\n");
  String message = "";
  if (bodyIndex >= 0) {
    message = request.substring(bodyIndex + 4); // extract the message from the request jumping the header
  }
  message.trim();


  if (message.equals("open")) {
    Serial.println("'open' command recongnized. Authorized");
    openGate();
  } else if (message.equals("denied")) {
    Serial.println(" 'denied' command recongnized. Not authorized.");
    digitalWrite(pinled, HIGH);
    delay(3000);
    digitalWrite(pinled, LOW);
    opening = false;
  } else {
    Serial.println("Command not recongnized.");
    digitalWrite(pinled, HIGH);
    delay(3000);
    digitalWrite(pinled, LOW);
  }
}

bool readSensor() {
  // Sensor ultrassônico
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long time = pulseIn(echo, HIGH);
  long cm = time / 58;

  int pot_value = map(analogRead(pot), 0, 1023, 0, 20);
  Serial.print("Configurated distance: ");
  Serial.println(pot_value);
  Serial.print("Mesure: ");
  Serial.println(cm);

  if (cm <= pot_value && cm != 0) {
    someoneHere = true;
    if (closed) {
      Serial.println("Photo taken.");
      Serial1.println("C"); // send a command to ESP32-CAM to take a photo
      opening = true;
    }
  } else {
    someoneHere = false;
  }

  return someoneHere;
}

void openGate() {
  closed = false;
  servo1.write(180);
  Serial.println("Gate opened");
  delay(5000);

  while (readSensor()) {
    delay(1000);
    Serial.println("waiting for car to leave...");
  }

  servo1.write(0);
  Serial.println("Gate closed");
  closed = true;
  opening = false;
}

void connectToWiFi() {
  Serial.print("WiFi connecting to");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}
