# Verified specifications

Every number below was checked against an official datasheet or official
documentation page on 2026-10-23, not copied from a tutorial. Where sources
disagree, the disagreement is recorded instead of picking one silently. If a
fact changes, update its source and check date here too.

## ESP32-C3 chip

- Single-core 32-bit RISC-V, up to 160 MHz, 400 KB SRAM, 384 KB ROM, 22 GPIOs
  at chip level, Wi-Fi 802.11 b/g/n 2.4 GHz only, Bluetooth LE 5.0.
  No 5 GHz radio, no classic Bluetooth, no DAC, no native capacitive-touch
  peripheral (unlike the classic ESP32, which has touch pads).
  Source: Espressif ESP32-C3 Series Datasheet; Espressif ESP-IDF GPIO/ADC
  documentation. Checked 2026-10-23.
- Two 12-bit SAR ADCs. ADC1 = 5 channels, GPIO 0-4. ADC2 = 1 channel, GPIO 5.
  Source: Espressif ESP-IDF ADC documentation for ESP32-C3. Checked 2026-10-23.
- ADC2 must not be used for the pot. ADC2 is shared with Wi-Fi: `adc2_get_raw()`
  can fail between `esp_wifi_start()` and `esp_wifi_stop()`, and ESP-IDF notes
  ADC2 oneshot/continuous modes are "no longer supported, due to hardware
  limitation. The results are not stable" (ESP32-C3 errata, cited in ESP-IDF).
  This is stronger than "unreliable while Wi-Fi is on". Digital use of GPIO 5
  (for example as I2C SCL) is unaffected; only analog use is affected.
  Source: Espressif ESP-IDF ADC documentation. Checked 2026-10-23.
- ADC full scale (Arduino `analogRead()`): 12-bit, 0-4095, default attenuation
  11 dB. At 11 dB the measurable input range is about 150 mV to 3100 mV, so
  the reading saturates at about 3.1 V, not 3.3 V, and reads 0 below about
  150 mV. The pot wiper itself still sweeps 0-3.3 V; only the top ~6% and
  bottom ~5% of travel are pinned at 4095 / 0. For a dimming control this is
  harmless (the map saturates gracefully), but do not describe it as
  "0-4095 for 0-3.3 V".
  Source: Espressif Arduino-ESP32 ADC documentation (attenuation table,
  default 12-bit). Checked 2026-10-23.
- Wi-Fi current (chip datasheet, 3.3 V, 25 C, 100% duty cycle): TX peak
  335 mA (802.11b, 1 Mbps, 21 dBm), 285 mA (802.11g, 54 Mbps), 276-278 mA
  (802.11n); RX 84-87 mA; modem-sleep with CPU running 23 mA (peripherals
  disabled) to 28 mA (enabled). Module datasheets (for example ESP32-C3-MINI-1)
  quote a slightly higher TX peak, 350 mA. Use 335-350 mA as the TX peak range.
  Source: Espressif ESP32-C3 Series Datasheet v1.9, section 5.6; ESP32-C3-MINI-1
  Datasheet v2.2, section 6.4. Checked 2026-10-23.
- I2C on the C3 runs through the GPIO matrix: there are no fixed I2C pins at
  chip level, and peripheral signals can be routed to any GPIO. The sketch
  must call `Wire.begin(OLED_SDA, OLED_SCL)` explicitly, where those
  defines are 4 and 5.
  Source: Espressif ESP-IDF GPIO documentation. Checked 2026-10-23.
- Strapping pins are GPIO 2, 8, 9. Boot mode is selected mainly by GPIO 8
  and GPIO 9: SPI boot needs GPIO 9 = 1; download boot needs GPIO 8 = 1 and
  GPIO 9 = 0; GPIO 8 = 0 with GPIO 9 = 0 is invalid. GPIO 2 alone does not
  select download mode. The repo rule "never use GPIO 2, 8, or 9" is therefore
  safe, and is stricter than necessary for GPIO 2 alone.
  Source: Espressif ESP-IDF GPIO documentation (strapping pins, boot-mode
  table). Checked 2026-10-23.
