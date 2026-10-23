# Verified specifications

Every fact below was checked against its source on the date shown.
Agents changing a fact must update the source and the date here —
never change a number from memory. See `AGENTS.md` and
`scripts/check.sh` (which enforces the pin and WMO lists).

Checked: 2026-10-23.

## Board: ESP32-C3 SuperMini

| Fact | Source |
| ---- | ------ |
| Breaks out GPIOs 0–10, 20, 21 | ESPboards SuperMini pinout, LastMinuteEngineers C3 Super Mini Pinout Reference |
| Strapping pins: GPIO 2, 8, 9 | Espressif ESP-IDF GPIO docs (ESP32-C3) |
| GPIO 8 drives the onboard LED (blue LED on standard boards, WS2812 on "Plus" variants); GPIO 9 is the BOOT button | Mischianti SuperMini / SuperMini Plus pinouts |
| I2C runs through the GPIO matrix; no fixed I2C pins at chip level | Espressif ESP-IDF GPIO docs; LastMinuteEngineers C3 pinout reference |
| 3.3 V regulator supplies up to about 500 mA | Mischianti SuperMini pinout |
| Single-core RISC-V, 160 MHz, 4 MB flash, 400 KB SRAM, 2.4 GHz WiFi only, USB-C native USB | Mischianti SuperMini pinout |
| USB CDC On Boot must be enabled for Serial output over native USB | Mischianti SuperMini Plus pinout; ESPboards SuperMini Plus notes |
| ADC1: GPIO 0–4; ADC2: GPIO 5 (unreliable while WiFi is on) | Espressif ESP-IDF GPIO docs |
| No capacitive-touch peripheral (unlike the classic ESP32) | Espressif ESP32-C3 documentation; see `docs/sources.md` |

## Sensors and display

| Fact | Source |
| ---- | ------ |
| DHT11: 0–50 °C (±2 °C), 20–80 % RH (±5 % RH), 1 Hz maximum sampling, 3.3–5.5 V | DHT11 datasheet summaries (see `docs/sources.md`); some datasheets quote up to 90 % RH — this project uses the conservative 20–80 % figure |
| SSD1306 I2C address: 0x3C or 0x3D, selected by SA0; most 4-pin modules include pull-ups and default to 0x3C | Adafruit SSD1306 documentation |
| OLED brightness is contrast (0–255), not a backlight | SSD1306 datasheet via Adafruit / ThingPulse driver docs |

## Weather: Open-Meteo

| Fact | Source |
| ---- | ------ |
| Free for non-commercial use, about 10,000 requests/day, no key, no signup | Open-Meteo documentation |
| WMO codes returned (full list, enforced by `scripts/check.sh`): 0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 97, 99 | Open-Meteo WMO Weather interpretation codes |
| Code 97 = Heavy thunderstorm. It IS in the official list. Models without an explicit hail forecast report 95 and 97; hail models report 96 and 99. | Open-Meteo WMO table, footnote on codes 96/99 |
| This project fetches once every 10 minutes = 144 requests/day | Project design (see `docs/how-it-works.md`) |

## Hosting and CI costs

| Fact | Source |
| ---- | ------ |
| GitHub Actions is free for public repos on standard runners; private repos get an included allowance only (2,000 min/month on Free, 3,000 on Pro/Team), then billed per minute | GitHub billing documentation (checked 2026-10-23) |
| A $0 spending limit stops workflows instead of billing once the allowance is used | GitHub billing documentation |

## Source links

- ESPboards SuperMini pinout: https://www.espboards.dev/esp32/esp32-c3-super-mini/
- LastMinuteEngineers C3 Super Mini Pinout Reference: https://lastminuteengineers.com/esp32-c3-super-mini-pinout-reference/
- Mischianti SuperMini pinout: https://mischianti.org/esp32-c3-super-mini-high-resolution-pinout-datasheet-and-specs/
- Mischianti SuperMini Plus pinout: https://mischianti.org/esp32-c3-supermini-plus-v2-high-resolution-pinout-datasheet-and-specs/
- Espressif ESP-IDF GPIO (ESP32-C3): https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32c3/api-reference/peripherals/gpio.html
- Open-Meteo docs: https://open-meteo.com/en/docs
- Adafruit SSD1306: https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module?view=all
