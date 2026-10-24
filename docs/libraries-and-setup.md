# Libraries & setup

Work in the Arduino IDE or PlatformIO — the sketch in
[`../firmware/desk_gadget.ino`](../firmware/desk_gadget.ino) is plain
Arduino-framework ESP32 either way.

## Arduino IDE

1. Install the ESP32 board package (Boards Manager → "esp32 by
   Espressif") and select **"ESP32C3 Dev Module"**, then set **Tools →
   USB CDC On Boot: Enabled** (its default is Disabled). This matches the
   configuration compile-verified under PlatformIO (arduino-esp32
   2.0.17, board esp32-c3-devkitm-1). The board
   **"Nologo ESP32C3 Super Mini"** exists in arduino-esp32 3.x, where
   USB CDC On Boot is enabled by default; it is not yet
   compile-verified with this sketch.
2. The SuperMini's USB-C is native USB, not a separate serial chip —
   without USB CDC On Boot, Serial Monitor output will not show.
3. Install these from the Library Manager:

| Library | Used for |
| ------- | -------- |
| Adafruit GFX Library | Display drawing primitives |
| Adafruit SSD1306 | SSD1306 OLED driver |
| DHT sensor library (Adafruit) | DHT11 readings (also requires Adafruit Unified Sensor, installed automatically as a dependency) |
| ArduinoJson (v7 or newer) | Parsing the Open-Meteo JSON response |

Compile-verified on arduino-esp32 2.0.17 (PlatformIO) only, 2026-10-24;
core 3.x not yet compile-verified (latest stable 3.3.12 as checked 2026-10-24).
Versions used: ArduinoJson 7.4.3, Adafruit SSD1306 2.5.17, Adafruit GFX
1.13.0, DHT sensor library 1.4.7, Adafruit Unified Sensor 1.1.15.

The following are built into the ESP32 core — nothing to install:

| Built-in | Used for |
| -------- | -------- |
| WiFi, HTTPClient, time | WiFi connection, the weather fetch, and NTP clock sync |
| WiFiClientSecure | TLS for the HTTPS weather request |
| Wire | I2C bus for the OLED |

## PlatformIO

Example `platformio.ini`:

```ini
[env:supermini]
platform = espressif32@6.9.0
board = esp32-c3-devkitm-1
framework = arduino
monitor_speed = 115200
build_flags =
    -DARDUINO_USB_CDC_ON_BOOT=1
    -DARDUINO_USB_MODE=1
lib_deps =
    adafruit/Adafruit GFX Library@1.13.0
    adafruit/Adafruit BusIO@1.17.4
    adafruit/Adafruit SSD1306@2.5.17
    adafruit/DHT sensor library@1.4.7
    adafruit/Adafruit Unified Sensor@1.1.15
    bblanchon/ArduinoJson@7.4.3
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
   Look up coordinates with the
   [Open-Meteo geocoding API](https://open-meteo.com/en/docs/geocoding-api)
   or any map service. The sketch sends coordinates to 4 decimal
   places (about 11 m precision). `LOCATION_TZ` only affects the
   server-side time formatting in the weather reply; the sketch's
   clock uses `TIMEZONE_POSIX`. Keep `LOCATION_NAME` ASCII and short —
   about 8 characters at most: the outdoor header is
   `"<NAME> - OPEN-METEO"` at text size 1 (6 px per character) on a
   128 px display, so a longer name clips off-screen and the sketch
   does not truncate it for you.
3. **Local time** — `TIMEZONE_POSIX`, the POSIX time-zone string for
   the clock (for example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time,
   `GMT0BST,M3.5.0,M10.5.0` for UK time). This is separate from the
   Open-Meteo time zone: the POSIX string tells the board how to
   convert NTP (UTC) time to local time, including daylight-saving
   rules. Look your zone up in a
   [POSIX time-zone list](https://github.com/nayarsystems/posix_tz_db/blob/master/zones.csv)
   rather than writing it from memory. The sign is inverted relative
   to UTC offsets: UTC+9 is written `JST-9`.
4. **WiFi TX power** — `WIFI_LOW_TX_POWER` (default 0). Set it to 1 if
   the board fails to join WiFi or drops out; the sketch then calls
   `WiFi.setTxPower()` at 8.5 dBm after `WiFi.begin()`. This is a
   community-reported SuperMini workaround, not an Espressif
   recommendation. It lowers radiated power, not a guaranteed fix for an
   undersized regulator: Espressif does not publish the TX current at
   8.5 dBm, so measure with a USB meter.
5. **Navigation input** — `USE_ENCODER` (default 0). Leave it at 0 for the push button, which steps to the next page on each press. Set it to 1 if a rotary encoder is wired instead of the button (CLK 6, DT 7, SW 10): rotate to change pages, press to jump to Summary and back. See [wiring.md](wiring.md).

The values shipped in the sketch are an example configuration; replace
them with the target location before use. Nothing else in the sketch
needs editing for a standard build.

## Uploading

1. Connect the SuperMini with a USB-C **data** cable.
2. Select the correct port and the board from the list above.
3. Upload. If the board does not enter download mode, hold the BOOT
   button (GPIO 9), tap RESET, then upload (or hold BOOT while plugging
   in USB). Press RESET after the upload finishes. The serial port may
   change while the board is in download mode.
4. Open Serial Monitor at 115200 baud to check for startup messages.
   The sketch prints only the OLED error (if the display is not
   found), "WiFi: connecting..." then "WiFi: connected" or
   "WiFi: connection failed (30 s timeout)", and weather HTTP/parse
   errors — it does not print a running WiFi status log. On native
   USB the monitor reconnects after a reset, so the earliest lines may
   be missed. A WiFi
   failure does not stop the sketch: after the 30 s timeout it
   continues, and NTP/weather recover on their own when WiFi comes
   up.

## Verifying the libraries

If the sketch fails to compile with "No such file or directory" for a
header, the corresponding library is missing from the Library Manager
list above — install it and recompile. If compilation fails on
`JsonDocument`, the installed ArduinoJson version is older than v7;
update it.

---

[← Previous: Wiring](wiring.md) · [Contents](../README.md) · [Next: How it works →](how-it-works.md)
