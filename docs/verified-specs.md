# Verified specifications

Every number below was checked against official documents where noted
(chip figures against the ESP32-C3 datasheet v2.4 and Espressif
documentation); board-level figures come from board pages and community
reports and are marked as such. Where sources disagree, the disagreement is
recorded instead of picking one silently. URLs are listed in
[sources.md](sources.md). If a fact changes, update its source and check date
here too.

## ESP32-C3 chip

- Single-core 32-bit RISC-V, up to 160 MHz, 400 KB SRAM, 384 KB ROM, 22 GPIOs
  at chip level, Wi-Fi 802.11 b/g/n 2.4 GHz only, Bluetooth LE 5.0.
  No 5 GHz radio, no classic Bluetooth, no DAC, no native capacitive-touch
  peripheral (unlike the classic ESP32, which has touch pads).
  Source: ESP32-C3 datasheet v2.4; Espressif ESP-IDF GPIO/ADC documentation.
  Checked 2026-10-24.
- Two 12-bit SAR ADCs. ADC1 = 5 channels, GPIO 0-4. ADC2 = 1 channel, GPIO 5.
  Source: Espressif ESP-IDF ADC documentation for ESP32-C3. Checked 2026-10-24.
- ADC2 must not be used for the pot. ESP-IDF states: "ADC2 oneshot mode is
  no longer supported, due to hardware limitations. The results are not
  stable." Digital use of GPIO 5 (for example as I2C SCL) is unaffected; only
  analog use is affected.
  Source: ESP-IDF ADC oneshot documentation, ESP32-C3. Checked 2026-10-24.
- ADC range: 12-bit, 0-4095. With 11 dB attenuation (the Arduino default
  for `analogRead()`), the effective range is 0-2500 mV (datasheet Table 5-6:
  ATTEN0 0-750 mV, ATTEN1 0-1050 mV, ATTEN2 0-1300 mV, ATTEN3 0-2500 mV).
  Anything above about 2.5 V reads as full scale. The sketch uses
  `analogReadMilliVolts()`, clamps to 0-2500 mV and maps that to contrast
  8-255, so on a pot across 3V3 the top ~24% of travel is full brightness.
  That is expected. The datasheet specifies ADC DNL/INL with an external
  100 nF capacitor on the input (section 5.5, Table 5-5); a 100 nF capacitor
  from the wiper to GND is optional here.
  Source: ESP32-C3 datasheet v2.4, Tables 5-5 and 5-6; Arduino-ESP32 ADC
  documentation. Checked 2026-10-24.
- Wi-Fi current (chip datasheet, 3.3 V, 25 C, 100% duty cycle, Table 5-7):
  TX peak 335 mA (802.11b, 21 dBm), 285 mA (802.11g, 54 Mbps), 276-278 mA
  (802.11n); RX 84-87 mA. Module datasheets (for example ESP32-C3-MINI-1)
  quote a slightly higher TX peak, 350 mA; use 335-350 mA as the TX peak
  range.
  Source: ESP32-C3 datasheet v2.4, section 5.6.1, Table 5-7; ESP32-C3-MINI-1
  datasheet. Checked 2026-10-24.
- Absolute limits: power pins max 3.6 V (Table 5-1); input high level max
  VDD + 0.3 V; internal pull-up about 45 kOhm (Table 5-4). Never connect 5 V
  to a 3V3 pin or a GPIO.
  Source: ESP32-C3 datasheet v2.4. Checked 2026-10-24.
- I2C on the C3 runs through the GPIO matrix: there are no fixed I2C pins at
  chip level, and peripheral signals can be routed to any GPIO. The sketch
  must call `Wire.begin(OLED_SDA, OLED_SCL)` explicitly, where those
  defines are 4 and 5.
  Source: Espressif ESP-IDF GPIO documentation. Checked 2026-10-23.
