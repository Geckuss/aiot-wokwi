# Indoor temperature and humidity monitor

This Wokwi project uses an **ESP32 DevKit v1**, a DHT22 sensor, and six LEDs.
The first version runs locally; the ESP32's Wi-Fi is available for future work.

## LED meaning

Both LED groups show the combined model classification: green for comfortable,
yellow for warning, and red for poor.

The DHT22 starts at 22 °C and 45% humidity. Target labels are comfortable at
**19–25 °C and 30–60% humidity**, warning just outside that range (within
17–27 °C and 20–70%), and poor beyond those margins. The small neural network
approximates these ranges; its predictions can differ near a boundary.

## Wiring

- DHT22 `VCC` -> ESP32 `3V3`
- DHT22 `GND` -> ESP32 `GND`
- DHT22 `SDA` -> ESP32 GPIO 4
- Temperature LEDs: GPIO 16, 17, 18 through 220 ohm resistors
- Humidity LEDs: GPIO 19, 21, 22 through 220 ohm resistors
- Every LED cathode connects to ESP32 `GND`

## Train the model

The CSV files in `datasets` contain 556 balanced synthetic examples labeled
using those ranges; they are not sensor recordings. Run:

```text
python train_model.py
```

This trains a `2 -> 16 -> 3` neural network and saves it to `model.json`.

## Quantize and run on the ESP32

Run `python optimize_model.py` to export the model to `model_data.h`, which the
ESP32 can use without reading JSON. The two weight matrices are stored as int8
with one scale per layer. Biases, activations, and inference remain float:
this is simple weight-only quantization, not a fully integer model.
AI assistance was used to create the model optimization and quantization script.

Keep `sketch.ino` and `model_data.h` in the Wokwi project. Start the simulation
and open the Serial Monitor to see readings and predictions. Run
`python -m unittest discover -s tests` to check quantized predictions against
held-out examples and representative range cases.
