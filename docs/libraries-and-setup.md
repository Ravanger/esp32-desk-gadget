# Libraries & setup

Work in the Arduino IDE or PlatformIO — the sketch in
[`../firmware/desk_gadget.ino`](../firmware/desk_gadget.ino) is plain
Arduino-framework ESP32 either way.

## Arduino IDE

1. Install the ESP32 board package (Boards Manager → "esp32 by
   Espressif"), and select your dev board.
2. Install these from the Library Manager:

| Library | Install name | Used for |
| ------- | ------------ | -------- |
| Adafruit GFX | "Adafruit GFX Library" | Text and drawing primitives for the OLED |
| Adafruit SSD1306 | "Adafruit SSD1306" | Driving the display, including the contrast command used for dimming |
| Adafruit DHT sensor | "DHT sensor library" by Adafruit (+ its "Adafruit Unified Sensor" dependency) | Reading the DHT11 |
| ArduinoJson | "ArduinoJson" by Benoit Blanchon (v7) | Parsing the Open-Meteo response |
| WiFi, HTTPClient, time | Built into the ESP32 core — nothing to install | WiFi, the weather fetch, and NTP clock sync |

## PlatformIO

The same set in `lib_deps`:

```
adafruit/Adafruit GFX Library
adafruit/Adafruit SSD1306
adafruit/DHT sensor library
bblanchon/ArduinoJson
```

## Configuration

The only configuration in the whole build is two lines at the top of
the sketch: your WiFi name and password. Everything else — Toronto
coordinates, timezone, pins — is already filled in.