- GPIO 4-7 labelled "strapping" on some board tables are a different thing:
  on internal-flash variants they are JTAG / Quad-SPI flash pins
  (GPIO 4 = MTMS/FSPIHD, GPIO 5 = MTDI/FSPIWP, GPIO 6 = MTCK/FSPICLK,
  GPIO 7 = MTDO/FSPID). Do not conflate those labels with Espressif
  strapping pins. GPIO 4, 5, 6, 7 are used by this project and are fine.
  Source: Espressif ESP-IDF GPIO documentation; ESPboards SuperMini pinout.
  Checked 2026-10-23.
- The C3 has an RTC block, but the SuperMini board has no battery-backed
  clock (no coin cell). Time is lost on power loss and re-fetched by NTP.
  Source: board-level observation; Espressif chip documentation describes
  the RTC block, not a battery. Checked 2026-10-23.

## ESP32-C3 SuperMini board

- Breaks out 13 GPIOs: 0-10, 20, 21. The two UART0 pins are left free
  for debug in this project (they are not assigned to any module).
  Chip is ESP32-C3FN4 with 4 MB in-package flash.
  Source: ESPboards ESP32-C3 Super Mini pinout; Mischianti SuperMini pinout.
  Checked 2026-10-23.
- Native USB-C, no USB-serial chip. For `Serial` over USB, Arduino IDE needs
  Tools > USB CDC On Boot > Enabled; otherwise `Serial` goes to the UART
  pins (GPIO 20/21). Board selection "ESP32C3 Dev Module"; PlatformIO board
  `esp32-c3-devkitm-1`. These are Arduino-package settings, not datasheet
  figures, confirmed across C3 board guides.
  Checked 2026-10-23.
- 3.3 V regulator rated up to about 500 mA. This is a board-page figure
  (Mischianti SuperMini page), not an Espressif chip figure, and the exact
  regulator part number was not verified. Board variants may differ; if a
  variant's regulator is weaker, the power budget below tightens.
  Source: Mischianti ESP32-C3 SuperMini pinout page. Checked 2026-10-23.
- Onboard LED variant trap: standard boards have a simple blue LED on
  GPIO 8; "Plus" variants have a WS2812 on GPIO 8. Some Plus documentation
  describes both a blue LED and a WS2812 sharing GPIO 8. Either way, GPIO 8
  is not a free GPIO in this project, and the exact variant in hand must be
  identified from the board, not assumed.
  Source: ESPboards Super Mini pinout; Mischianti SuperMini Plus page.
  Checked 2026-10-23. Variant in hand: unverified.
- One board-page line (Mischianti) says "USB-serial via CH340". That is
  wrong for the SuperMini, which has native USB and no CH340. Do not cite
  that page for USB.
  Checked 2026-10-23.

## Power budget (corrected)

