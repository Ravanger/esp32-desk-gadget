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

WiFi is not waited on forever: after a 30 s timeout the sketch
continues anyway and prints "WiFi: connection failed (30 s timeout)"
to Serial (or "WiFi: connected" on success). A WiFi failure therefore
shows as the clock page with `--:--` — WiFi connected but NTP not
yet synced shows the same `--:--` — plus "WiFi DOWN" on the Summary
page, not a blank screen. NTP and the 10-minute weather fetch keep
working in the background, so both recover on their own when WiFi
comes up.

## Indoor readings — the DHT11, and its limits

The DHT11 is a one-wire digital sensor. Verified specifications
— with one disagreement recorded, not resolved: datasheet summaries
disagree on humidity range (20–80 % RH, 20–90 % RH, and up to 95 %
all appear), on current (about 0.3 mA measuring, up to 2.5 mA during
conversion), and on the supply low end (3.3 V vs 3.5 V). The figures
below use the conservative humidity range and the larger current
for the power budget:

| Parameter | Value |
| --------- | ----- |
| Operating voltage | 3.3–5.5 V (some datasheets 3.5–5.5 V; 3V3 power is at the low edge — if readings are flaky, do NOT move the pull-up to 5 V, which would put 5 V on a C3 GPIO) |
| Temperature range | 0–50 °C, ±2 °C accuracy |
| Humidity range | 20–80 % RH, ±5 % RH accuracy (conservative; other summaries say 20–90 %) |
| Sampling rate | 1 Hz maximum (one reading per second) |
| Current | ~0.3 mA measuring, ~60 µA standby, up to 2.5 mA during conversion (use 2.5 mA for the power budget) |

That accuracy is fine for "is the room hot and dry", which is all a
desk gadget needs — but it is not a precision instrument. A reading of
20 °C means the real temperature is plausibly anywhere from 18 °C to
22 °C. For tighter accuracy or outdoor use, a DHT22 is a drop-in
replacement (same wiring, same library, change `DHT11` to `DHT22` in
the sketch) with three caveats: range −40 °C to +80 °C, ±0.5 °C,
0–100 % RH, and a sampling period of at least 2 seconds (0.5 Hz max)
— the sketch's 2-second interval is exactly at that limit, so
"drop-in" is true only if the interval is not shortened.

Two rules, both baked into the code:

- **Read it at most every 2 seconds.** The sensor needs about a
  second to recover between reads; polling faster produces stale or
  failed readings. The sketch reads on a 2-second `millis()` timer,
  comfortably inside the limit.
- **Always check for failure.** A failed read returns NaN ("not a
  number"). The sketch tests `isnan()`: the Indoor page keeps
  showing the last good values ("No reading" before the first good
  read), and the Summary page shows "In --" until the first good
  read, instead of printing `nan`.

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

The request is built from the sketch's location settings, with
coordinates sent to 4 decimal places (about 11 m precision — the
sketch used to send 2, about 1 km, which silently rounded any
configured location):

```
https://api.open-meteo.com/v1/forecast?latitude=<LAT>&longitude=<LON>
  &current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m
  &timezone=<IANA_TIMEZONE>
```

The time-zone name is appended raw, not URL-encoded: a slash in
`America/Toronto` is accepted unencoded in a query string by
Open-Meteo. The sketch sends no unit parameters, so the wind label
"km/h" on the display is correct only under Open-Meteo's defaults
(Celsius, km/h) — if a unit parameter is ever added, the display
label must change with it.

From the reply, the sketch reads
`doc["current"]["temperature_2m"]`, `["relative_humidity_2m"]`,
`["weather_code"]`, and `["wind_speed_10m"]`. Paste the URL into a
browser first and look at the raw JSON — seeing the structure once
makes the parsing code obvious.

The one quirk: Open-Meteo does not send a text description, it sends
a numeric weather code. Open-Meteo uses a subset of WMO codes (not the
full 00–99 present-weather set), and the sketch translates each code
to its own label — not grouped intensities — with this table
(official Open-Meteo labels):

| Code | Meaning | Code | Meaning |
| ---- | ------- | ---- | ------- |
| 0 | Clear sky | 56 | Light freezing drizzle |
| 1 | Mainly clear | 57 | Dense freezing drizzle |
| 2 | Partly cloudy | 61 | Slight rain |
| 3 | Overcast | 63 | Moderate rain |
| 45 | Fog | 65 | Heavy rain |
| 48 | Depositing rime fog | 66 | Light freezing rain |
| 51 | Light drizzle | 67 | Heavy freezing rain |
| 53 | Moderate drizzle | 71 | Slight snowfall |
| 55 | Dense drizzle | 73 | Moderate snowfall |
| 77 | Snow grains | 75 | Heavy snowfall |
| 80 | Slight rain showers | 85 | Slight snow showers |
| 81 | Moderate rain showers | 86 | Heavy snow showers |
| 82 | Violent rain showers | 95 | Thunderstorm |
| 96 | Thunderstorm with slight hail | 97 | Heavy thunderstorm |
| 99 | Thunderstorm with heavy hail | | |

Codes 96 and 99 are only reported by models with an explicit hail
forecast; other models report 95 and 97 instead. Codes outside this
table (including 98 in the full WMO set, which Open-Meteo does not
return) show as `-` on the screen, which is the safe fallback if
Open-Meteo ever adds a code.

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
module's signals are mechanical switches to GND with pull-ups —
functionally open-drain-like, not transistor open-collector
outputs, but the behaviour is the same: HIGH open, LOW closed);
the push button is edge-triggered (it acts only on the HIGH→LOW
transition, with a 200 ms guard, so holding it down does not
re-trigger — a press jumps to Summary, a second press returns to
Clock, it never steps through pages); and if the knob counts
backwards, just swap the CLK and DT wires (or swap the two pin
numbers in code). Both are equally correct fixes.

## Dimming — there is no backlight to dim

An OLED pixel makes its own light, so there is no backlight knob.
Brightness is set by the SSD1306's contrast register: send
`SSD1306_SETCONTRAST` followed by a value from 0–255. (The ThingPulse
driver exposes the same thing as `setContrast()` / `setBrightness()`.)
The sketch reads the pot on GPIO 1 — the ESP32-C3 ADC is 12-bit, so
it returns 0–4095 — and maps it onto 8–255, with a floor of 8 so the
screen never goes fully invisible mid-adjustment. One correction to
an earlier version of this page: at the default 11 dB attenuation,
the measurable input range is about 150 mV–3100 mV, so the reading
saturates at about 3.1 V, not 3.3 V, and reads 0 below about 150 mV.
The wiper itself still sweeps 0–3.3 V; only the top ~6% and bottom
~5% of travel are pinned, which is harmless for dimming.

The pot must be on an ADC1 pin (GPIO 0–4 on the C3). GPIO 5 is ADC2,
and ADC2 must not be used for analog input on this build at all:
ESP-IDF notes ADC2 oneshot/continuous modes are no longer supported
due to a hardware limitation, and `adc2_get_raw()` can fail while
WiFi is running — which is always, on this build. That is why the
pot is on GPIO 1, even though GPIO 5 is also used in this build as
the I2C clock line (digital use of GPIO 5 is fine; analog use is
the problem).

Two warnings: at very low contrast the display can look patchy rather
than elegantly dim — that is the panel, not the wiring — and for true
"off", use the display on/off commands instead, which is exactly what
the optional PIR sleep does.

---

[← Previous: Libraries & setup](libraries-and-setup.md) · [Contents](../README.md) · [Next: Build order →](build-order.md)
