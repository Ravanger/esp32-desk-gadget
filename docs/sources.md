# Sources & credits

This project synthesizes patterns and facts from the following
guides and references. Where a source disagrees with another, the
resolution used in this project is noted.

## Guides

- **MakerGuides — Simple ESP32 Internet Weather Station.**
  The WiFi + HTTPClient + ArduinoJson + Adafruit_SSD1306 pattern,
  field parsing, display, and 10-minute refresh used for the outdoor
  screen. The original used OpenWeatherMap with an API key; this
  project substitutes Open-Meteo, which needs none.
  <https://www.makerguides.com/simple-esp32-internet-weather-station/>
- **Instructables — ESP32 and OLED Display: Internet Clock (DHT22).**
  The one-display, multiple-pages concept; the original's page
  selector was a potentiometer, replaced here by a rotary encoder.
  <http://www.instructables.com/id/ESP32-and-OLED-Display-Internet-Clock-DHT22/>
- **LastMinuteEngineers — ESP32 Rotary Encoder Tutorial.**
  Quadrature CLK/DT phase relationship, polling vs interrupt decode
  table, INPUT_PULLUP, and button debounce.
  <https://lastminuteengineers.com/esp32-rotary-encoder-tutorial/>
- **CircuitDigest — Internet Clock using ESP32 and OLED.**
  NTP/UDP concept diagram only. The CircuitDigest build itself wires
  its OLED over SPI; this project uses I2C, so its circuit diagram
  is deliberately not reproduced.
  <https://circuitdigest.com/microcontroller-projects/esp32-internet-clock>

## Board and component references

- **ESP32-C3 SuperMini pinout sources.** The SuperMini breaks out
  GPIOs 0–10, 20, 21; I2C runs through the GPIO matrix (not fixed
  pins); strapping pins are GPIO 2, 8, 9; GPIO 8 also drives the
  onboard LED (simple blue LED on standard boards, WS2812 RGB on
  "Plus" variants) and GPIO 9 is the BOOT button, so neither is used
  for I2C here — I2C is on GPIO 4/5 instead. The 3.3 V regulator
  supplies up to about 500 mA.
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
- **DHT11 specifications.** 0–50 °C (±2 °C), 20–80 % RH (±5 % RH),
  1 Hz maximum sampling rate, 3.3–5.5 V operation. Some datasheets
  quote up to 90 % RH; this project uses the conservative 20–80 %
  figure.
  <https://pcbsync.com/dht11-arduino/>
- **SSD1306 I2C addressing.** The 7-bit address is 0x3C or 0x3D,
  selected by the SA0 pin; most 4-pin modules include pull-up
  resistors and default to 0x3C.
  <https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module?view=all>
- **Open-Meteo API.** Free weather API, no key, no signup; the
  `current` fields and the WMO weather-code subset used by this
  project are documented there.
  <https://open-meteo.com/>

## Images

### Self-hosted (in `assets/`)

| Image | Source guide |
| ----- | ------------ |
| `oled-display.jpg` | MakerGuides — 0.96-inch SSD1306 OLED photo |
| `esp32-oled-wiring.png` | MakerGuides — ESP32 → OLED wiring (shown for the four-wire pattern only; pin numbers differ on the SuperMini) |
| `encoder-wiring.png` | LastMinuteEngineers — rotary encoder wiring |
| `encoder-internal.png` | LastMinuteEngineers — encoder internal structure |

### Linked from source guides (not hosted here)

| Image | Used in | Source guide |
| ----- | ------- | ------------ |
| ESP32 board photo | `parts.md` | MakerGuides |
| Breadboard photo | `parts.md` | MakerGuides |
| Jumper wire set photo | `parts.md` | MakerGuides |
| Encoder module pinout | `wiring.md` | LastMinuteEngineers |
| NTP/UDP communication diagram | `how-it-works.md` | CircuitDigest (concept diagram, not wiring) |
| Encoder working animation | `how-it-works.md` | LastMinuteEngineers |
| Clockwise pulse diagram | `how-it-works.md` | LastMinuteEngineers |
| Counter-clockwise pulse diagram | `how-it-works.md` | LastMinuteEngineers |
| Serial Monitor encoder output | `build-order.md` | LastMinuteEngineers |

### Deliberately excluded

- CircuitDigest's circuit diagram: it wires the OLED over SPI, which
  contradicts this project's I2C wiring.
- Instructables step photos/GIFs: they show a 128×32 demo panel, not
  this project's 128×64 panel.
- MakerGuides' weather-JSON screenshot: it shows OpenWeatherMap JSON,
  which would mislead readers of an Open-Meteo build.

## Data sources

- Weather data: Open-Meteo, free for non-commercial use.
- Time: NTP (`pool.ntp.org`, `time.nist.gov`).
