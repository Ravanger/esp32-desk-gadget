# Libraries & setup

Work in the Arduino IDE or PlatformIO — the sketch in
[`../firmware/desk_gadget.ino`](../firmware/desk_gadget.ino) is plain
Arduino-framework ESP32 either way.

## Arduino IDE

1. Install the ESP32 board package (Boards Manager → "esp32 by
   Espressif"), and select **"ESP32C3 Dev Module"** for the SuperMini.
2. **Enable Tools → USB CDC On Boot.** The SuperMini's USB-C is native
   USB, not a separate serial chip — without this setting, Serial
   Monitor output will not show.
3. Install these from the Library Manager:

| Library | Used for |
| ------- | -------- |
| Adafruit GFX Library | Display drawing primitives |
| Adafruit SSD1306 | SSD1306 OLED driver |
| DHT sensor library (Adafruit) | DHT11 readings (also requires Adafruit Unified Sensor, installed automatically as a dependency) |
| ArduinoJson (v7) | Parsing the Open-Meteo JSON response |

The following are built into the ESP32 core — nothing to install:

| Built-in | Used for |
| -------- | -------- |
| WiFi, HTTPClient, time | WiFi connection, the weather fetch, and NTP clock sync |

## PlatformIO

Board: `esp32-c3-devkitm-1`. The same libraries in `lib_deps`:

```
adafruit/Adafruit GFX Library
adafruit/Adafruit SSD1306
adafruit/DHT sensor library
bblanchon/ArduinoJson
```

## Configuration (edit before uploading)

All configuration is in one block at the top of the sketch:

1. **WiFi** — `WIFI_SSID` and `WIFI_PASSWORD`. The network must be
   2.4 GHz; the ESP32-C3 has no 5 GHz radio, so a 5 GHz-only network
   will never connect.
2. **Location** — `LOCATION_LAT` and `LOCATION_LON` in decimal
   degrees, `LOCATION_TZ` as the IANA time-zone name (for example
   `America/Toronto`, `Europe/London`, `Asia/Tokyo`), and
   `LOCATION_NAME` as the short label shown on the outdoor screen.
   Coordinates can be found via the Open-Meteo geocoding API or any
   map service.
3. **Local time** — `TIMEZONE_POSIX`, the POSIX time-zone string for
   the clock (for example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time,
   `GMT0BST,M3.5.0,M10.5.0` for UK time). This is separate from the
   Open-Meteo time zone: the API time zone tells the server which
   local time to report, and the POSIX string tells the board how to
   convert NTP (UTC) time to local time, including daylight-saving
   rules.

The values shipped in the sketch are an example configuration; replace
them with the target location before use. Nothing else in the sketch
needs editing for a standard build.

## Uploading

1. Connect the SuperMini with a USB-C **data** cable.
2. Select the correct port and the "ESP32C3 Dev Module" board.
3. Upload. If the board does not enter download mode, hold the BOOT
   button (GPIO 9) while starting the upload, or hold BOOT while
   plugging in USB.
4. Open Serial Monitor at 115200 baud to check for startup messages
   (OLED detection, WiFi connection, weather fetch results).

## Verifying the libraries

If the sketch fails to compile with "No such file or directory" for a
header, the corresponding library is missing from the Library Manager
list above — install it and recompile. If compilation fails on
`JsonDocument`, the installed ArduinoJson version is older than v7;
update it.
