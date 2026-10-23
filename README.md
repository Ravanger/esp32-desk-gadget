# ESP32 Desk Gadget: Clock, Room & Weather on One Little Screen

A multi-screen desktop display built from the ESP32 starter kit and the
45-in-1 sensor kit. It shows the time, your room's temperature and humidity,
and Toronto's outdoor weather from the internet — powered by USB from your
PC, with nothing to install on the PC, no account, and no API key.

- **Time to build:** ~1 evening
- **Soldering:** none — breadboard only
- **Cost:** $0, all parts on hand
- **Power:** micro USB from PC
- **Weather:** Open-Meteo, no key

## The four screens

| Screen | Shows | Data source | Refresh |
| ------ | ----- | ----------- | ------- |
| 1 · Clock | Time (HH:MM), seconds, day and date | NTP over WiFi, America/Toronto | Every second |
| 2 · Indoor | Room temperature + relative humidity | DHT11 on GPIO 4 | Every 2 seconds |
| 3 · Toronto weather | Outdoor temp, humidity, condition, wind | Open-Meteo API (no key) | Every 10 minutes |
| 4 · Summary / settings | All key numbers at a glance, brightness value, WiFi status, uptime | Everything above | Every second |

Rotate the rotary encoder to move through pages, press it to jump to
Summary and back to Clock. A separate analog potentiometer does one job
only: brightness.

## Start here

1. [Parts](docs/parts.md) — everything, with quantities and where it came from
2. [Wiring](docs/wiring.md) — the full wiring table, including the I2C-pin warning
3. [Libraries & setup](docs/libraries-and-setup.md) — Arduino IDE and PlatformIO
4. [How it works](docs/how-it-works.md) — NTP clock, DHT11, Open-Meteo, encoder, dimming
5. [Build order](docs/build-order.md) — 8 stages, with a test at the end of each one
6. [Troubleshooting](docs/troubleshooting.md) — symptoms, causes, fixes
7. [Sources & credits](docs/sources.md) — the guides this is synthesized from, and photo credits

Then upload the sketch:

- [firmware/desk_gadget.ino](firmware/desk_gadget.ino) — the complete sketch.
  Fill in only your WiFi name and password at the top.

## What this build deliberately doesn't need

No program on your PC (the ESP32 talks to the internet itself over WiFi —
the PC only supplies USB power). No OpenWeatherMap account or API key —
the MakerGuides weather-station pattern is kept, but the data source is
swapped to Open-Meteo, which is keyless. No batteries, no soldering.

Optional extra, later: an HC-SR501 PIR (from the starter kit) on GPIO 13
wakes the display when you sit down and blanks it when you leave — the
sketch has a switch for it (`USE_PIR`).

## A note on the wiki

This repo uses `docs/` as its documentation pages instead of a separate
GitHub Wiki, so the guide and the code stay in the same place and can't
drift apart. Each file in `docs/` is written as a standalone page, so any
of them can be copied into the Wiki verbatim if you ever want one.

## Sources

Synthesized from MakerGuides, Instructables, LastMinuteEngineers, and
Open-Meteo — full list and photo credits in
[docs/sources.md](docs/sources.md). Photos and wiring diagrams in
`assets/` are theirs, credited under each image — none are photos of
this build. Weather data: Open-Meteo. Times: America/Toronto.