The old wording ("OLED ~20 mA, DHT11 ~0.3 mA, encoder negligible, far less
than 500 mA") omitted the dominant load, the ESP32-C3 itself. Corrected:

- ESP32-C3: ~20-28 mA modem-sleep/CPU running, ~84-87 mA RX, 335-350 mA
  TX peak (brief bursts; 100% duty-cycle figure, not a continuous draw).
- OLED module: about 20 mA typical (module-dependent, varies with pixels
  lit; one module guide cites 0.06 W normal display, about 18 mA at 3.3 V).
  This is an approximate module figure, not a single SSD1306 datasheet value.
- DHT11: about 0.3 mA measuring, about 60 uA standby in the Aosong-style
  table; up to 2.5 mA during conversion in other datasheet summaries.
  Use 2.5 mA for the budget.
- PIR (if fitted): quiescent under 50 uA (some listings about 65 uA).
- Encoder, pot, TTP223: negligible (under 1 mA each in practice).
- Worst-case peak if every peak coincided: about 335-350 + 20 + 2.5 + 0.1
  = about 360-375 mA, under the 500 mA regulator with about 125-140 mA
  margin. Typical draw is far lower (tens of mA plus RX bursts). The margin
  is real but not "far less" in the peak sense, and a 500 mA USB 2.0 port
  limit is close to the same peak, so a weak USB port or cable can still
  brown out during TX bursts even though the regulator rating is not
  exceeded on paper. Measure total current at the bench stage if the
  display flickers during weather fetches.
  Sources: Espressif ESP32-C3 Series Datasheet v1.9 section 5.6; Aosong DHT11
  datasheet summaries; module guides. Checked 2026-10-23.

## SSD1306 OLED (0.96-inch, 128x64, I2C)

- 128x64 pixels, 256-step contrast control, I2C interface. Bare-chip supply:
  VDD 1.65-3.3 V, VBAT 3.3-4.2 V for the charge pump, VCC 7-15 V for panel
  driving. The bare chip is NOT 5 V-tolerant (inputs max VDD + 0.3 V).
  Source: Solomon Systech SSD1306 datasheet Rev 1.5. Checked 2026-10-23.
- I2C slave addresses from SA0: 7-bit 0x3C (0111100) and 0x3D (0111101).
  Most 4-pin modules default to 0x3C. If the I2C scanner finds nothing,
  try 0x3D before assuming a dead panel.
  Source: Solomon Systech SSD1306 datasheet. Checked 2026-10-23.
- Most 4-pin modules include an onboard regulator (commonly cited as 662K)
  and pull-up resistors, and accept 3.3-5 V. This project wires VCC to 3V3,
  which is safe for both regulated modules and 3.3 V-only modules. Do not
  generalise to "all OLED modules are 5 V-safe": a 3.3 V-only module powered
  from 5 V can be damaged, and some modules swap the VCC and GND pin order
  - always read the module silkscreen before powering it.
  Source: SSD1306 datasheet (chip limits) plus module guides. Checked
  2026-10-23. Pull-up resistor values (4.7 k vs 10 k) vary by module and
  were not verified for any specific module.
- Contrast is set with command SSD1306_SETCONTRAST plus a value 0-255;
  display on/off with SSD1306_DISPLAYON / SSD1306_DISPLAYOFF. The sketch's
  dimming (contrast value from the pot) is the datasheet's brightness
  control, not a backlight (there is no backlight on an OLED).
  Source: SSD1306 datasheet; Adafruit SSD1306 command set. Checked 2026-10-23.
- SH1106 trap (missing from the old docs, added here): SH1106 has a 132x64
  RAM buffer versus SSD1306's 128x64, different memory mapping, and needs
  its own driver (Adafruit SH110x or U8g2 U8G2_SH1106_128X64_NONAME_*).
  Running Adafruit_SSD1306 on an SH1106 panel can show a 2-pixel shift or
  garbage at the borders. Many 1.3-inch panels sold as "SSD1306" are actually
  SH1106; 0.96-inch panels are usually SSD1306, but check the driver chip,
  not the size. If the display is shifted or garbled with correct wiring
  and address, suspect SH1106 first.
  Source: SH1106 datasheet summaries; Adafruit SH110x / U8g2 driver docs.
  Checked 2026-10-23.

## DHT11

- Temperature 0-50 C, accuracy +/-2 C. Humidity: sources disagree. This repo
  previously said 20-80% RH, +/-5% RH, calling it conservative. Many
  datasheet summaries (including Aosong-derived tables) say 20-90% RH,
  +/-5% RH, and some say up to 95%. The conservative 20-80% figure is
  defensible, but 20-90% is at least as common; do not present either as
  the only datasheet value. Resolution 1 C / 1% RH.
  Source: Aosong DHT11 datasheet summaries (disagreeing). Checked 2026-10-23.
- Sampling: 1 Hz maximum in the Aosong-style table, but library guidance
  commonly says read at most once every 2 seconds. The sketch reads every
  2 seconds, which satisfies both. Do not shorten the interval.
  Source: Aosong DHT11 datasheet summaries; DHT library guidance.
  Checked 2026-10-23.
- Supply: commonly listed 3.3-5.5 V, but some datasheets list 3.5-5.5 V.
  This project powers the module from 3V3, which module guides confirm is
  standard for ESP32 builds, but it is at the low edge of the 3.5-5.5 V
  variant. If readings are flaky at 3.3 V, do NOT move the pull-up to 5 V:
  the data line is pulled up to the module supply, and 5 V on a C3 GPIO
  exceeds its 3.3 V input rating.
- Current: about 0.3 mA measuring, about 60 uA standby (Aosong-style table);
  up to 2.5 mA during conversion in other summaries. Use 2.5 mA for the
  power budget.
  Source: Aosong DHT11 datasheet summaries (disagreeing). Checked 2026-10-23.
- Wiring: a bare 4-pin DHT11 needs a pull-up resistor (typically 4.7 k to
  10 k) between DATA and VCC; 3-pin modules include the pull-up. This
  project uses 10 k, which is inside that range.
  Source: DHT11 module guides; Aosong datasheet. Checked 2026-10-23.
- DHT11 is not a precision instrument. Small disagreements with other
  thermometers are expected from its +/-2 C / +/-5% RH accuracy, not proof
  of a wiring fault.
- DHT22 as a drop-in: same wiring, same library, change `DHT11` to `DHT22`
  in the sketch - with three caveats the old docs omitted. Range -40 C to
  +80 C, accuracy +/-0.5 C, humidity 0-100% RH, +/-2% RH (some sources say
  +/-2-5%), resolution 0.1 C / 0.1% RH, supply 3.3-6 V, and sampling period
  at least 2 seconds (0.5 Hz max). The sketch's 2-second interval is
  exactly at that limit, so "drop-in" is true only if the interval is not
  shortened.
  Source: Aosong DHT22 datasheet summaries. Checked 2026-10-23.

## Rotary encoder module (KY-040 style)

- CLK = channel A, DT = channel B, SW = push button to GND (active LOW when
  pressed). The board carries 10 k pull-ups on CLK and DT, and on most
  boards on SW too, so signals read HIGH when open and LOW when closed.
  The sketch enables INPUT_PULLUP on all three pins, which also covers
  boards whose SW pull-up footprint is left blank.
  Source: KY-040 schematics and module guides. Checked 2026-10-23.
- The old wording "module's signals are open-collector style" is a
  simplification: they are mechanical switches to GND with pull-ups,
  functionally open-drain-like, not transistor open-collector outputs.
  The behaviour (HIGH open, LOW closed) is the same, so no wiring change.
- Detents per revolution (typically 20 on KY-040/EC11 modules) is not
  stated in this repo and was not needed for the sketch, which counts
  edges, not revolutions. Do not add a detent count without a source for
  the specific module in hand.

## HC-SR501 PIR (optional)

- Supply DC 4.5-20 V (5 V recommended). This project powers it from the
  SuperMini 5 V pin, which is inside that range. Output HIGH 3.3 V /
  LOW 0 V, so OUT is safe on a C3 GPIO.
  Source: HC-SR501 module manuals and datasheet-style listings.
  Checked 2026-10-23.
- Warm-up / initialisation about 30-60 seconds after power-on, during which
  triggers are spurious. Correction to an earlier audit note: the sketch
  does NOT blank the first 60 seconds — `lastMotion` starts at 0, so the
  display stays awake for the first 60 s after boot, then blanks if no
  motion is seen. Spurious warm-up triggers only keep it awake longer;
  they cannot blank it early.
  Source: HC-SR501 module manuals (one lists about 60 s). Checked 2026-10-23.
- Two jumpers/pots the old docs did not mention: H/L trigger-mode jumper
  (H = repeatable, L = non-repeatable; most listings default to
  repeatable) and delay and sensitivity potentiometers. Delay ranges
  differ by listing (commonly about 3 s to 5 min; one manual variant says
  5-18 s), so this repo does not pin a single delay range. Detection range
  is about 3-7 m with about a 110-120 degree cone, again listing-dependent.
  If the PIR holds the display awake, check the H/L jumper and the delay
  pot before suspecting the sketch.
  Source: HC-SR501 module manuals (ranges disagree by listing).
  Checked 2026-10-23.

## TTP223 touch module (optional, corrected)

- CORRECTION: the old wiring section said a TTP223 module "behaves like
  that button" (the encoder button between GPIO 10 and GND with
  INPUT_PULLUP, active LOW when pressed). That is wrong for a
  default-configuration TTP223, and there is no TTP223 code path in the
  sketch at all. Do not wire a TTP223 as a drop-in for the encoder button
  without one of the fixes below.
