# Build order — test each stage before the next

Don't wire everything and then debug everything. Build in this order;
each stage ends with a check that proves it works before the next part
goes on. Total wiring is only ~15 jumpers, so this goes fast.

1. **OLED only.** Wire just the display (4 wires: SDA GPIO 4, SCL
   GPIO 5, [wiring.md](wiring.md)). Upload a minimal test only:
   `display.begin(SSD1306_SWITCHCAPVCC, 0x3C)`, print "Hello".
   Do not use the full sketch for this stage: with the shipped
   placeholder WiFi credentials it waits out its 30 s WiFi timeout
   before drawing anything, so "text on the OLED" is not a stage-1
   test for the full sketch. (If Serial shows nothing at all, check
   USB CDC On Boot is enabled — see
   [libraries-and-setup.md](libraries-and-setup.md).)
   - **Test:** text on the OLED, and Serial Monitor (115200 baud) shows
     no "OLED not found" error. Black screen? Jump to
     [troubleshooting.md](troubleshooting.md) before continuing.
2. **WiFi + clock + encoder.** Fill in the WiFi credentials,
   location, and time-zone settings from
   [libraries-and-setup.md](libraries-and-setup.md), wire the
   encoder now (5 wires: CLK 6, DT 7, SW 10) — it has to come before
   the DHT and weather stages, because those stages need you to
   rotate to their pages — upload, and stay on page 1 (the clock is
   the default page).
   - **Test:** the clock shows the correct local time within a few
     seconds of boot and the seconds tick. Wrong by whole hours =
     time-zone string. Stuck at `--:--` = WiFi connected but NTP not
     yet synced; a WiFi failure instead shows "Connecting WiFi..."
     then the clock page with `--:--`, and Serial prints
     "WiFi: connection failed (30 s timeout)". Turning the knob
     cycles pages 1→2→3→4→1, the other way goes backwards, and a
     press jumps to Summary and back to Clock — a press does not
     step through pages. Counts backwards? Swap CLK and DT — that's
     a fix, not a failure. Double-steps or missed steps? See the
     "Encoder double-steps or skips" row in
     [troubleshooting.md](troubleshooting.md).

     ![Serial Monitor output showing encoder direction and counter as the knob is turned](https://lastminuteengineers.com/wp-content/uploads/iot/Rotary-Encoder-Output-On-Serial-Monitor.png)

     What a working encoder looks like in the Serial Monitor, from the
     LastMinuteEngineers tutorial: direction (CW/CCW) and a counter that
     goes up one way and down the other. Adding a temporary
     `Serial.print` of the page number should show the same behaviour.
     Screenshot: LastMinuteEngineers.
3. **Add the DHT11.** Power down, add its 3 wires (DATA to GPIO 3),
   power up, rotate to the Indoor page.
   - **Test:** plausible room readings appear within ~4 seconds and
     update every 2 s. Breathe on the sensor — humidity should climb.
     "No reading" persisting = see the DHT row in
     [troubleshooting.md](troubleshooting.md).
4. **Outdoor weather.** No new wiring — rotate to the outdoor page.
   Also paste the Open-Meteo URL from [how-it-works.md](how-it-works.md)
   (with the configured coordinates and time zone filled in) into a
   browser once, to see the JSON the code is parsing.
   - **Test:** the page fills in on the first fetch (it runs once at
     boot) and the numbers match the browser's JSON. Serial Monitor
     prints the HTTP code if the fetch fails.
5. **Add the potentiometer.** Power down, wire the pot (ends to
   3V3/GND, wiper to GPIO 1), power up.
   - **Test:** turning the pot sweeps the OLED from dim to full
     brightness, smoothly, on every page. The Summary page's "Bright"
     value should track it from ~8 to 255.
6. **Leave it running.** Park it on the Clock page, powered over
   USB-C. Check it again in 15 minutes.
   - **Test:** clock still correct, weather page has refreshed at least
     once, indoor page still updating, knob and pot still responsive
     (this is the check that would catch a blocking `delay()` if one
     ever crept in).
7. **Optional: PIR wake/sleep.** Wire the PIR (5 V in, OUT to
   GPIO 0), set `USE_PIR` to 1 in the sketch, re-upload.
   - **Test:** wave at it — display on. Leave the room — display
     blanks 60 s after the PIR last reads HIGH, plus whatever delay
     the module's own delay potentiometer is set to (set it to
     minimum for the stated behaviour). Note the HC-SR501 itself
     needs a minute to settle after power-up and will trigger
     spuriously until then.

---

[← Previous: How it works](how-it-works.md) · [Contents](../README.md) · [Next: Hardware tests →](hardware-tests.md)