- Strapping pins are GPIO 2, 8, 9. Datasheet Table 3-3: SPI boot needs
  GPIO 9 = 1 (GPIO 8 any); download boot needs GPIO 8 = 1 and GPIO 9 = 0.
  GPIO 2 does not select the mode; the datasheet recommends pulling it up
  because of glitches. The repo rule "never use GPIO 2, 8, or 9" is
  therefore safe, and is stricter than necessary for GPIO 2 alone.
  Source: ESP32-C3 datasheet v2.4, Table 3-3. Checked 2026-10-24.
- GPIO 0 and 1 are XTAL_32K_P / XTAL_32K_N (also ADC1_CH0 / CH1). They are
  free for general use when no 32 kHz crystal is fitted, as on the SuperMini.
  Source: ESP32-C3 datasheet v2.4. Checked 2026-10-24.
- GPIO 4-7 labelled "strapping" on some board tables are a different thing:
  on internal-flash variants they are JTAG / Quad-SPI flash pins
  (GPIO 4 = MTMS/FSPIHD, GPIO 5 = MTDI/FSPIWP, GPIO 6 = MTCK/FSPICLK,
  GPIO 7 = MTDO/FSPID). Do not conflate those labels with Espressif
  strapping pins. GPIO 4, 5, 6, 7 are used by this project and are fine.
  Source: Espressif ESP-IDF GPIO documentation; ESPboards SuperMini pinout.
  Checked 2026-10-23.
- The C3 has an RTC block, but the SuperMini has no battery-backed RTC
  (no coin cell). Time is lost on power loss and re-fetched by NTP.
  Source: board-level observation; Espressif chip documentation describes
  the RTC block, not a battery. Checked 2026-10-23.

## ESP32-C3 SuperMini board

- Breaks out 13 GPIOs: 0-10, 20, 21. GPIO 20/21 (UART0 pins) are left
  free; `Serial` runs over native USB. The chip is an ESP32-C3 with 4 MB
  in-package flash; the specific variant is not claimed (the datasheet v2.4
  marks ESP32-C3FN4 as end-of-life).
  Source: ESPboards ESP32-C3 Super Mini pinout; Mischianti SuperMini pinout;
  datasheet v2.4. Checked 2026-10-24.
- Native USB-C, no USB-serial chip. For `Serial` over USB, use board
  "ESP32C3 Dev Module" with Tools > USB CDC On Boot > Enabled (default
  Disabled; the verified path), or "Nologo ESP32C3 Super Mini" (arduino-esp32
  3.x; USB CDC On Boot is enabled by default in `boards.txt`; the sketch
  compiles on core 3.3.12, see below). PlatformIO board `esp32-c3-devkitm-1`
  with `-DARDUINO_USB_CDC_ON_BOOT=1 -DARDUINO_USB_MODE=1`.
  Source: arduino-esp32 `boards.txt`. Checked 2026-10-24.
- 3.3 V regulator rating varies by clone. Random Nerd Tutorials quotes
  500 mA (an ME6211-type part); a reader report on the SIGMDEL page mentions
  250 mA parts. These are community / board-page figures, not Espressif
  figures. The 5V pin is wired to USB VBUS directly (SIGMDEL); the Wi-Fi
  antenna is reported as a weak point and some boards fail to join Wi-Fi
  until TX power is lowered (HomeSpan issue 780, Electromaker; community
  reports).
  Source: Random Nerd Tutorials; SIGMDEL; HomeSpan #780; Electromaker.
  Checked 2026-10-24.
- Onboard LED variant trap: standard boards have a simple blue LED on
  GPIO 8; "Plus" variants have a WS2812 on GPIO 8. Some Plus documentation
  describes both a blue LED and a WS2812 sharing GPIO 8. Either way, GPIO 8
  is not a free GPIO in this project, and the exact variant in hand must be
  identified from the board, not assumed.
  Source: ESPboards Super Mini pinout; Mischianti SuperMini Plus page.
  Checked 2026-10-24. Variant in hand: unverified.
