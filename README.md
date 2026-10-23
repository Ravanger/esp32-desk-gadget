# ESP32 Desk Gadget

A multi-screen desktop display built around an ESP32-C3 SuperMini and
a 0.96-inch SSD1306 OLED. It shows:

- The time, synced over WiFi via NTP
- Indoor temperature and humidity from a DHT11 sensor
- Outdoor weather for a configurable location, from Open-Meteo
  (free, no API key, no account)
- A summary screen with brightness, WiFi status, and uptime

Navigation is a rotary encoder (rotate to change pages, press to jump
to the summary). A separate analog potentiometer controls screen
brightness. Power is USB-C; no software is required on the host
computer, which only supplies power.

> **Board:** ESP32-C3 SuperMini. All pin numbers in this repository
> are SuperMini pins (I2C on GPIO 4/5, encoder on 6/7/10, pot on ADC1
> GPIO 1). Pin numbers from classic ESP32 guides (21/22, 25/26/27, 34)
> do not apply to this board — see [docs/wiring.md](docs/wiring.md).

## Features

- 4 screens: Clock, Indoor, Outdoor weather, Summary
- NTP time with a configurable time zone
- Configurable weather location (latitude, longitude, time zone)
- Indoor sensing with last-good-value retention on failed reads
- OLED brightness via potentiometer (contrast control, no backlight)
- Optional PIR wake/sleep support (compile-time flag)
- No soldering required — breadboard build
- No API keys, accounts, or host-side software

## The four screens

| Screen | Shows | Data source | Refresh |
| ------ | ----- | ----------- | ------- |
| 1 · Clock | Time (HH:MM), seconds, day and date | NTP over WiFi | Every second |
| 2 · Indoor | Indoor temperature + relative humidity | DHT11 on GPIO 3 | Every 2 seconds |
| 3 · Outdoor | Outdoor temperature, humidity, condition, wind | Open-Meteo API (no key) | Every 10 minutes |
| 4 · Summary | Key values, brightness, WiFi status, uptime | All of the above | Every second |

## Hardware

See [docs/parts.md](docs/parts.md) for the full list. In short:
ESP32-C3 SuperMini, SSD1306 128×64 I2C OLED, DHT11 module, rotary
encoder module, 10K potentiometer, breadboard, jumper wires, and a
USB-C data cable (not a charge-only cable).

## Getting started

1. [Parts](docs/parts.md) — components and quantities
2. [Wiring](docs/wiring.md) — wiring table, including the I2C-pin warning
3. [Libraries & setup](docs/libraries-and-setup.md) — Arduino IDE and
   PlatformIO, plus configuration (WiFi, location, time zone)
4. [How it works](docs/how-it-works.md) — NTP clock, DHT11, Open-Meteo,
   encoder, dimming
5. [Build order](docs/build-order.md) — staged build, with a test after
   each stage
6. [Troubleshooting](docs/troubleshooting.md) — symptoms, causes, fixes
7. [Sources & credits](docs/sources.md) — guides this project draws on,
   and image credits

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
- `TIMEZONE_POSIX` — the POSIX time-zone string for local clock time
  (for example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time)

The values shipped in the sketch are an example configuration; replace
them with the target location before use.

## What this build deliberately does not need

- No host-side program: the board talks to the internet itself over
  WiFi; USB only supplies power.
- No weather API key: Open-Meteo is keyless. At one fetch every
  10 minutes, this project makes 144 requests per day, well within
  Open-Meteo's non-commercial allowance.
- No batteries and no soldering.

Optional, after the base build works: an HC-SR501 PIR on GPIO 0 can
blank the display when the room is quiet and wake it on motion. Enable
it with the `USE_PIR` flag in the sketch.

## Documentation

Documentation lives in `docs/`, next to the code, so the guide and the
firmware cannot drift apart. Each file in `docs/` is written as a
standalone page.

## Contributing

Issues and pull requests are welcome. When reporting a wiring or
firmware problem, include the board variant, the sketch version, and
the Serial Monitor output.

## Sources

Synthesized from MakerGuides, Instructables, LastMinuteEngineers,
Espressif documentation, and Open-Meteo — full list and image credits
in [docs/sources.md](docs/sources.md). Photos and wiring diagrams in
`assets/` are from those guides, credited under each image; none are
photos of this specific build. Weather data: Open-Meteo.
