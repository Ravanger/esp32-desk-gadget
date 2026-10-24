# ESPHome firmware (default)

This page covers the ESPHome firmware in
[esphome/desk_gadget.yaml](../esphome/desk_gadget.yaml), the default
firmware for the gadget. It makes the gadget a Home Assistant device
and needs a running Home Assistant for outdoor weather. If you do not
run Home Assistant, use the standalone Arduino sketch in
[firmware/desk_gadget.ino](../firmware/desk_gadget.ino) instead (see
[libraries-and-setup.md](libraries-and-setup.md)); it fetches weather
from Open-Meteo itself.

Wiring does not change. The pin assignment, the build order in
[build-order.md](build-order.md), and the bench checklist in
[hardware-tests.md](hardware-tests.md) all apply to both firmwares.
If you have already built the gadget for the sketch, flashing the
ESPHome firmware needs no rewiring.

## What you get in Home Assistant

After the device is added to Home Assistant (see below), these
entities appear:

| Entity | Source |
| ------ | ------ |
| Desk Gadget Indoor Temperature | DHT11 on GPIO 3 |
| Desk Gadget Indoor Humidity | DHT11 on GPIO 3 |
| Desk Gadget WiFi Signal | WiFi signal strength |
| Desk Gadget Uptime | Device uptime |
| Desk Gadget Button | Nav button on GPIO 10 (pressed/released) |
| Desk Gadget Motion | PIR on GPIO 0, only useful when a PIR is fitted |

The outdoor temperature, humidity, wind, and condition are imported
from Home Assistant into the device (see below). They are internal to
the device and are not re-exported back to Home Assistant.

## Setup

1. Install ESPHome (the dashboard add-on, or `pip install esphome`
   on a computer with USB access to the board). The YAML needs
   ESPHome 2026.10.0 or newer, the release it is compiled and checked
   against; `min_version` enforces this.
2. Copy [secrets.example.yaml](../esphome/secrets.example.yaml) to
   `esphome/secrets.yaml` in the same directory and fill it in.
   `secrets.yaml` is gitignored and must never be committed.
   Generate the API encryption key with:
   ```
   openssl rand -base64 32
   ```
3. Edit the substitutions at the top of
   [desk_gadget.yaml](../esphome/desk_gadget.yaml):
   - `timezone` — the IANA time-zone name for the clock. The shipped
     value is a labelled example (Toronto), same as the sketch.
   - `location_name` — the short label on the outdoor screen.
     Keep it to about 8 characters, or the outdoor header clips,
     same as the sketch.
   - `weather_entity` — your Home Assistant weather entity, for
     example `weather.home`. It must expose a `temperature`
     attribute; `humidity`, `wind_speed`, `temperature_unit`, and
     `wind_speed_unit` are shown when present.
   - `use_encoder` — `false` for the push button (default), `true`
     for a rotary encoder on CLK 6 / DT 7 / SW 10. Changing it needs
     a recompile, like `USE_ENCODER` in the sketch.
   - `use_pir` — `false` for no PIR (default), `true` for a PIR on
     GPIO 0. Changing it needs a recompile, like `USE_PIR` in the
     sketch. The Motion entity appears in Home Assistant either way;
     with `use_pir: false` it simply always reads off.
   - `wifi_tx_power` — `20dB` by default. If the board fails to join
     WiFi (a known SuperMini antenna weakness), try `8.5dB`, the
     ESPHome form of `WIFI_LOW_TX_POWER` in the sketch.
4. Validate the config before flashing:
   ```
   esphome config esphome/desk_gadget.yaml
   ```
   This needs `esphome/secrets.yaml` to exist with real values (the
   example placeholders are refused on purpose). Over-the-air
   updates are encrypted with the same `api_key`, so there is no
   separate OTA password to set.
5. Flash it:
   ```
   esphome run esphome/desk_gadget.yaml
   ```
   The first flash is over USB: plug the board into the computer
   running ESPHome with a USB-C data cable (not a charge-only cable)
   and pick the serial port when asked. Later updates go over the
   air, with no cable.
