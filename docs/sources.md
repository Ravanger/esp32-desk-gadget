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
  selector was a potentiometer, replaced here by a push button (or an optional rotary encoder).
  <https://www.instructables.com/id/ESP32-and-OLED-Display-Internet-Clock-DHT22/>
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

- **ESP32-C3 SuperMini board sources** (board-level and community
  reports, not Espressif documents). The SuperMini breaks out
  GPIOs 0–10, 20, 21; I2C runs through the GPIO matrix (not fixed
  pins); strapping pins are GPIO 2, 8, 9; GPIO 8 also drives the
  onboard LED (simple blue LED on standard boards, WS2812 RGB on
  "Plus" variants) and GPIO 9 is the BOOT button, so neither is used
  for I2C here. The 3.3 V regulator rating varies by clone: 500 mA
  is quoted by Random Nerd Tutorials, while one reader report on the
  SIGMDEL page mentions 250 mA parts. Checked 2026-10-24.
  - ESPboards — ESP32 C3 Super Mini pinout:
    <https://www.espboards.dev/esp32/esp32-c3-super-mini/>
  - Random Nerd Tutorials — Getting started with the ESP32-C3 Super
    Mini (pinout, 500 mA regulator claim):
    <https://randomnerdtutorials.com/getting-started-esp32-c3-super-mini/>
  - SIGMDEL — Super Mini ESP32-C3 (5V pin is USB VBUS directly;
    antenna design flaw; reader report of 250 mA regulator parts):
    <https://sigmdel.ca/michel/ha/esp8266/super_mini_esp32c3_en.html>
  - Components101 — ESP32-C3 Mini development board pinout:
    <https://components101.com/development-boards/esp32c3-mini-development-board-datasheet-pinout>
  - LastMinuteEngineers — ESP32-C3 Super Mini Pinout Reference
    (including the warning against GPIO 8/9 for I2C):
    <https://lastminuteengineers.com/esp32-c3-super-mini-pinout-reference/>
  - Mischianti — ESP32-C3 SuperMini Plus pinout (recommends
    `Wire.begin(4, 5)`, which this sketch writes as
    `Wire.begin(OLED_SDA, OLED_SCL)`; USB CDC On Boot for Serial):
    <https://mischianti.org/esp32-c3-supermini-plus-v2-high-resolution-pinout-datasheet-and-specs/>
  - WiFi TX-power workaround (community reports, not Espressif;
    call `WiFi.setTxPower()` after `WiFi.begin()`):
    <https://github.com/HomeSpan/HomeSpan/issues/780> and
    <https://www.electromaker.io/project/view/esp32-c3-super-mini-wifi-fix-3-methods-that-work>
- **SSD1306 I2C addressing.** The 7-bit address is 0x3C or 0x3D,
  selected by the SA0 pin; most 4-pin modules include pull-up
  resistors and default to 0x3C.
  <https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module?view=all>
- **Open-Meteo API.** Free weather API, no key, no signup; the
  `current` fields and the WMO weather-code subset used by this
  project are documented there. Checked 2026-10-24.
  - API documentation: <https://open-meteo.com/en/docs>
  - Geocoding API (latitude/longitude lookup):
    <https://open-meteo.com/en/docs/geocoding-api>
  - Terms (free non-commercial tier: under 10,000 calls/day,
    5,000/hour, 600/minute; CC-BY 4.0 licence):
    <https://open-meteo.com/en/terms>
- **POSIX time-zone strings.** A table of IANA zone names with
  matching POSIX strings. Note the inverted sign: UTC+9 is written
  `JST-9`. Checked 2026-10-24 (page loads; the table is truncated in
  the web view, use the raw file link).
  <https://github.com/nayarsystems/posix_tz_db/blob/master/zones.csv>

## Datasheets and official documentation

All checked 2026-10-24. Figures taken from them are listed in
[verified-specs.md](verified-specs.md).

- **ESP32-C3 datasheet v2.4** (Espressif): ADC attenuation ranges
  (Table 5-6), ADC DNL/INL with an external 100 nF capacitor
  (section 5.5, Table 5-5), Wi-Fi TX/RX current (Table 5-7), absolute
  maximum ratings and pull-up value (Tables 5-1, 5-4), strapping pins
  and boot modes (Table 3-3), GPIO 0/1 as 32 kHz crystal pins.
  <https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf>
- **Arduino-ESP32 ADC API** (11 dB = 0–2500 mV on the C3;
  `analogReadMilliVolts`):
  <https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html>
- **ESP-IDF ADC oneshot mode, ESP32-C3** (ADC2 oneshot mode not
  supported due to hardware limitations):
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/adc/adc_oneshot.html>
- **arduino-esp32 `boards.txt`** ("Nologo ESP32C3 Super Mini" with
  USB CDC On Boot enabled by default; "ESP32C3 Dev Module" default
  disabled):
  <https://github.com/espressif/arduino-esp32/blob/master/boards.txt>
- **Espressif ESP-IDF — GPIO & RTC GPIO, ESP32-C3** (ADC1 on
  GPIO 0–4, ADC2 on GPIO 5, strapping pins 2/8/9):
  <https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32c3/api-reference/peripherals/gpio.html>
- **SSD1306 datasheet** (Solomon Systech; contrast command, I2C
  address, VDD limits). Checked 2026-10-24:
  <https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf>
- **Adafruit_SSD1306** (`begin()` does not probe I2C). Checked 2026-10-24:
  <https://github.com/adafruit/Adafruit_SSD1306>
- **Adafruit SH110x** and **U8g2** (drivers for SH1106 panels). Checked
  2026-10-24:
  <https://github.com/adafruit/Adafruit_SH110x> and
  <https://github.com/olikraus/u8g2>
