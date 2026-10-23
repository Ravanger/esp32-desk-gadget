# Build order — test each stage before the next

Don't wire everything and then debug everything. Build in this order;
each stage ends with a check that proves it works before the next part
goes on. Total wiring is only ~15 jumpers, so this goes fast.

1. **OLED only.** Wire just the display (4 wires, [wiring.md](wiring.md)).
   Upload a minimal test: `display.begin(SSD1306_SWITCHCAPVCC, 0x3C)`,
   print "Hello" — or just upload the full sketch; it initialises the
   OLED first and prints an error to Serial if the display isn't found.
   - **Test:** text on the OLED, and Serial Monitor (115200 baud) shows
     no "OLED not found" error. Black screen? Jump to
     [troubleshooting.md](troubleshooting.md) row 1 before continuing.
2. **WiFi + clock.** Fill in your WiFi credentials, upload, and turn to
   page 1 (the clock is the default page).
   - **Test:** the clock shows the correct Toronto time within a few
     seconds of boot and the seconds tick. Wrong by whole hours =
     timezone string; stuck at `--:--` = WiFi or NTP blocked.
3. **Add the DHT11.** Power down, add its 3 wires, power up, rotate to
   the Indoor page.
   - **Test:** plausible room readings appear within ~4 seconds and
     update every 2 s. Breathe on the sensor — humidity should climb.
     "No reading" persisting = [troubleshooting.md](troubleshooting.md)
     row 2.
4. **Outdoor weather.** No new wiring — rotate to the Toronto page.
   Also paste the Open-Meteo URL from [how-it-works.md](how-it-works.md)
   into a browser once, so you've seen the JSON the code is parsing.
   - **Test:** the page fills in on the first fetch (it runs once at
     boot) and the numbers match the browser's JSON. Serial Monitor
     prints the HTTP code if the fetch fails.
5. **Add the rotary encoder.** Power down, add its 5 wires, power up.
   - **Test:** turning the knob cycles pages 1→2→3→4→1, the other way
     goes backwards, and a press jumps to Summary and back to Clock.
     Counts backwards? Swap CLK and DT — that's a fix, not a failure.
     Double-steps or missed steps? See
     [troubleshooting.md](troubleshooting.md) row 5.
6. **Add the potentiometer.** Power down, wire the pot (ends to
   3V3/GND, wiper to GPIO 34), power up.
   - **Test:** turning the pot sweeps the OLED from dim to full
     brightness, smoothly, on every page. The Summary page's "Bright"
     value should track it from ~8 to 255.
7. **Leave it running.** Park it on the Clock page, powered from the
   PC's USB. Check it again in 15 minutes.
   - **Test:** clock still correct, weather page has refreshed at least
     once, indoor page still updating, knob and pot still responsive
     (this is the check that would catch a blocking `delay()` if one
     ever crept in).
8. **Optional: PIR wake/sleep.** Wire the PIR (5 V in, OUT to
   GPIO 13), set `USE_PIR` to 1 in the sketch, re-upload.
   - **Test:** wave at it — display on. Leave the room — display
     blanks about 60 s after the last motion. Note the HC-SR501 itself
     needs a minute to settle after power-up and will trigger
     spuriously until then.
