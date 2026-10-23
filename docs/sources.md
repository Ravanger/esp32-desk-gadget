# Sources & photo credits

This guide is a synthesis of the three builds below, adapted to the
parts on hand: the MakerGuides fetch-parse-display pattern (with
Open-Meteo substituted for the key-based OpenWeatherMap), the
Instructables clock's multi-page idea, and LastMinuteEngineers' encoder
reading. All photos and wiring diagrams are theirs, credited under each
image — none are photos of this build.

- **MakerGuides — Simple ESP32 Internet Weather Station.** WiFi +
  HTTPClient + ArduinoJson + Adafruit_SSD1306 pattern, 10-minute
  refresh, and the ESP32-Lite SDA 19 / SCL 23 caveat.
  <https://www.makerguides.com/simple-esp32-internet-weather-station/>
- **Open-Meteo API.** Free weather API, no key, no signup. Toronto
  request used in this guide:
  <https://api.open-meteo.com/v1/forecast?latitude=43.65&longitude=-79.36&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=America%2FToronto>
  · WMO code reference: <https://open-meteo.com/en/docs>
- **Instructables — ESP32 and OLED Display: Internet Clock (DHT22).**
  The one-display, multiple-pages concept this build's page system
  adapts.
  <http://www.instructables.com/id/ESP32-and-OLED-Display-Internet-Clock-DHT22/>
- **LastMinuteEngineers — ESP32 Rotary Encoder Tutorial.** Quadrature
  signals, polling vs interrupt decode table, pull-ups and button
  debounce.
  <https://lastminuteengineers.com/esp32-rotary-encoder-tutorial/>
- **ESP32-C3 SuperMini pinout sources (for the C3 revision of this
  guide).** The SuperMini breaks out GPIOs 0–10, 20, 21; I2C runs
  through the GPIO matrix (not fixed pins); strapping pins are GPIO 2,
  8, 9; GPIO 8 also drives the onboard LED and GPIO 9 is the BOOT
  button, so neither is used for I2C here — I2C is on GPIO 4/5 instead.
  - ESPboards — ESP32 C3 Super Mini pinout:
    <https://www.espboards.dev/esp32/esp32-c3-super-mini/>
  - LastMinuteEngineers — ESP32-C3 Super Mini Pinout Reference
    (including the warning against GPIO 8/9 for I2C):
    <https://lastminuteengineers.com/esp32-c3-super-mini-pinout-reference/>
  - Mischianti — ESP32-C3 SuperMini Plus pinout (recommends
    `Wire.begin(4, 5)`, USB CDC On Boot for Serial):
    <https://mischianti.org/esp32-c3-supermini-plus-v2-high-resolution-pinout-datasheet-and-specs/>
  - Espressif ESP-IDF — GPIO & RTC GPIO, ESP32-C3 (ADC1 on GPIO 0–4,
    ADC2 on GPIO 5, strapping pins 2/8/9):
    <https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32c3/api-reference/peripherals/gpio.html>

Built from parts in the ESP32 starter kit + 45-in-1 sensor kit. Photos
and diagrams © their respective guides, linked above. Weather data:
Open-Meteo. Times: America/Toronto.

## Images in this repo

Self-hosted in `assets/` (copied from the source guides, credited
under each image):

| File | Source guide |
| ---- | ------------ |
| `assets/oled-display.jpg` | MakerGuides — SSD1306 OLED photo |
| `assets/esp32-oled-wiring.png` | MakerGuides — ESP32-Lite → OLED wiring |
| `assets/encoder-wiring.png` | LastMinuteEngineers — rotary encoder wiring |
| `assets/encoder-internal.png` | LastMinuteEngineers — encoder internal structure |

Linked from the source guides (not self-hosted, so they always show
the guide's own version):

| Where used | Image | Source guide |
| ---------- | ----- | ------------ |
| `docs/parts.md` | ESP32 board photo | MakerGuides |
| `docs/parts.md` | Breadboard photo | MakerGuides |
| `docs/parts.md` | Jumper wire set photo | MakerGuides |
| `docs/wiring.md` | Encoder module pinout | LastMinuteEngineers |
| `docs/how-it-works.md` | NTP/UDP communication diagram | CircuitDigest (concept diagram, not wiring — their clock uses SPI, this build uses I2C) |
| `docs/how-it-works.md` | Encoder working animation | LastMinuteEngineers |
| `docs/how-it-works.md` | Clockwise pulse diagram | LastMinuteEngineers |
| `docs/how-it-works.md` | Counter-clockwise pulse diagram | LastMinuteEngineers |
| `docs/build-order.md` | Serial Monitor encoder output | LastMinuteEngineers |

Deliberately left out: CircuitDigest's own circuit diagram (it wires
the OLED over SPI, which would contradict this build's I2C wiring),
and the Instructables step photos (their demo uses a 128×32 OLED and
GIF demos, not the 128×64 panel in this build).
