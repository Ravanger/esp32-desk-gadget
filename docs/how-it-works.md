# How each piece works

## The clock — NTP over WiFi

The ESP32 has no battery-backed clock, so on boot it asks an internet
time server (NTP, pool.ntp.org) for the current UTC time, then applies
the America/Toronto rules — EST/EDT with North American daylight-saving
switch dates — via the timezone string
`"EST5EDT,M3.2.0,M11.1.0"`. After that one sync, the ESP32's internal
timer keeps time on its own and the sketch just reads it once a second
with `getLocalTime()`. Unplug the internet and the clock keeps ticking;
unplug the power and it re-syncs on the next boot.

## Indoor readings — the DHT11, and its two rules

The DHT11 is a one-wire digital sensor that reports temperature
(±2 °C) and humidity (±5%). It's good enough for "is the room hot and
dry", which is all a desk gadget needs. Two rules from hard experience
in the source guides, both baked into the code:

- **Read it at most every 2 seconds.** The DHT11 needs about a second
  to recover between reads; poll it faster and you get stale or failed
  readings. The sketch reads on a 2-second `millis()` timer.
- **Always check for failure.** A failed read returns NaN ("not a
  number"). The sketch tests `isnan()` and simply keeps showing the
  last good values instead of printing `nan` on your desk.

And a rule for the whole program: **no long `delay()` calls.** The
original MakerGuides loop sleeps for 10 minutes between weather fetches,
which is fine for a single-screen station — but here it would freeze the
encoder and the clock. Every recurring job in this sketch (DHT, weather,
redraw, pot) runs off its own `millis()` timer, so everything stays
responsive at once.

## Outdoor weather — Open-Meteo, no key

The MakerGuides pattern is: WiFi connects, HTTPClient downloads a JSON
document, ArduinoJson picks the fields out of it, the OLED displays
them, and the whole thing repeats every 10 minutes — weather doesn't
change faster than that, and hammering an API gains nothing. This build
keeps that pattern exactly, but swaps OpenWeatherMap (account + API
key) for Open-Meteo: free for non-commercial use (roughly 10,000
requests a day — this gadget uses 144), no signup, no key in the URL.
The exact request, already set to Toronto:

```
https://api.open-meteo.com/v1/forecast?latitude=43.65&longitude=-79.36
  &current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m
  &timezone=America%2FToronto
```

From the reply, the sketch reads
`doc["current"]["temperature_2m"]`, `["relative_humidity_2m"]`,
`["weather_code"]`, and `["wind_speed_10m"]`. Paste the URL into a
browser first and look at the raw JSON — seeing the structure once
makes the parsing code obvious.

The one quirk: Open-Meteo doesn't send a text description, it sends a
numeric WMO weather code. The sketch translates it with this table:

| Code | Meaning | Code | Meaning |
| ---- | ------- | ---- | ------- |
| 0 | Clear sky | 51 / 53 / 55 | Drizzle (light / moderate / dense) |
| 1 | Mainly clear | 61 / 63 / 65 | Rain (slight / moderate / heavy) |
| 2 | Partly cloudy | 71 / 73 / 75 | Snow (slight / moderate / heavy) |
| 3 | Overcast | 80 / 81 / 82 | Rain showers (slight / moderate / violent) |
| 45 | Fog | 95 | Thunderstorm |
| 48 | Icy fog (rime fog) | 96 / 99 | Thunderstorm with hail |

## Navigation — the rotary encoder

An incremental rotary encoder outputs two square waves, CLK and DT,
90° out of phase. Both look identical on their own; the trick is that
which one leads tells you the direction. Turn clockwise and CLK changes
first; turn counter-clockwise and DT changes first. That phase
relationship is the entire mechanism — inside, a slotted disc and
contacts generate the two offset signals as you turn.

![Diagram of a rotary encoder's internal structure showing the slotted disc and contacts that generate the CLK and DT signals](../assets/encoder-internal.png)

Inside the encoder: the rotating disc and contacts that produce the two
phase-shifted signals. Diagram: LastMinuteEngineers, ESP32 Rotary
Encoder Tutorial.

Two ways to read it, both covered by the LastMinuteEngineers tutorial:

- **Polling (used in this sketch):** watch CLK in the main loop; when
  it changes, read DT. If DT differs from CLK's new state, you turned
  one way; if it matches, the other. Simple, and plenty fast here
  because the loop never blocks.
- **Interrupt + decode table:** attach interrupts to both pins and
  feed the 4-bit (old CLK/DT, new CLK/DT) state through a 16-entry
  quadrature table. More robust at high spin speeds and on busier
  programs — the upgrade path if the knob ever feels like it misses
  steps.

Three practical details: the pins are configured INPUT_PULLUP (the
module's signals are open-collector style); the push button gets a
200 ms debounce guard so one press never registers as three; and if
your knob turns out to count backwards, don't debug — just swap the CLK
and DT wires (or swap the two pin numbers in code). Both are equally
correct.

## Dimming — there is no backlight to dim

An OLED pixel makes its own light, so there's no backlight knob.
Brightness is set by the SSD1306's contrast register: send
`SSD1306_SETCONTRAST` followed by a value from 0–255. (The ThingPulse
driver exposes the same thing as `setContrast()` / `setBrightness()`.)
The sketch reads the pot on GPIO 34 — the ESP32 ADC returns 0–4095 —
and maps it straight onto 0–255, with a floor of 8 so the screen never
goes fully invisible mid-adjustment.

Two warnings: at very low contrast the display can look patchy rather
than elegantly dim — that's the panel, not your wiring — and for true
"off", use the display on/off commands instead, which is exactly what
the optional PIR sleep does.