- One board-page line (Mischianti) says "USB-serial via CH340". That is
  wrong for the SuperMini, which has native USB and no CH340. Do not cite
  that page for USB.
  Checked 2026-10-23.

## Power budget

- ESP32-C3: ~20-28 mA modem-sleep/CPU running, ~84-87 mA RX, 335-350 mA
  TX peak (brief bursts; 100% duty-cycle figure, not a continuous draw).
- OLED module: about 20 mA typical (module-dependent, varies with pixels
  lit). This is an approximate module figure, not a single SSD1306
  datasheet value.
- DHT11: 0.5 mA typical / 2.5 mA maximum measuring, 100 uA standby
  (Aosong datasheet). Use 2.5 mA for the budget.
- PIR (if fitted): quiescent under 50 uA (HC-SR501 datasheet).
- Encoder, pot, TTP223: negligible (under 1 mA each in practice).
- Worst-case peak if every peak coincided: about 335-350 + 20 + 2.5 + 0.1
  = about 360-375 mA. Against a 500 mA regulator that leaves about
  125-140 mA; against a 250 mA part it does not fit. A 500 mA USB 2.0 port
  limit is close to the same peak, so a weak USB port or cable can brown out
  during TX bursts. If the display flickers or WiFi drops: set
  `WIFI_LOW_TX_POWER` to 1, add 10-100 uF across 5V/GND, use a short good
  cable, and measure total current at the bench stage.
  Sources: ESP32-C3 datasheet v2.4 Table 5-7; Aosong DHT11 datasheet;
  HC-SR501 datasheet; board pages. Checked 2026-10-24.

## SSD1306 OLED (0.96-inch, 128x64, I2C)

- 128x64 pixels, 256-step contrast control, I2C interface. Bare-chip supply:
  VDD 1.65-3.3 V, VBAT 3.3-4.2 V for the charge pump, VCC 7-15 V for panel
  driving. The bare chip is NOT 5 V-tolerant (inputs max VDD + 0.3 V).
  Source: Solomon Systech SSD1306 datasheet Rev 1.5. Checked 2026-10-23.
- I2C slave addresses from SA0: 7-bit 0x3C (0111100) and 0x3D (0111101).
  Most 4-pin modules default to 0x3C. If the I2C scanner finds nothing,
  try 0x3D before assuming a dead panel.
  Source: Solomon Systech SSD1306 datasheet. Checked 2026-10-23.
- Most 4-pin modules include an onboard regulator and pull-up resistors, and
  accept 3.3-5 V. The regulator part marking was not verified. This project wires VCC to 3V3,
  which is safe for both regulated modules and 3.3 V-only modules. Do not
  generalise to "all OLED modules are 5 V-safe": a 3.3 V-only module powered
  from 5 V can be damaged, and pin order varies between modules (the pictured
  module is GND, VCC, SCL, SDA) - always read the module silkscreen before
  powering it. Module pull-ups go to VCC, so keep VCC on 3V3.
  Source: SSD1306 datasheet (chip limits) plus module guides. Checked
  2026-10-23. Pull-up resistor values (4.7 k vs 10 k) vary by module and
  were not verified for any specific module.
- Contrast is set with command SSD1306_SETCONTRAST plus a value 0-255;
  display on/off with SSD1306_DISPLAYON / SSD1306_DISPLAYOFF. The sketch's
  dimming (contrast value from the pot) is the datasheet's brightness
  control, not a backlight (there is no backlight on an OLED).
  Source: SSD1306 datasheet; Adafruit SSD1306 command set. Checked 2026-10-23.
- SH1106 trap: SH1106 has a 132x64
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

