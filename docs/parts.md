# Parts

All parts are common hobbyist components, available from electronics
retailers and general marketplaces. No part is specific to a kit.

| Qty | Part | Notes |
| --- | ---- | ----- |
| 1 | ESP32-C3 SuperMini | Single-core RISC-V, 160 MHz, 4 MB flash, 400 KB SRAM, 2.4 GHz WiFi, USB-C, native USB. Only 13 GPIOs are broken out (0–10, 20, 21). |
| 1 | SSD1306 OLED, 0.96-inch, 128×64, I2C | 4-pin module (VCC, GND, SCL, SDA). Most modules include I2C pull-up resistors and run at 3.3 V. I2C address is usually 0x3C; some modules are 0x3D (see [wiring.md](wiring.md) — note the sketch hardcodes 0x3C and halts if not found, so a 0x3D module needs a code change, not just a rewire). A bare panel without a module board needs external pull-ups — prefer the module, and note the bare SSD1306 chip itself is NOT 5 V-tolerant (inputs max VDD + 0.3 V). Check the driver chip, not the size: many 1.3-inch panels sold as "SSD1306" are actually SH1106 (132×64 RAM, different mapping, needs its own driver — Adafruit_SSD1306 on SH1106 can show a 2-pixel shift or border garbage). Always read the module silkscreen before powering: some modules swap the VCC and GND pin order. |
| 1 | DHT11 temperature/humidity module | 3-pin module with an integrated pull-up resistor. Range 0–50 °C (±2 °C) and 20–80 % RH (±5 % RH, conservative — other datasheet summaries say 20–90 %); see the accuracy note in [how-it-works.md](how-it-works.md). A bare 4-pin DHT11 needs a 10K pull-up resistor between DATA and VCC. |
| 1 | Rotary encoder module (CLK / DT / SW) | Incremental encoder with a push button. A bare encoder (no module board) works the same way; omit the power wire. |
| 1 | Potentiometer, 10K, linear taper | A breadboard-mount trimmer pot fits this no-solder build directly. A standard panel pot's solder lugs do not fit breadboard holes cleanly — with a panel pot, use jumper wires from its lugs to the breadboard. Used only for brightness. |
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

## Optional parts

| Qty | Part | Notes |
| --- | ---- | ----- |
| 1 | HC-SR501 PIR motion sensor | Only for the wake/sleep extra. Skip it on the first build. Wired to GPIO 0, with VCC on the 5V pin (its OUT pin is 3.3 V logic). Check its H/L trigger-mode jumper (H = repeatable, L = non-repeatable; most default H) and its delay/sensitivity pots — delay ranges differ by listing (commonly ~3 s–5 min), and the total blank time is the module delay plus the sketch's 60 s. |
| 1 | TTP223 capacitive touch module | Alternative page control instead of the encoder's push button, or in place of a tactile button — with a correction: a default TTP223 (both jumpers unsoldered) is momentary active-HIGH (OUT HIGH on touch), which is exactly backwards for the sketch's active-LOW button logic, and there is no TTP223 code path in the sketch. Solder jumper A for active-low output, or invert the logic for that input — not both. Power it from 3V3 only: its output is VCC-driven, so 5 V power would drive OUT to ~4 V. Do NOT wire a TTP223 (or a button) on GPIO 10 at the same time as the encoder's SW pin — a button press would short TTP223 OUT to GND. The ESP32-C3 has no capacitive-touch peripheral, so a bare wire or foil pad cannot be used for touch on this board — the module is required. |
| 1 | Tactile push button | Alternative page control: one button between GPIO 10 and GND, using INPUT_PULLUP in code. A press jumps to Summary, and a second press returns to Clock — it does not step through pages. Do not wire it at the same time as the encoder's SW pin. |

## Parts not needed

- No separate power supply: USB-C from a computer or USB charger
  powers the whole build. The SuperMini's 3.3 V regulator supplies up
  to about 500 mA (a board-page figure; the exact regulator part was
  not verified, and variants may differ). Corrected power budget:
  the ESP32-C3 itself is the dominant load — about 23–28 mA
  modem-sleep, 84–87 mA RX, 335–350 mA TX peak (brief bursts) —
  plus OLED about 20 mA typical, DHT11 up to 2.5 mA during conversion,
  and under 1 mA each for the encoder, pot, and TTP223. Worst-case
  coincident peak is about 360–375 mA, under 500 mA with about
  125–140 mA margin; typical draw is far lower (tens of mA plus RX
  bursts). So "draws far less" is true typically, not at TX peak —
  and a weak 500 mA USB port or cable can still brown out during TX
  bursts even though the regulator rating is not exceeded on paper.
  Measure total current at the bench stage if the display flickers
  during weather fetches.
- No level shifters: every module in this build runs at 3.3 V logic,
  except the PIR's power input, which is 5 V in with a 3.3 V logic
  output.
- No resistors for the module versions of the OLED and DHT11: their
  pull-ups are on the module boards.

---

[← Previous: Start](../README.md) · [Next: Wiring →](wiring.md)