- Factory default (both jumpers unsoldered) is momentary active-HIGH:
  OUT HIGH on touch, LOW when released. The sketch's button logic expects
  LOW when pressed, so a default TTP223 will read exactly backwards.
  Fixes, pick one: solder jumper A for active-low output, or invert the
  logic for that input, or use a different input configuration. Do not do
  more than one (soldering A and inverting the logic cancels out).
  Source: Tontek TTP223 datasheet (TTP223_SPEC_V1.0, TTP223E-HA6);
  TTP223 module guides (default active-HIGH). Checked 2026-10-23.
- Operating voltage 2.0-5.5 V, CMOS output, output mode selectable
  active-high / active-low via AHLB, direct / toggle via TOG. Response
  max about 60 ms fast mode / about 220 ms low-power mode at 3 V.
  About 0.5 s stable time after power-on, during which the pad must not
  be touched. Sensitivity adjustable 0-50 pF.
  Source: Tontek TTP223 datasheet. Checked 2026-10-23.
- Power the module from 3V3, as the repo wires it. Its output is
  VCC-driven CMOS, so powering it at 5 V would drive OUT to about 4 V,
  above the C3's 3.3 V input comfort. At 3V3, OUT is 3.3 V logic and safe.
  Source: Tontek TTP223 datasheet; module guides. Checked 2026-10-23.