- Aosong datasheet (translated copy): supply 3-5.5 V; humidity 20-90 % RH
  +/-5 % RH; temperature 0-50 C +/-2 C; resolution 1 C / 1 % RH; sampling
  period 1 s; wait 1 s after power-up. Third-party summaries disagree on
  humidity range (80 %, 90 %, 95 %), current and supply minimum (3.3 V vs
  3.5 V); the datasheet figures are used here.
  Source: Aosong DHT11 datasheet. Checked 2026-10-24.
- Sampling: the datasheet allows 1 Hz, but the Adafruit DHT library caches
  reads for 2000 ms (MIN_INTERVAL), so the sketch reads every 2.5 s. Do not
  shorten the interval.
  Source: Aosong DHT11 datasheet; DHT sensor library 1.4.7. Checked 2026-10-24.
- Powered from 3V3 (inside 3-5.5 V). Do NOT move the pull-up to 5 V: the
  data line is pulled up to the supply, and 5 V on a C3 GPIO exceeds its
  3.3 V input rating.
- Current: 0.5 mA typical / 2.5 mA maximum measuring, 100 uA standby. Use
  2.5 mA for the power budget.
  Source: Aosong DHT11 datasheet. Checked 2026-10-24.
- Wiring: a bare 4-pin DHT11 needs a pull-up resistor between DATA and VCC:
  the datasheet recommends 5 kOhm for cables under 20 m. This project uses
  4.7 kOhm; 10 kOhm works on short wires. An optional 100 nF capacitor
  between VDD and GND is suggested. 3-pin modules include the pull-up, and
  their pin order differs between makers - read the silkscreen; reversed
  power can destroy the sensor.
  Source: Aosong DHT11 datasheet. Checked 2026-10-24.
- DHT11 is not a precision instrument. Small disagreements with other
  thermometers are expected from its +/-2 C / +/-5% RH accuracy, not proof
  of a wiring fault.
- DHT22 as a drop-in: same wiring, same library, change `DHT11` to `DHT22`
  in the sketch. Range -40 C to +80 C, accuracy +/-0.5 C, humidity 0-100% RH,
  +/-2% RH (some sources say +/-2-5%), resolution 0.1 C / 0.1% RH, supply
  3.3-6 V, sampling period at least 2 seconds. The sketch's 2.5 s interval
  satisfies that.
  Source: Aosong DHT22 datasheet summaries (unverified: no primary datasheet
  URL has been confirmed). Checked 2026-10-23.

## Rotary encoder module (KY-040 style, optional)

- CLK = channel A, DT = channel B, SW = push button to GND (active LOW when
  pressed). The module has pull-ups on CLK and DT that go to its `+` pin, so
  `+` must be wired to 3V3. The SW pull-up and resistor values are
  unverified. The sketch enables INPUT_PULLUP on all three pins.
  The signals are mechanical switches to GND with pull-ups: HIGH open, LOW
  closed.
  Source: Wokwi KY-040 part documentation (secondary). Checked 2026-10-24.
- Pulses per detent varies by encoder and is unverified; the sketch counts
  one CLK falling edge per step with a 3 ms bounce guard. A bare encoder
  (no module) has terminals A, B and a common C: C to GND, A to CLK,
  B to DT, no power.

## HC-SR501 PIR (optional)

- Supply 5-20 V (the feature list says 4.5-20 V); this project powers it from
  the SuperMini 5 V pin. Output HIGH 3.3 V / LOW 0 V, so OUT is safe on a
  C3 GPIO. Quiescent current under 50 uA.
  Source: HC-SR501 datasheet (reseller copy). Checked 2026-10-24.
- Warm-up about 1 minute after power-on, during which triggers are
  spurious. Spurious triggers only keep the display awake longer; they
  cannot blank it early.
  Source: HC-SR501 datasheet. Checked 2026-10-24.
