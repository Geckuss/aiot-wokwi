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
the current readings every two seconds.