6. Add the device in Home Assistant, under Settings, Devices,
   ESPHome. It usually appears by discovery. If discovery does not
   find it (common when Home Assistant runs in a container, where
   mDNS may not cross the container network), add it manually with
   the device's IP address, or give the device a fixed address in
   the YAML, for example:
   ```yaml
   wifi:
     manual_ip:
       static_ip: 192.168.1.50
       gateway: 192.168.1.1
       subnet: 255.255.255.0
   ```
   Replace those three values with ones for your own network.
7. The outdoor page stays on "Waiting for first fetch..." until the
   device is registered in Home Assistant. That is expected:
   Home Assistant sensors only start sending once the node is added
   (see the ESPHome Home Assistant sensor docs), so add the device
   first, then check the outdoor page.

## Parity with the sketch

Every screen, control, and timing rule from the sketch is carried
over. The table below is the checkable form of that claim; anything
that deliberately differs is listed separately, below the table.

| Sketch behaviour | ESPHome form |
| ---------------- | ------------ |
| Clock, Indoor, Outdoor, Summary pages, in that order | Same four pages, same order, same content per page |
| Button steps one page per press, holding does not repeat | Same, via the GPIO binary sensor on GPIO 10 |
| Press counts only if the line was HIGH for at least 30 ms | `delayed_on_off: 30ms` filter on the button: bounce under 30 ms is ignored, at the cost of a 30 ms delay per press |
| Encoder build: rotate steps both ways, press jumps to/from Summary | Same, via the rotary encoder sensor on CLK 6 / DT 7 and SW 10 |
| Pot dims the display, contrast 8–255, changes under 5 ignored | Same: ADC on GPIO 1, clamped to 0–2500 mV, hysteresis over 4 |
| C3 ADC tops out around 2.5 V, so the top of pot travel reads full brightness | Same clamp, same note |
| DHT11 every 2.5 s, failed reads leave the last good value on screen | Same interval; ESPHome publishes NaN on a failed read and a `filter_out: nan` filter drops it, so the last good value stays (in Home Assistant too) |
| Indoor values are the mean of the last 5 good reads (`DHT_AVG_N`) | `sliding_window_moving_average` (window 5, send every 1) after `filter_out: nan`; Home Assistant receives the averaged values too |
| Clock from NTP, configurable IANA time zone, `--:--` until synced | SNTP with the `timezone` substitution, `is_valid()` guard |
| Summary: time, indoor, outdoor, brightness, WiFi status, uptime | Same six lines, same positions |
| Page dots at the bottom, header title with a rule at y = 11 | Same positions |
| PIR blanks the display 60 s after the last motion, button press, or encoder step (including 60 s after boot); motion or a press wakes it | Same rule, via a restarting 60 s `pir_blank` script; the Motion entity in Home Assistant follows the PIR output directly |
| WiFi is 2.4 GHz only | Same; the YAML says so and the C3 has no 5 GHz radio |
| No real credentials in the repo | Secrets only in gitignored `secrets.yaml` |

## Deliberate differences (read these before switching)

- **Outdoor weather comes from Home Assistant, not Open-Meteo.**
  The device no longer fetches weather itself, and the outdoor
  header reads `<location_name> - HA` instead of
  `<location_name> - OPEN-METEO`. If Home Assistant is down or the
  entity becomes unavailable, the outdoor page keeps its last values
  and the "Updated N min ago" line keeps counting, same as the
  sketch after a failed fetch. The sketch remains the build to use
  for a standalone gadget.
- **"Updated N min ago" counts from the last change, not the last
  fetch.** Home Assistant only sends the temperature when it changes,
  so a steady temperature lets the counter climb even while Home
  Assistant is up. The sketch counts from its last successful fetch,
  every 10 minutes.
- **Condition labels are mapped from Home Assistant conditions, not
  WMO codes.** Home Assistant reports conditions like `sunny`,
  `partlycloudy`, and `rainy`, with no intensity. The display maps
  them to short labels ("Clear sky", "Partly cloudy", "Rain") and
  does not claim an intensity Home Assistant did not report, except
  `pouring`, shown as "Heavy rain". A condition with no mapping shows
  as-is, so nothing is silently hidden. The WMO code table in the
  sketch and in verified-specs.md does not apply to this build.
