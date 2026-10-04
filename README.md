# Indoor temperature and humidity monitor

This Wokwi project uses an **ESP32 DevKit v1**, a DHT22 sensor, and six LEDs.
The ESP32 is a good choice for this project because it has built-in Wi-Fi for
future AIoT features, while the first version stays local and easy to understand.

## LED meaning

There are three LEDs for each measurement:

| Measurement | Green | Yellow | Red |
| --- | --- | --- | --- |
| Temperature | 18-26 °C | 15-17 °C or 27-30 °C | below 15 °C or above 30 °C |
| Humidity | 30-60% | 20-29% or 61-70% | below 20% or above 70% |

The DHT22 starts at 22 °C and 45% humidity. In the Wokwi simulator, click the
sensor and change its values to test the yellow and red states.

## Wiring

- DHT22 `VCC` -> ESP32 `3V3`
- DHT22 `GND` -> ESP32 `GND`
- DHT22 `SDA` -> ESP32 GPIO 4
- Temperature LEDs: GPIO 16, 17, 18 through 220 ohm resistors
- Humidity LEDs: GPIO 19, 21, 22 through 220 ohm resistors
- Every LED cathode connects to ESP32 `GND`

Open `diagram.json` in Wokwi and start the simulation. The serial monitor shows
the current readings every `sampleRateSeconds` seconds.

## Collect labelled training data

The sketch also prints CSV rows for a future on-device AI model:

```text
sample_ms,temperature_c,humidity_percent,label
```

Before each recording session, change `datasetLabel` in `sketch.ino` to one
of these labels:

- `comfortable`: temperature 18-26 °C and humidity 30-60%
- `warning`: moderately too cold, hot, dry, or humid
- `poor`: strongly too cold, hot, dry, or humid

In Wokwi, set the DHT22 values to match the label, restart the simulation, and
let it produce at least 30 rows. Copy only the CSV rows from the serial monitor
into a dataset file. Repeat this for all three labels, including several
different values and transitions within each class. Keep the header only once.

For example:

```csv
sample_ms,temperature_c,humidity_percent,label
1000,22.00,45.00,comfortable
6000,22.10,45.20,comfortable
11000,27.50,64.00,warning
16000,32.00,78.00,poor
```

## Train the first small model

Run the standard-library training script from the project folder:

```text
Python train_model.py
```

The script trains a small `2 -> 8 -> 3` neural network:

- Inputs: temperature and humidity
- Hidden layer: 8 ReLU units
- Outputs: `comfortable`, `warning`, and `poor`

It uses a deterministic stratified test split and stores the fitted
normalization values with the model. The generated `model.json` contains the
weights needed for later ESP32 inference, while `training_metrics.json` records
the measured train/test accuracy and individual test predictions.

The model-training workflow was AI-assisted: AI helped design the small
architecture and training script, while the script was run locally against the
project datasets to produce the recorded model and metrics.
