#include <DHT.h>

const int DHT_PIN = 4;
const int DHT_TYPE = DHT22;

const int TEMP_GREEN = 16;
const int TEMP_YELLOW = 17;
const int TEMP_RED = 18;

const int HUMID_GREEN = 19;
const int HUMID_YELLOW = 21;
const int HUMID_RED = 22;

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(TEMP_GREEN, OUTPUT);
  pinMode(TEMP_YELLOW, OUTPUT);
  pinMode(TEMP_RED, OUTPUT);
  pinMode(HUMID_GREEN, OUTPUT);
  pinMode(HUMID_YELLOW, OUTPUT);
  pinMode(HUMID_RED, OUTPUT);
}

void setStatusLeds(float value, float goodMin, float goodMax,
                  float warningMin, float warningMax,
                  int greenLed, int yellowLed, int redLed) {
  digitalWrite(greenLed, LOW);
  digitalWrite(yellowLed, LOW);
  digitalWrite(redLed, LOW);

  if (value >= goodMin && value <= goodMax) {
    digitalWrite(greenLed, HIGH);
  } else if (value >= warningMin && value <= warningMax) {
    digitalWrite(yellowLed, HIGH);
  } else {
    digitalWrite(redLed, HIGH);
  }
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Could not read the DHT22 sensor.");
    delay(2000);
    return;
  }

  // Comfortable indoor ranges: temperature 18-26 C, humidity 30-60%.
  setStatusLeds(temperature, 18, 26, 15, 30,
                TEMP_GREEN, TEMP_YELLOW, TEMP_RED);
  setStatusLeds(humidity, 30, 60, 20, 70,
                HUMID_GREEN, HUMID_YELLOW, HUMID_RED);

  Serial.print("Temperature: ");
  Serial.print(temperature, 1);
  Serial.print(" C | Humidity: ");
  Serial.print(humidity, 1);
  Serial.println(" %");

  delay(2000);
}
