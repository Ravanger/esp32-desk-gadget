# Parts

All parts are common hobbyist components. Check whether the header
pins on the SuperMini and the modules are already soldered; unsoldered
headers need soldering before they fit a breadboard.

| Qty | Part | Notes |
| --- | ---- | ----- |
| 1 | ESP32-C3 SuperMini | ESP32-C3 (single-core RISC-V, 160 MHz) with 4 MB in-package flash, 400 KB SRAM, 2.4 GHz WiFi, USB-C, native USB. Only 13 GPIOs are broken out (0–10, 20, 21). |
| 1 | SSD1306 OLED, 0.96-inch, 128×64, I2C | 4-pin module; pin order varies (the pictured module is GND, VCC, SCL, SDA) — read the silkscreen. Most modules include I2C pull-up resistors and run at 3.3 V. I2C address is usually 0x3C; some modules are 0x3D (see [wiring.md](wiring.md) — note the sketch hardcodes 0x3C and halts if not found, so a 0x3D module needs a code change, not just a rewire). A bare panel without a module board needs external pull-ups — prefer the module, and note the bare SSD1306 chip itself is NOT 5 V-tolerant (inputs max VDD + 0.3 V). Check the driver chip, not the size: many 1.3-inch panels sold as "SSD1306" are actually SH1106 (132×64 RAM, different mapping, needs its own driver — Adafruit_SSD1306 on SH1106 can show a 2-pixel shift or border garbage). |
| 1 | DHT11 temperature/humidity module | 3-pin module with an integrated pull-up resistor. Supply 3–5.5 V; 0–50 °C (±2 °C) and 20–90 % RH (±5 % RH), 1 Hz maximum sampling; see the accuracy note in [how-it-works.md](how-it-works.md). A bare 4-pin DHT11 needs a 4.7 kΩ pull-up resistor between DATA and VCC (the datasheet recommends 5 kΩ; 10 kΩ works on short wires), plus an optional 100 nF capacitor between VCC and GND. |
| 1 | Rotary encoder module (CLK / DT / SW) | Incremental encoder with a push button. A bare encoder (no module board) also works: C (common) to GND, A to GPIO 6, B to GPIO 7, switch terminals to GPIO 10 and GND, no power; see [wiring.md](wiring.md). |
| 1 | Potentiometer, 10K, linear taper | A breadboard-mount trimmer pot fits directly. A standard panel pot's solder lugs do not fit breadboard holes cleanly — with a panel pot, use jumper wires from its lugs to the breadboard. Used only for brightness. |
| 1 | Breadboard, half-size or larger | |
| ~20 | Jumper wires (male-to-male) | |
| 1 | USB-C data cable | Must carry data, not charge-only, or uploads and Serial Monitor will not work. |

![ESP32 board photo from MakerGuides](https://www.makerguides.com/wp-content/uploads/2023/10/Lolin32_lite.jpg)

An ESP32 board. Photo: MakerGuides. The board in this project is the
smaller ESP32-C3 SuperMini, not the board pictured; the photo is shown
for the general form factor only.

![Breadboard photo from MakerGuides](https://www.makerguides.com/wp-content/uploads/2019/05/Half_breadboard56a.png)

A half-size breadboard. Photo: MakerGuides.

![Jumper wire set photo from MakerGuides](https://www.makerguides.com/wp-content/uploads/2023/09/dupon_wire_set.png)

Male-to-male jumper wires. Photo: MakerGuides.

![0.96-inch SSD1306 OLED module photo from MakerGuides](../assets/oled-display.jpg)

A 0.96-inch SSD1306 OLED module. Photo: MakerGuides.

## Optional parts

| Qty | Part | Notes |
| --- | ---- | ----- |
| 1 | HC-SR501 PIR motion sensor | Only for the wake/sleep extra. Skip it on the first build. Wired to GPIO 0, with VCC on the 5V pin (its OUT pin is 3.3 V logic). Check its H/L trigger-mode jumper (H = repeatable, L = non-repeatable; most default H) and its delay/sensitivity pots — the delay pot spans roughly 5–300 s, the module needs about a minute to warm up after power-up, and the display blanks 60 s after the PIR's output drops (see [how-it-works.md](how-it-works.md#optional-pir-sleep)). |
| 1 | TTP223 capacitive touch module | Alternative page control instead of the encoder's push button, or in place of a tactile button. A default TTP223 (both jumpers unsoldered) is momentary active-HIGH (OUT HIGH on touch), which is exactly backwards for the sketch's active-LOW button logic, and there is no TTP223 code path in the sketch. Solder jumper A for active-low output, or invert the logic for that input — not both. Power it from 3V3 only: its output is VCC-driven, so 5 V power would drive OUT to ~4 V. Do NOT wire a TTP223 (or a button) on GPIO 10 at the same time as the encoder's SW pin — a button press would short TTP223 OUT to GND. The ESP32-C3 has no capacitive-touch peripheral, so a bare wire or foil pad cannot be used for touch on this board — the module is required. |
| 1 | Tactile push button | Alternative page control: one button between GPIO 10 and GND, using INPUT_PULLUP in code. A press jumps to Summary, and a second press returns to Clock — it does not step through pages. Do not wire it at the same time as the encoder's SW pin. |

## Parts not needed

- No separate power supply: USB-C from a computer or USB charger
  powers the whole build. The 3.3 V regulator rating varies by board
  clone: one retailer tutorial states 500 mA (an ME6211-type part),
  while a reader on another board review reports 250 mA parts; these
  are community and board-page figures, not Espressif's. The ESP32-C3
  draws a brief TX peak of 335 mA (802.11b, 21 dBm; datasheet v2.4
  Table 5-7) and 84–87 mA in receive, with the OLED about 20 mA and
  the other parts well under 3 mA each. If the display flickers or
  WiFi drops during weather fetches, set `WIFI_LOW_TX_POWER` to 1 in
  the sketch, add a 10–100 µF capacitor across 5V and GND, and use a
  short, good-quality USB cable.
- No level shifters: every module in this build runs at 3.3 V logic,
  except the PIR's power input, which is 5 V in with a 3.3 V logic
  output.
- No resistors for the module versions of the OLED and DHT11: their
  pull-ups are on the module boards.

---

[← Previous: Start](../README.md) · [Contents](../README.md) · [Next: Wiring →](wiring.md)