## Open-Meteo

- Endpoint `/v1/forecast`, no API key, no signup for non-commercial use.
  Free non-commercial allowance widely cited as about 10,000 requests/day;
  one comparison table also cites 5,000/hour and 600/minute sub-limits.
  This project makes 144/day (one fetch every 10 minutes: 24 x 6), far
  under all three figures. Commercial use requires a key and pricing.
  Source: Open-Meteo documentation (open-meteo.com/en/docs); free-tier
  comparison tables. Checked 2026-10-23. Whether Open-Meteo enforces
  attribution (CC-BY 4.0) for this use was not verified - check the
  current Open-Meteo terms before publishing a derivative that displays
  its data.
- `current` variables used: `temperature_2m` (default unit Celsius),
  `relative_humidity_2m` (%), `weather_code` (WMO code), `wind_speed_10m`
  (default unit km/h). The sketch sends no unit parameters, so the
  "km/h" on the display is correct only under those defaults. If a unit
  parameter is ever added, the display label must change with it.
  Source: Open-Meteo documentation (current variables, defaults).
  Checked 2026-10-23.
- `timezone` accepts any time-zone-database name; default is GMT, and
  `auto` resolves from coordinates. The sketch sends the IANA name
  unencoded (for example `America/Toronto`); the old how-it-works text
  showed a placeholder `IANA_TIMEZONE_URL_ENCODED` while the sketch
  comment said IANA names need no encoding. A slash is accepted
  unencoded in a query string by Open-Meteo in practice; the wording
  mismatch is a documentation nit, not a functional error.
  Source: Open-Meteo documentation. Checked 2026-10-23.
- WMO weather codes: the sketch's `codeText()` covers exactly the 29 codes
  Open-Meteo reports, and since 2026-10-23 each code has its own
  official label (the earlier grouped labels were simplifications).
  Codes not in the Open-Meteo list -
  including 98 (thunderstorm with dust/sandstorm in the full WMO 00-99
  set) - are not returned by Open-Meteo; the sketch's default `-`
  fallback covers any unexpected value.
  Source: Open-Meteo documentation, "WMO Weather interpretation codes (WW)".
  Checked 2026-10-23.