- Delay potentiometer 5-300 s; block time 2.5 s; H/L trigger-mode jumper
  with default H (repeatable). The sketch blanks the panel 60 s after the PIR's output drops (see
  [how-it-works.md](how-it-works.md#optional-pir-sleep)). If the
  PIR holds the display awake, check the H/L jumper and the delay pot before
  suspecting the sketch. Detection range and cone angle vary by listing and
  are not pinned. RF-induced false triggers were not verified.
  Source: HC-SR501 datasheet. Checked 2026-10-24.

## TTP223 touch module (optional)

- A default-configuration TTP223 does not behave like the navigation button
  (between GPIO 10 and GND with INPUT_PULLUP, active LOW when pressed), and
  there is no TTP223 code path in the sketch. Do not wire a TTP223 as a
  drop-in for the navigation button without one of the fixes below.
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
  Free tier limits per the Open-Meteo terms: under 10,000 calls/day,
  5,000/hour, 600/minute. This project makes 144/day when every fetch
  succeeds (one every 10 minutes), far under all three. Commercial use
  requires a paid plan. Data is licensed CC-BY 4.0.
  Source: https://open-meteo.com/en/terms. Checked 2026-10-24.
- `current` variables used: `temperature_2m` (default unit Celsius),
  `relative_humidity_2m` (%), `weather_code` (WMO code), `wind_speed_10m`
  (default unit km/h). The sketch sends no unit parameters, so the
  "km/h" on the display is correct only under those defaults. If a unit
  parameter is ever added, the display label must change with it.
  Source: Open-Meteo documentation (current variables, defaults).
  Checked 2026-10-24.
- `timezone` accepts any time-zone-database name; default is GMT, and
  `auto` resolves from coordinates. The sketch sends the IANA name
  unencoded (for example `America/Toronto`); a slash is accepted unencoded
  in a query string. This setting only affects server-side time formatting;
  the sketch clock uses `TIMEZONE_POSIX`.
  Source: Open-Meteo documentation. Checked 2026-10-23.
- WMO weather codes: the sketch's `codeText()` covers exactly the 29 codes
  Open-Meteo reports, each with its own label (96 and 99 use shorter
  labels than Open-Meteo's combined "Thunderstorm with slight and heavy hail";
  long labels wrap onto a second line on the Outdoor page, and the Summary
  page shows outdoor temperature and humidity only). Codes not in the Open-Meteo list -
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
- Labels follow Open-Meteo's table: code 48 is "Depositing rime fog", codes
  85/86 are "Slight snow showers" / "Heavy snow showers", code 95 is plain
  "Thunderstorm", and code 97 ("Heavy thunderstorm") is in the official
  table.
- NTP: the sketch uses `pool.ntp.org` and `time.nist.gov` over UDP
  port 123 via `configTzTime()`; SNTP re-syncs periodically. POSIX time-zone
  strings carry the standard/daylight offsets and DST switch dates (for
  example `EST5EDT,M3.2.0,M11.1.0` for Eastern Time). The sign is inverted
  relative to UTC offsets: UTC+9 is `JST-9`. Individual zone strings were
  not re-verified here; copy them from a current tz source such as
  https://github.com/nayarsystems/posix_tz_db/blob/master/zones.csv
  (checked 2026-10-24: loads).
- Weather fetch is a blocking HTTPS request with 4 s connect, 4 s TLS
  handshake (`client.setHandshakeTimeout(4)`, seconds; the core default is
  120 s) and 4 s read timeouts (HTTPClient default is 5 s). A failing fetch
  typically blocks the loop for a few seconds, at worst about 12 s plus DNS
  lookup time; encoder input during a fetch is missed. The first fetch
  happens as soon as WiFi is connected, then every 10 minutes after success
  and every 60 s after a failure. Clock validity is a non-blocking `time()`
  check against `MIN_VALID_EPOCH` (no `getLocalTime()`).
  Source: arduino-esp32 2.0.17 `WiFiClientSecure.cpp` and 3.3.12
  `NetworkClientSecure.cpp` (handshake timeout); `esp32-hal-time.c`;
  HTTPClient. Checked 2026-10-24.
- TLS: the sketch uses `WiFiClientSecure` with `setInsecure()`. Traffic is
  encrypted, but the server certificate is NOT verified. Optional hardening:
  the core's built-in CA bundle (3.x `useBuiltinCACertBundle`), which per the
  core's own example CI needs the Huge APP partition; not used here.
- Adafruit_SSD1306 `begin()` does not probe I2C (it fails only on
  allocation), so the sketch probes address 0x3C first and repeats
  "OLED not found at 0x3C - check wiring/address" every 2 s on Serial. The
  sketch calls `display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true, false)` so the
  library does not re-init Wire away from GPIO 4/5.
  Source: Adafruit_SSD1306 source. Checked 2026-10-24.

## Tested toolchain

Compile-verified on PlatformIO, platform espressif32 (arduino-esp32 2.0.17),
board `esp32-c3-devkitm-1`, with ArduinoJson 7.4.3, Adafruit SSD1306 2.5.17,
Adafruit GFX 1.13.0, DHT sensor library 1.4.7 (+ Adafruit Unified Sensor).
Result, 2026-10-24: SUCCESS with no sketch warnings under `-Wall` (PlatformIO platform
espressif32 6.9.0 = arduino-esp32 2.0.17, board `esp32-c3-devkitm-1`, the
pinned library versions above): RAM 12.4% (40,508 / 327,680 bytes), Flash
about 938 KB (71.6% of 1,310,720 bytes; the exact figure varies by a few
hundred bytes with library resolution). scripts/check.py compiles two
configurations: the default, and every option define (`USE_PIR`,
`USE_ENCODER`, `WIFI_LOW_TX_POWER`) set to 1; both compile.
Latest stable arduino-esp32 as checked 2026-10-24: 3.3.12 (released
2026-09-18). Core 3.x result, 2026-10-24: SUCCESS for both configurations
with no sketch warnings under `-Wall` (pioarduino platform 55.03.312-1 =
arduino-esp32 3.3.12, PlatformIO Core 6.2.0, board `esp32-c3-devkitm-1`
with the same CDC flags, same library versions): default RAM 12.0%
(39,376 bytes), Flash 91.0% (1,193,313 of 1,310,720 bytes); all options
Flash 91.1% (1,193,927 bytes). Core 3.x builds are about 250 KB larger, so
little room is left in the default app partition, so 2.0.17 stays the
recommended core. Single-machine result: run by hand once, not yet
reproduced elsewhere; scripts/check.py compiles core 2.0.17 only.
Platform line used: `platform = https://github.com/pioarduino/platform-espressif32/releases/download/55.03.312-1/platform-espressif32.zip`.

## What this audit could NOT verify

- The exact SuperMini regulator part number, rating and thermal / dropout
  behaviour; ratings differ between clones (see above).
- The exact SuperMini variant in any given builder's hand (standard vs
  Plus, blue LED vs WS2812, whether both share GPIO 8 on the Plus).
- Any specific OLED module's pull-up resistor values, regulator part, or
  whether it is 3.3 V-only; and whether a specific module's VCC/GND pin
  order matches the repo diagram. Read the silkscreen.
- Any behaviour on real hardware: the project has not been bench-tested,
  on either core.
- KY-040 pulses per detent and pull-up resistor values.
- PIR false triggers from RF interference.
- Open-Meteo's free-tier enforcement (rate-limit headers) and how its
  CC-BY 4.0 attribution applies to a displayed value.
- Individual POSIX time-zone strings against a current tz database.
- The ESP32-C3 ADC's per-chip calibration error; 0-2500 mV is the
  documented effective range at 11 dB attenuation, not a per-chip guarantee.
- DHT22 figures against the primary Aosong datasheet (no verified URL).

---

[← Previous: Sources & credits](sources.md) · [Contents](../README.md) · [Next: ESPHome →](esphome.md)