- **Adafruit DHT sensor library** (`MIN_INTERVAL` 2000 in `DHT.cpp`).
  Checked 2026-10-24:
  <https://github.com/adafruit/DHT-sensor-library>
- **arduino-esp32 core sources** (`cores/esp32/esp32-hal-time.c`,
  `libraries/HTTPClient`, `libraries/NetworkClientSecure`). Checked
  2026-10-24:
  <https://github.com/espressif/arduino-esp32>
- **TTP223 datasheet** (copy hosted by Components101; the Tontek
  original is no longer reliably online). Checked 2026-10-24:
  <https://components101.com/sites/default/files/component_datasheet/TTP223-Datasheet.pdf>
- **Aosong DHT11 datasheet** (translated copy; supply 3–5.5 V,
  20–90 % RH ±5 %, 0–50 °C ±2 °C, 1 s sampling period, 5 kΩ pull-up
  for cables under 20 m). Third-party summaries disagree with it on
  humidity range, current and supply minimum; the datasheet is used
  here.
  <https://ece-classes.usc.edu/ee459/library/datasheets/DHT11.pdf>
- **HC-SR501 PIR datasheet** (reseller copy; supply 5–20 V, output
  3.3 V, about 1 min warm-up, delay 5–300 s):
  <https://electrokit.com/upload/quick/17/af/010a_41015509-ds.pdf>
- **KY-040 encoder module** (secondary: CLK/DT pull-ups to `+`;
  SW pull-up and resistor values unverified):
  <https://docs.wokwi.com/parts/wokwi-ky-040>

## Images

All images are stored in `assets/` and credited here; none are
hotlinked. Images without a stated licence are used with credit for
this private, non-commercial guide; reuse permission was not
separately obtained, and a credit here is not a licence. Before making
the guide public or commercial, re-clear every unlicensed image and
replace `supermini-pinout.jpg` (CC BY-NC-ND 4.0 bars commercial use).

| Image | Used in | Credit and source |
| ----- | ------- | ----------------- |
| `supermini-pinout.jpg` | `parts.md`, `wiring.md` | Renzo Mischianti, CC BY-NC-ND 4.0 — <https://mischianti.org/esp32-c3-super-mini-high-resolution-pinout-datasheet-and-specs/> |
| `oled-display.jpg` | `parts.md` | MakerGuides — <https://www.makerguides.com/simple-esp32-internet-weather-station/> |
| `esp32-oled-wiring.png` | `wiring.md` | MakerGuides (four-wire pattern only; pin numbers differ on the SuperMini) — <https://www.makerguides.com/simple-esp32-internet-weather-station/> |
| `breadboard.png` | `parts.md` | MakerGuides — <https://www.makerguides.com/wp-content/uploads/2019/05/Half_breadboard56a.png> |
| `jumper-wires.png` | `parts.md` | MakerGuides — <https://www.makerguides.com/wp-content/uploads/2023/09/dupon_wire_set.png> |
| `dht11-pinout.jpg` | `parts.md` | Components101 — <https://components101.com/sensors/dht11-temperature-sensor> |
| `push-button-pinout.gif` | `parts.md`, `wiring.md` | Components101 — <https://components101.com/switches/push-button> |
| `pir-pinout.png` | `parts.md`, `how-it-works.md` | Components101 — <https://components101.com/sensors/hc-sr501-pir-sensor> |
| `potentiometer.jpg` | `parts.md` | Richard Wheeler (Zephyris), Wikimedia Commons, CC BY-SA 3.0 / GFDL 1.2+ — <https://commons.wikimedia.org/wiki/File:Rotary_Potentiometer.jpg> |
| `voltage-divider.png` | `how-it-works.md` | Wikimedia Commons, public domain (rendered from SVG) — <https://commons.wikimedia.org/wiki/File:Voltage_divider.svg> |
| `switch-bounce.png` | `how-it-works.md` | Pololu — <https://www.pololu.com/docs/0J16/4> |
| `ntp-udp.png` | `how-it-works.md` | CircuitDigest (concept diagram, not wiring) — <https://circuitdigest.com/microcontroller-projects/esp32-internet-clock> |
| `encoder-wiring.png` | `wiring.md` | LastMinuteEngineers — <https://lastminuteengineers.com/esp32-rotary-encoder-tutorial/> |
| `encoder-pinout.png` | `wiring.md` | LastMinuteEngineers — <https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/> |
| `encoder-internal.png` | `how-it-works.md` | LastMinuteEngineers — <https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/> |
| `encoder-animation.gif` | `how-it-works.md` | LastMinuteEngineers — <https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/> |
| `encoder-pulses-cw.png` | `how-it-works.md` | LastMinuteEngineers — <https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/> |
| `encoder-pulses-ccw.png` | `how-it-works.md` | LastMinuteEngineers — <https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/> |
| `encoder-serial-monitor.png` | `build-order.md` | LastMinuteEngineers — <https://lastminuteengineers.com/esp32-rotary-encoder-tutorial/> |

### Deliberately excluded

- CircuitDigest's circuit diagram: it wires the OLED over SPI, which
  contradicts this project's I2C wiring.
- Instructables step photos/GIFs: they show a 128×32 demo panel, not
  this project's 128×64 panel.
- MakerGuides' weather-JSON screenshot: it shows OpenWeatherMap JSON,
  which would mislead readers of an Open-Meteo build.

## Data sources

- Weather data: Open-Meteo, free for non-commercial use
  (<https://open-meteo.com/en/terms>).
- Time: NTP (`pool.ntp.org`, `time.nist.gov`).

---

[← Previous: Troubleshooting](troubleshooting.md) · [Contents](../README.md) · [Next: Verified specifications →](verified-specs.md)
