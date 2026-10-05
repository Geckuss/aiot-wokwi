#include <DHT.h>
#include <math.h>
#include "model_data.h"

const int DHT_PIN = 4;
const int DHT_TYPE = DHT22;

const int TEMP_GREEN = 16;
const int TEMP_YELLOW = 17;
const int TEMP_RED = 18;

const int HUMID_GREEN = 19;
const int HUMID_YELLOW = 21;
const int HUMID_RED = 22;

unsigned int sampleRateSeconds = 5;
const unsigned long STATUS_DISPLAY_TIME_MS = 500;
const char* datasetLabel = "inference";

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

  Serial.println("sample_ms,temperature_c,humidity_percent,label");
}

void turnOffAllLeds() {
  digitalWrite(TEMP_GREEN, LOW);
  digitalWrite(TEMP_YELLOW, LOW);
  digitalWrite(TEMP_RED, LOW);
  digitalWrite(HUMID_GREEN, LOW);
  digitalWrite(HUMID_YELLOW, LOW);
  digitalWrite(HUMID_RED, LOW);
}

int predictCondition(float temperature, float humidity, float* confidence) {
  float inputs[MODEL_INPUTS] = {
    (temperature - NORMALIZATION_MEANS[0]) / NORMALIZATION_SCALES[0],
    (humidity - NORMALIZATION_MEANS[1]) / NORMALIZATION_SCALES[1]
  };
  float hidden[MODEL_HIDDEN_UNITS];

  for (int unit = 0; unit < MODEL_HIDDEN_UNITS; unit++) {
    float value = HIDDEN_BIAS[unit];
    for (int input = 0; input < MODEL_INPUTS; input++) {
      value += inputs[input] * HIDDEN_WEIGHTS[unit][input];
    }
    hidden[unit] = value > 0 ? value : 0;
  }

  float logits[MODEL_OUTPUTS];
  float sumExp = 0;
  for (int output = 0; output < MODEL_OUTPUTS; output++) {
    logits[output] = OUTPUT_BIAS[output];
    for (int unit = 0; unit < MODEL_HIDDEN_UNITS; unit++) {
      logits[output] += hidden[unit] * OUTPUT_WEIGHTS[output][unit];
    }
    sumExp += exp(logits[output]);
  }

  int bestOutput = 0;
  *confidence = 0;
  for (int output = 0; output < MODEL_OUTPUTS; output++) {
    float probability = exp(logits[output]) / sumExp;
    if (probability > *confidence) {
      *confidence = probability;
      bestOutput = output;
    }
  }
  return bestOutput;
}

void showPrediction(int condition) {
  turnOffAllLeds();
  int greenLed = condition == 0 ? HIGH : LOW;
  int yellowLed = condition == 1 ? HIGH : LOW;
  int redLed = condition == 2 ? HIGH : LOW;

  digitalWrite(TEMP_GREEN, greenLed);
  digitalWrite(TEMP_YELLOW, yellowLed);
  digitalWrite(TEMP_RED, redLed);
  digitalWrite(HUMID_GREEN, greenLed);
  digitalWrite(HUMID_YELLOW, yellowLed);
  digitalWrite(HUMID_RED, redLed);
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Could not read the DHT22 sensor.");
    turnOffAllLeds();
    delay(sampleRateSeconds * 1000UL);
    return;
  }

  float confidence;
  int condition = predictCondition(temperature, humidity, &confidence);
  showPrediction(condition);

  Serial.print("Temperature: ");
  Serial.print(temperature, 1);
  Serial.print(" C | Humidity: ");
  Serial.print(humidity, 1);
  Serial.println(" %");
  Serial.print("AI prediction: ");
  Serial.print(MODEL_LABELS[condition]);
  Serial.print(" (confidence ");
  Serial.print(confidence * 100, 1);
  Serial.println("%)");

  Serial.print(millis());
  Serial.print(",");
  Serial.print(temperature, 2);
  Serial.print(",");
  Serial.print(humidity, 2);
  Serial.print(",");
  Serial.println(datasetLabel);

  // Keep the status visible briefly, then turn LEDs off while waiting.
  delay(STATUS_DISPLAY_TIME_MS);
  turnOffAllLeds();

  unsigned long sampleIntervalMs = sampleRateSeconds * 1000UL;
  if (sampleIntervalMs > STATUS_DISPLAY_TIME_MS) {
    delay(sampleIntervalMs - STATUS_DISPLAY_TIME_MS);
  }
}