- Official Open-Meteo labels, for reference: 0 Clear sky, 1 Mainly clear,
  2 Partly cloudy, 3 Overcast, 45 Fog, 48 Depositing rime fog,
  51 Light drizzle, 53 Moderate drizzle, 55 Dense drizzle,
  56 Light freezing drizzle, 57 Dense freezing drizzle, 61 Slight rain,
  63 Moderate rain, 65 Heavy rain, 66 Light freezing rain,
  67 Heavy freezing rain, 71 Slight snowfall, 73 Moderate snowfall,
  75 Heavy snowfall, 77 Snow grains, 80 Slight rain showers,
  81 Moderate rain showers, 82 Violent rain showers,
  85 Slight snow showers, 86 Heavy snow showers, 95 Thunderstorm,
  96 Thunderstorm with slight hail, 97 Heavy thunderstorm,
  99 Thunderstorm with heavy hail.
  Footnote: codes 96 and 99 are only reported by models with an explicit
  hail forecast (for example DWD ICON, UKMO); all other models derive
  thunderstorms from instability parameters and report 95 and 97.
  Source: Open-Meteo documentation. Checked 2026-10-23.
- Label alignment, applied in `codeText()` on 2026-10-23: code 48 is
  "Depositing rime fog", not "Icy fog"; codes 85/86 are "Slight snow
  showers" / "Heavy snow showers", not a single "Snow showers";
  code 95 is plain "Thunderstorm" in Open-Meteo's table (no
  slight/moderate qualifier). Code 97 ("Heavy thunderstorm") is
  confirmed in the official table; the earlier audit note claiming
  it was invented was wrong.
- NTP: the sketch uses `pool.ntp.org` and `time.nist.gov` over UDP
  port 123 via `configTzTime()`. POSIX time-zone strings carry the
  standard/daylight offsets and DST switch dates (for example
  `EST5EDT,M3.2.0,M11.1.0` for Eastern Time). The POSIX format is standard;
  individual zone strings were not re-verified against a tz database in
  this audit - copy them from a current tz source, not from memory.
- Weather fetch is a blocking HTTP request (about 1-2 s in practice).
  Encoder turns during that window can be missed. This is an accepted
  implementation trade-off, documented in how-it-works, not a datasheet
  figure.

## What this audit could NOT verify

- The exact SuperMini regulator part number and its thermal / dropout
  behaviour at 500 mA; the 500 mA figure is a board-page claim.
- The exact SuperMini variant in any given builder's hand (standard vs
  Plus, blue LED vs WS2812, whether both share GPIO 8 on the Plus).
- Any specific OLED module's pull-up resistor values, regulator part
  (662K or other), or whether it is 3.3 V-only; and whether a specific
  module's VCC/GND pin order matches the repo diagram. Read the silkscreen.
- The sketch's compile status at audit time: `scripts/check.sh` then
  had no compile check, so "checks pass" did not mean "sketch
  compiles". Since then, `scripts/check.sh` gained a PlatformIO
  compile check (check 9). Post-fix compile, verified 2026-10-23
  (PlatformIO, board `esp32-c3-devkitm-1`): SUCCESS, RAM 12.4%
  (40,540 / 327,680 bytes), Flash 72.5% (950,656 / 1,310,720 bytes).
  Re-verify after any further sketch change; do not carry these
  figures forward unchanged.
- Open-Meteo's current free-tier enforcement (rate-limit headers) and
  its attribution requirement for displayed data.
- Individual POSIX time-zone strings against a current tz database.
- The ESP32-C3 ADC's per-chip calibration error; the 150 mV / 3100 mV
  figures above are the Arduino-ESP32 documented measurable range at
  11 dB attenuation, not a per-chip guarantee.
- DHT11 / DHT22 figures from any single "the" datasheet: Aosong-derived
  summaries disagree on humidity range (80% vs 90% vs 95%), current
  (0.3 mA vs 2.5 mA), and supply low end (3.3 V vs 3.5 V). The
  disagreements are recorded above rather than resolved.
- GitHub Actions pricing was re-checked 2026-10-23 against third-party
  summaries of GitHub's billing docs (not GitHub's own billing page
  directly): public repos free on standard runners; private repos get an
  included allowance only - 2,000 min/month on Free, 3,000 on Pro/Team,
  50,000 on Enterprise Cloud - then billed per minute. The repo's
  "local-first checks, hosted CI opt-in only" stance follows from that.
  Re-check GitHub's billing page before budgeting, because these numbers
  move.
