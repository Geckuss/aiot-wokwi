# Indoor temperature and humidity monitor

This Wokwi project uses an **ESP32 DevKit v1**, a DHT22 sensor, and six LEDs.
The first version runs locally; the ESP32's Wi-Fi is available for future work.

## LED meaning

| Measurement | Green | Yellow | Red |
| --- | --- | --- | --- |
| Temperature | 18-26 °C | 15-17 °C or 27-30 °C | below 15 °C or above 30 °C |
| Humidity | 30-60% | 20-29% or 61-70% | below 20% or above 70% |

The DHT22 starts at 22 °C and 45% humidity. Change its values in Wokwi to test
the other states.

## Wiring

- DHT22 `VCC` -> ESP32 `3V3`
- DHT22 `GND` -> ESP32 `GND`
- DHT22 `SDA` -> ESP32 GPIO 4
- Temperature LEDs: GPIO 16, 17, 18 through 220 ohm resistors
- Humidity LEDs: GPIO 19, 21, 22 through 220 ohm resistors
- Every LED cathode connects to ESP32 `GND`

## Train the model

The sketch prints rows in this format:

```text
sample_ms,temperature_c,humidity_percent,label
```

Set `datasetLabel` in `sketch.ino`, record examples for `comfortable`,
`warning`, and `poor`, and save them in the matching CSV files under `datasets`.
Then run:

```text
python train_model.py
```

This trains a small `2 -> 8 -> 3` neural network and saves it to `model.json`.

## Quantize and run on the ESP32

Run `python optimize_model.py` to export the model to `model_data.h`, which the
ESP32 can use without reading JSON. The two weight matrices are stored as int8
with one scale per layer. Biases, activations, and inference remain float:
this is simple weight-only quantization, not a fully integer model.

Keep `sketch.ino` and `model_data.h` in the Wokwi project. Start the simulation
and open the Serial Monitor to see readings and predictions. Run
`python -m unittest discover -s tests` to check the quantized model against the
held-out training rows.
