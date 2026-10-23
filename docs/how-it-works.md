# How each piece works

## The clock — NTP over WiFi

The ESP32-C3 has no battery-backed clock, so on boot it asks an
internet time server (NTP, `pool.ntp.org`) for the current UTC time,
then converts it to local time with the POSIX time-zone string set in
the sketch (for example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time).
That string carries both the standard/daylight offsets and the
daylight-saving switch dates, so no separate DST handling is needed.

![Diagram of communication between a client and an NTP server over UDP](https://circuitdigest.com/sites/default/files/inlineimages/u/Communication-between-UDP-and-NTP-server.png)

How NTP works, conceptually: the client asks a time server over UDP
(port 123) and the server answers with the time of day. Diagram:
CircuitDigest — note this is a concept diagram, not wiring for this
build (CircuitDigest's own clock uses SPI; this build uses I2C).

After that one sync, the chip's internal timer keeps time on its own
and the sketch reads it once a second with `getLocalTime()`. Lose the
internet connection and the clock keeps ticking; lose power and it
re-syncs on the next boot.

## Indoor readings — the DHT11, and its limits

The DHT11 is a one-wire digital sensor. Verified specifications
(datasheets vary slightly on humidity range — 20–80 % RH is the
conservative figure):

| Parameter | Value |
| --------- | ----- |
| Operating voltage | 3.3–5.5 V |
| Temperature range | 0–50 °C, ±2 °C accuracy |
| Humidity range | 20–80 % RH, ±5 % RH accuracy |
| Sampling rate | 1 Hz maximum (one reading per second) |
| Current | ~0.3 mA measuring, ~60 µA standby |

That accuracy is fine for "is the room hot and dry", which is all a
desk gadget needs — but it is not a precision instrument. A reading of
20 °C means the real temperature is plausibly anywhere from 18 °C to
22 °C. For tighter accuracy or outdoor use, a DHT22 is a drop-in
replacement (same wiring, same library, change `DHT11` to `DHT22` in
the sketch).

Two rules, both baked into the code:

- **Read it at most every 2 seconds.** The sensor needs about a
  second to recover between reads; polling faster produces stale or
  failed readings. The sketch reads on a 2-second `millis()` timer,
  comfortably inside the limit.
- **Always check for failure.** A failed read returns NaN ("not a
  number"). The sketch tests `isnan()` and keeps showing the last
  good values instead of printing `nan` on the screen.

And a rule for the whole program: **no long `delay()` calls in the
main loop.** A single-screen station can sleep for 10 minutes between
weather fetches, but here that would freeze the encoder and the clock.
Every recurring job in this sketch (DHT, weather, redraw, pot) runs off
its own `millis()` timer, so everything stays responsive at once.
One exception to know about: the weather fetch itself is a blocking
HTTP request that takes a second or two, so encoder turns during that
brief window can be missed. That is an accepted trade-off, not a bug
to chase — the fetch only happens once every 10 minutes.

## Outdoor weather — Open-Meteo, no key

The pattern, taken from the MakerGuides weather station: WiFi connects,
HTTPClient downloads a JSON document, ArduinoJson picks the fields out
of it, the OLED displays them, and the whole thing repeats every
10 minutes — weather does not change faster than that, and polling an
API more often gains nothing. This build keeps that pattern exactly,
but uses Open-Meteo instead of OpenWeatherMap: free for
non-commercial use (about 10,000 requests a day — this gadget uses
144), no signup, no key in the URL.

The request is built from the sketch's location settings:

```
https://api.open-meteo.com/v1/forecast?latitude=<LAT>&longitude=<LON>
  &current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m
  &timezone=<IANA_TIMEZONE_URL_ENCODED>
```

From the reply, the sketch reads
`doc["current"]["temperature_2m"]`, `["relative_humidity_2m"]`,
`["weather_code"]`, and `["wind_speed_10m"]`. Paste the URL into a
browser first and look at the raw JSON — seeing the structure once
makes the parsing code obvious.

The one quirk: Open-Meteo does not send a text description, it sends
a numeric weather code. Open-Meteo uses a subset of WMO codes (not the
full 00–99 present-weather set), and the sketch translates the full
subset with this table:

| Code | Meaning | Code | Meaning |
| ---- | ------- | ---- | ------- |
| 0 | Clear sky | 56 / 57 | Freezing drizzle (light / moderate-heavy) |
| 1 | Mainly clear | 61 / 63 / 65 | Rain (slight / moderate / heavy) |
| 2 | Partly cloudy | 66 / 67 | Freezing rain (light / moderate-heavy) |
| 3 | Overcast | 71 / 73 / 75 | Snow (slight / moderate / heavy) |
| 45 | Fog | 77 | Snow grains |
| 48 | Icy fog (rime fog) | 80 / 81 / 82 | Rain showers (slight / moderate / violent) |
| 51 / 53 / 55 | Drizzle (light / moderate / dense) | 85 / 86 | Snow showers (slight / moderate-heavy) |
| 95 | Thunderstorm | 96 / 99 | Thunderstorm with hail (slight / heavy) |

Any code outside this table shows as `-` on the screen, which is the
safe fallback if Open-Meteo ever adds a code.

## Navigation — the rotary encoder

An incremental rotary encoder outputs two square waves, CLK and DT,
90° out of phase. Both look identical on their own; the trick is that
which one leads tells you the direction. Turn clockwise and CLK changes
first; turn counter-clockwise and DT changes first. That phase
relationship is the entire mechanism — inside, a slotted disc and
contacts generate the two offset signals as the knob turns.

![Diagram of a rotary encoder's internal structure showing the slotted disc and contacts that generate the CLK and DT signals](../assets/encoder-internal.png)

Inside the encoder: the rotating disc and contacts that produce the two
phase-shifted signals. Diagram: LastMinuteEngineers, ESP32 Rotary
Encoder Tutorial.

![Animation of a rotary encoder's internal disc rotating and its CLK and DT signals changing](https://lastminuteengineers.com/wp-content/uploads/arduino/rotary-encoder-working-animation.gif)

The same mechanism in motion: as the disc turns, CLK and DT make
contact in sequence, one always leading the other. Animation:
LastMinuteEngineers.

![CLK and DT output pulses during clockwise rotation](https://lastminuteengineers.com/wp-content/uploads/arduino/rotary-encoder-output-pulses-in-clockwise-rotation.png)

Clockwise: CLK leads DT. Diagram: LastMinuteEngineers.

![CLK and DT output pulses during counter-clockwise rotation](https://lastminuteengineers.com/wp-content/uploads/arduino/rotary-encoder-output-pulses-in-anticlockwise-rotation.png)

Counter-clockwise: DT leads CLK — the phase relationship is reversed,
and that reversal is how the code knows which way the knob turned.
Diagram: LastMinuteEngineers.

Two ways to read it, both covered by the LastMinuteEngineers tutorial:

- **Polling (used in this sketch):** watch CLK in the main loop; when
  it changes, read DT. If DT differs from CLK's new state, the knob
  turned one way; if it matches, the other. Simple, and fast enough
  here because the loop never blocks for long (see the weather-fetch
  caveat above).
- **Interrupt + decode table:** attach interrupts to both pins and
  feed the 4-bit (old CLK/DT, new CLK/DT) state through a 16-entry
  quadrature table. More robust at high spin speeds and on busier
  programs — the upgrade path if the knob ever feels like it misses
  steps.

Three practical details: the pins are configured INPUT_PULLUP (the
module's signals are open-collector style); the push button gets a
200 ms debounce guard so one press never registers as three; and if
the knob counts backwards, just swap the CLK and DT wires (or swap the
two pin numbers in code). Both are equally correct fixes.

## Dimming — there is no backlight to dim

An OLED pixel makes its own light, so there is no backlight knob.
Brightness is set by the SSD1306's contrast register: send
`SSD1306_SETCONTRAST` followed by a value from 0–255. (The ThingPulse
driver exposes the same thing as `setContrast()` / `setBrightness()`.)
The sketch reads the pot on GPIO 1 — the ESP32-C3 ADC is 12-bit, so it
returns 0–4095 — and maps it onto 0–255, with a floor of 8 so the screen
never goes fully invisible mid-adjustment.

The pot must be on an ADC1 pin (GPIO 0–4 on the C3). GPIO 5 is ADC2,
and ADC2 readings go unreliable once WiFi is running — which is
always, on this build. That is why the pot is on GPIO 1, even though
GPIO 5 is also used in this build as the I2C clock line (digital use
of GPIO 5 is fine; analog use is the problem).

Two warnings: at very low contrast the display can look patchy rather
than elegantly dim — that is the panel, not the wiring — and for true
"off", use the display on/off commands instead, which is exactly what
the optional PIR sleep does.
