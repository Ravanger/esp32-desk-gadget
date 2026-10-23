# Libraries & setup

Work in the Arduino IDE or PlatformIO — the sketch in
[`../firmware/desk_gadget.ino`](../firmware/desk_gadget.ino) is plain
Arduino-framework ESP32 either way.

## Arduino IDE

1. Install the ESP32 board package (Boards Manager → "esp32 by
   Espressif"), and select **"ESP32C3 Dev Module"** for the SuperMini.
2. **Enable Tools → USB CDC On Boot.** The SuperMini's USB-C is native
   USB, not a separate serial chip — without this setting, Serial
   Monitor output won't show.
3. Install these from the Library Manager:

| Library | Install name | Used for |
| ------- | ------------ | -------- |
| Adafruit GFX | "Adafruit GFX Library" | Text and drawing primitives for the OLED |
| Adafruit SSD1306 | "Adafruit SSD1306" | Driving the display, including the contrast command used for dimming |
| Adafruit DHT sensor | "DHT sensor library" by Adafruit (+ its "Adafruit Unified Sensor" dependency) | Reading the DHT11 |
| ArduinoJson | "ArduinoJson" by Benoit Blanchon (v7) | Parsing the Open-Meteo response |
| WiFi, HTTPClient, time | Built into the ESP32 core — nothing to install | WiFi, the weather fetch, and NTP clock sync |

## PlatformIO

Board: `esp32-c3-devkitm-1`. The same libraries in `lib_deps`:

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