- **Outdoor units follow Home Assistant.** The sketch always shows
  °C and km/h, from Open-Meteo. This build reads the weather
  entity's `temperature_unit` and `wind_speed_unit` attributes, so
  an imperial Home Assistant shows F and mph. Indoor values stay in
  °C, like the sketch.
- **The font is Roboto Mono, not the sketch's fixed-width font.**
  Text sits on the same baselines as the sketch's, but glyph shapes
  and widths differ, so lines are a few pixels shorter or longer.
- **No "Connecting WiFi..." splash at boot.** The sketch prints
  that line while joining WiFi; this build shows the first page as
  soon as the display updates (within a second). The clock still
  shows `--:--` until NTP syncs.
- **No halt on a missing OLED.** The sketch stops with a Serial
  message if no OLED answers at 0x3C. This build keeps running and
  reports the failure in the logs (the I2C scan is on for exactly
  this reason); the screen simply stays dark. Check wiring if that
  happens.
- **No access-point fallback.** If WiFi is down, the device keeps
  displaying (clock `--:--`, outdoor waiting), the same way the
  sketch continues after its 30 s WiFi timeout. `reboot_timeout: 0s`
  turns off ESPHome's default reboot after 15 minutes without WiFi.
  There is no setup hotspot to join.

## Troubleshooting

- **Outdoor page stuck on "Waiting for first fetch..."**: the device
  is not yet added in Home Assistant, or `weather_entity` names an
  entity that does not exist or has no temperature attribute. Add
  the device first (step 6 above), then check the entity name.
- **Clock stuck on `--:--`**: WiFi is not connected or NTP is
  blocked. Check the WiFi credentials in `secrets.yaml`, that the
  network is 2.4 GHz, and the serial logs over USB.
- **Display dark after flashing**: check the OLED wiring and that
  it answers at 0x3C (the I2C scan in the logs shows what was
  found). A panel sold as SSD1306 is sometimes an SH1106 instead;
  that needs its own driver model, same trap as the sketch.
- **Encoder double-steps**: try `resolution: 2` on the rotary
  encoder sensor in the YAML and recompile.
- **Pot does nothing at the top of travel**: expected. The C3 ADC
  tops out around 2.5 V, so the top roughly 24% of travel reads full
  brightness. See the parity table above.
- **Device not discovered in Home Assistant**: add it manually with
  its IP address, or set a fixed address with `manual_ip` as shown
  in step 6 above.
- **Display blanks 60 s after boot with a PIR fitted**: expected
  when nothing moves, same as the sketch. If it blanks while you are
  in front of it, check the PIR wiring against wiring.md and the
  module's sensitivity setting.

## Guardrails

`python scripts/check.py` checks the ESPHome files too: the YAML
exists, it assigns each frozen pin to the same role as the sketch
and uses no other GPIO, a secrets example exists, and `secrets.yaml`
is gitignored. When the `esphome` tool is installed, the full run
(not `--quick`) also copies the YAML next to throwaway secrets under
the gitignored `esphome/.esphome/check/` and requires
`esphome config` to pass, so no real `secrets.yaml` is needed. When
the tool is missing, that step prints SKIP instead of failing, so
Arduino-only users are not blocked by a tool they do not have.
Build output stays local and gitignored; never commit it or
`secrets.yaml`. The link and image scan in check.py skips ESPHome's
local build output under `.esphome/`, because it holds third-party
component READMEs whose hotlinked images and relative links would
otherwise trip it.

Validation status: see the ESPHome entry under
[Tested toolchain](verified-specs.md#tested-toolchain).

## Sources

- ESPHome SSD1306 display docs:
  https://esphome.io/components/display/ssd1306.html
- ESPHome Home Assistant sensor docs (importing states and
  attributes, and the note that the node must be registered first):
  https://esphome.io/components/sensor/homeassistant/
- ESPHome Home Assistant text sensor docs:
  https://esphome.io/components/text_sensor/homeassistant/

---

[← Previous: Wiring](wiring.md) · [Contents](../README.md) · [Next: Libraries & setup →](libraries-and-setup.md)
