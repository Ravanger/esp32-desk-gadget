# Hardware tests — staged verification

This page is a checklist, not a report: it lists the test for each
stage, the expected result, and how to measure it. Run it in order —
do not add the next stage until the current one passes. Record the
actual measured value next to each expected value; a test with no
recorded measurement is not passed.

All voltages are measured with the board powered over USB-C and a
multimeter, black lead on a SuperMini GND pin. All pins are
SuperMini GPIOs. Power off before changing any wiring (the one exception is the DHT11 data-wire test in stage 3).

## Stage 0 — Unpowered checks

- [ ] Every wire matches [wiring.md](wiring.md), checked twice.
- [ ] No 5 V wire touches a GPIO pin or the 3V3 pin. The only 5 V
      connection in the whole build is the optional PIR VCC, and only
      after the base build works.
- [ ] OLED VCC is on 3V3, not 5V. DHT11 VCC is on 3V3. Encoder power
      is on 3V3. Pot ends are on 3V3 and GND.
- [ ] No GPIO 2, 8, or 9 is wired to anything. GPIO 20/21 are left free.

## Stage 1 — Power and OLED

- [ ] Plug in USB-C. Measure SuperMini 3V3 pin: expect about 3.3 V.
      Measured: ______ V
- [ ] Upload the sketch (see [libraries-and-setup.md](libraries-and-setup.md)).
      The OLED lights and shows the clock screen.
- [ ] If the OLED stays black: run an I2C scanner sketch first.
      Expect exactly one device at 0x3C (a few modules are 0x3D —
      if you see 0x3D, change the address in the sketch, do not
      rewire). If no device appears, recheck SDA GPIO 4 / SCL
      GPIO 5, then VCC/GND.
- [ ] Measure total current (USB meter, if available): idle expect
      tens of mA; during a weather fetch expect brief TX peaks (up
      to 335 mA per datasheet Table 5-7 for the ESP32-C3 alone, plus the OLED), within
      the regulator rating of your board (which varies by clone). Measured idle:
      ______ mA, peak during fetch: ______ mA

## Stage 2 — Clock (NTP) and encoder (or button)

The encoder (or button) is tested here, before the indoor and outdoor stages,
because those stages need you to rotate (or press, in button
mode) to their pages.

- [ ] Serial Monitor shows "WiFi: connecting..." then
      "WiFi: connected" on a 2.4 GHz network (the ESP32-C3 has no
      5 GHz radio). A "WiFi: connection failed (30 s timeout)"
      message means this stage has not passed — the clock will
      show `--:--` until NTP syncs.
- [ ] Clock screen time matches a known clock (phone) within a
      second, and the date is correct for the configured time zone.
- [ ] After a power cycle, the clock resyncs on its own — no
      button press, no re-upload. (It shows `--:--` until the first
      NTP sync and never blocks the display.)
- [ ] Encoder build: rotate the encoder: pages change in order Clock → Indoor →
      Outdoor → Summary, and back the other way when rotated the
      other way. If it counts backwards, swap CLK/DT (GPIO 6/7).
- [ ] Encoder build: press the encoder: the display jumps to the Summary page;
      press again: back to Clock. A press does not step through
      pages, and holding it down does not re-trigger.
- [ ] Button-mode build only (`USE_BUTTON_NAV` 1, no encoder): each
      press steps the pages in order, Clock → Indoor → Outdoor →
      Summary, then wraps back to Clock. Holding the button down does
      not repeat the step. One press is exactly one page step: no
      double steps and no skipped pages.

## Stage 3 — Indoor (DHT11)

- [ ] Indoor screen shows a temperature and humidity reading, not
      "No reading" (before the first good read) or NaN.
- [ ] Compare against a known thermometer/hygrometer in the same
      room: expect agreement within the DHT11 limits, ±2 °C and
      ±5 % RH. Larger disagreement is a sensor or placement
      problem, not a reason to "calibrate" the reading in code.
- [ ] While the gadget is running, unplug the DHT11 DATA wire: the
      indoor screen must keep showing the last good reading, not
      jump to 0 or NaN. (After a reboot with the wire unplugged
      there is no last value, so it shows "No reading".) Reconnect
      it: readings resume within a few seconds (the sketch reads
      every 2.5 seconds; the DHT11 maximum rate is 1 Hz).
      This is the one live change allowed: pulling only the DATA jumper
      (never VCC or GND) and plugging it back in is safe because it is a
      3.3 V signal line.

## Stage 4 — Outdoor (Open-Meteo)

- [ ] Outdoor screen fills in shortly after WiFi connects
      (the first fetch runs as soon as WiFi is up, then every 10
      minutes after a success and every 60 s after a failure). A
      failing fetch typically blocks for a few seconds and at worst
      about 12 s plus DNS lookup time, so encoder or button input during
      a fetch is missed. The page shows "Updated N min ago".
- [ ] Temperature, humidity, condition, and wind match Open-Meteo
      for the configured location when the same URL from
      [how-it-works.md](how-it-works.md) is opened in a browser.
- [ ] With WiFi off from boot (or the wrong WiFi password), the
      outdoor screen shows "Waiting for first fetch..." — no
      invented data. If WiFi drops after a successful fetch, the
      last fetched values stay displayed (the sketch keeps the
      last good values on a failed fetch), so a stale display
      after a drop is expected, not a fault; "Updated N min ago"
      shows its age. Recovery happens on the next retry (60 s
      after a failure) once WiFi returns, not instantly.

## Stage 5 — Pot

- [ ] Turn the pot end to end: the OLED brightness changes
      smoothly, with no flicker. The Summary page's "Bright" value
      runs from about 8 to about 255.
- [ ] Measure the pot wiper (GPIO 1) with a multimeter: expect a
      smooth sweep from ~0 V to about 3.3 V, never above 3.3 V.
      Measured low: ______ V, high: ______ V
- [ ] At the dimmest setting the display may look patchy — that is
      a panel trait at very low contrast, not a wiring fault. For
      true "off", use the display on/off commands (see
      [how-it-works.md](how-it-works.md)). Note the ADC range is
      0–2500 mV, so the top ~24% of pot travel (above about 2.5 V at
      the wiper) is full brightness — that is expected, not a
      fault. Optionally, a 3.3 kΩ resistor in series between 3V3 and
      pot end 1 limits the wiper to about 2.48 V so the full travel
      is usable.

## Stage 6 — Optional PIR (only after stages 1–5 pass)

- [ ] PIR VCC is on 5V, OUT on GPIO 0, GND on GND. Measure OUT with
      no motion: expect ~0 V; with motion: expect about 3.3 V.
- [ ] Set `USE_PIR` to 1, re-upload, and wait a minute after
      power-up: the HC-SR501 triggers spuriously until it settles.
- [ ] Wave at it: display on. Leave the room: the display
      blanks 60 s after the PIR's output drops (see [how-it-works.md](how-it-works.md#optional-pir-sleep)).
      Turning or pressing the encoder (or pressing the button in button mode) also wakes it.

## If a stage fails

Stop at that stage. Do not "fix" it by changing a pin in the sketch
to match a miswired board, or by changing a spec in a doc to match
a wrong reading — fix the wiring or the code, then re-run that
stage from the top. Note the failure, the measurement, and the fix
in the build log; that note is what turns a one-off bench session
into a verified guide.

---

[← Previous: Build order](build-order.md) · [Contents](../README.md) · [Next: Troubleshooting →](troubleshooting.md)
