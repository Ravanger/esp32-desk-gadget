# ESP32 Desk Gadget

A multi-screen desktop display built around an ESP32-C3 SuperMini and
a 0.96-inch SSD1306 OLED. It shows:

- The time, synced over WiFi via NTP
- Indoor temperature and humidity from a DHT11 sensor
- Outdoor weather for a configurable location, from Open-Meteo
  (free, no API key, no account)
- A summary screen with brightness, WiFi status, and uptime

Navigation is one push button: each press steps to the next page (Clock → Indoor → Outdoor → Summary → Clock). An optional rotary encoder can replace the button (`USE_ENCODER` 1: rotate to change pages, press to jump to the summary and back to the clock).
A separate analog potentiometer controls screen
brightness. Power is USB-C; no host software is required at runtime —
the host computer only supplies power. Uploading the sketch still
needs the Arduino IDE or PlatformIO.

> **Board:** ESP32-C3 SuperMini. All pin numbers in this repository
> are SuperMini pins (I2C on GPIO 4/5, button on GPIO 10 (encoder on 6/7/10 if fitted), pot on ADC1
> GPIO 1). Pin numbers from classic ESP32 guides (21/22, 25/26/27, 34)
> do not apply to this board — see [docs/wiring.md](docs/wiring.md).

Bench-test status: compile-verified on arduino-esp32 2.0.17
(PlatformIO) only; core 3.x is not yet compile-verified. Not yet
bench-tested on hardware — measured values in [docs/hardware-tests.md](docs/hardware-tests.md)
are blank until someone records them.

## Features

- 4 screens: Clock, Indoor, Outdoor weather, Summary
- NTP time with a configurable time zone
- Configurable weather location (latitude, longitude, time zone)
- Indoor sensing with last-good-value retention on failed reads
- OLED brightness via potentiometer (contrast control, no backlight)
- Optional PIR wake/sleep support (compile-time flag)
- Breadboard build; no soldering if your SuperMini and modules already have header pins fitted
- No API keys or accounts; no host software at runtime (uploading
  needs the IDE or PlatformIO)

## The four screens

| Screen | Shows | Data source | Refresh |
| ------ | ----- | ----------- | ------- |
| 1 · Clock | Time (HH:MM), seconds, day and date | NTP over WiFi | Every second |
| 2 · Indoor | Indoor temperature + relative humidity | DHT11 on GPIO 3 | Every 2.5 seconds |
| 3 · Outdoor | Outdoor temperature, humidity, condition, wind | Open-Meteo API (no key) | Every 10 minutes (retry after 60 s on failure) |
| 4 · Summary | Key values, brightness, WiFi status, uptime | All of the above | Every second |

## Hardware

See [docs/parts.md](docs/parts.md) for the full list. In short:
ESP32-C3 SuperMini, SSD1306 128×64 I2C OLED, DHT11 module, tactile push button (or an optional rotary encoder module), 10K potentiometer, breadboard, jumper wires, and a
USB-C data cable (not a charge-only cable).

## Getting started

1. [Parts](docs/parts.md) — components and quantities
2. [Wiring](docs/wiring.md) — wiring table, including the I2C-pin warning
3. [Libraries & setup](docs/libraries-and-setup.md) — Arduino IDE and
   PlatformIO, plus configuration (WiFi, location, time zone)
4. [How it works](docs/how-it-works.md) — NTP clock, DHT11, Open-Meteo, button and optional encoder, dimming
5. [Build order](docs/build-order.md) — staged build, with a test after
   each stage
6. [Hardware tests](docs/hardware-tests.md) — bench checklist with
   expected values, to run against a finished build
7. [Troubleshooting](docs/troubleshooting.md) — symptoms, causes, fixes
8. [Sources & credits](docs/sources.md) — guides this project draws on,
   and image credits
9. [Verified specifications](docs/verified-specs.md) — checked facts,
   with sources and dates, that agents must not change from memory

Then upload the sketch:

- [firmware/desk_gadget.ino](firmware/desk_gadget.ino) — the complete
  sketch. Before uploading, edit the configuration block at the top:
  WiFi credentials, location (latitude/longitude/time zone), and the
  POSIX time-zone string for local time.

## Configuration

All user-specific settings live in one block at the top of the sketch:

- `WIFI_SSID`, `WIFI_PASSWORD` — a 2.4 GHz WiFi network
  (the ESP32-C3 has no 5 GHz radio)
- `LOCATION_LAT`, `LOCATION_LON` — decimal degrees for the weather
  location
- `LOCATION_TZ` — the IANA time-zone name for the Open-Meteo request
  (for example `America/Toronto`, `Europe/London`)
- `LOCATION_NAME` — the short label shown on the outdoor screen
  (keep it to about 8 characters, or the outdoor header clips)
- `TIMEZONE_POSIX` — the POSIX time-zone string for local clock time
  (for example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time)

The values shipped in the sketch are an example configuration; replace
them with the target location before use.

Optional, after the base build works: an HC-SR501 PIR on GPIO 0 can
blank the display when the room is quiet and wake it on motion. Enable
it with the `USE_PIR` flag in the sketch. The display blanks 60 s after the PIR's output drops
(details in [docs/how-it-works.md](docs/how-it-works.md#optional-pir-sleep)).

## Documentation

Documentation lives in `docs/`, next to the code, so the guide and the
firmware cannot drift apart. Each file in `docs/` is written as a
standalone page, and every page ends with Previous / Contents / Next
links in the order of the Getting started list above, so you can read
straight through or jump to a single page.

## Contributing

Enable the local guardrail hooks once with `git config core.hooksPath .githooks`.
Run `python scripts/check.py` before pushing (`--quick` skips the compile check).
See [AGENTS.md](AGENTS.md) for the rules.

## Sources

Synthesized from MakerGuides, Instructables, LastMinuteEngineers,
Espressif documentation, and Open-Meteo — full list and image credits
in [docs/sources.md](docs/sources.md). Photos and wiring diagrams in
`assets/` are from those guides, credited under each image; none are
photos of this specific build. Weather data: Open-Meteo.

---

[Next: Parts →](docs/parts.md)
