# Parts

All parts are common hobbyist components, available from electronics
retailers and general marketplaces. No part is specific to a kit.

| Qty | Part | Notes |
| --- | ---- | ----- |
| 1 | ESP32-C3 SuperMini | Single-core RISC-V, 160 MHz, 4 MB flash, 400 KB SRAM, 2.4 GHz WiFi, USB-C, native USB. Only 13 GPIOs are broken out (0–10, 20, 21). |
| 1 | SSD1306 OLED, 0.96-inch, 128×64, I2C | 4-pin module (VCC, GND, SCL, SDA). Most modules include I2C pull-up resistors and run at 3.3 V. I2C address is usually 0x3C; some modules are 0x3D (see [wiring.md](wiring.md)). A bare panel without a module board needs external pull-ups — prefer the module. |
| 1 | DHT11 temperature/humidity module | 3-pin module with an integrated pull-up resistor. Range 0–50 °C (±2 °C) and 20–80 % RH (±5 % RH); see the accuracy note in [how-it-works.md](how-it-works.md). A bare 4-pin DHT11 needs a 10K pull-up resistor between DATA and VCC. |
| 1 | Rotary encoder module (CLK / DT / SW) | Incremental encoder with a push button. A bare encoder (no module board) works the same way; omit the power wire. |
| 1 | Potentiometer, 10K, linear taper | Any 10K linear pot. Used only for brightness. |
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
| 1 | HC-SR501 PIR motion sensor | Only for the wake/sleep extra. Skip it on the first build. Wired to GPIO 0, with VCC on the 5V pin (its OUT pin is 3.3 V logic). |
| 1 | TTP223 capacitive touch module | Alternative page control instead of the encoder's push button, or in place of a tactile button. The ESP32-C3 has no capacitive-touch peripheral, so a bare wire or foil pad cannot be used for touch on this board — the module is required. |
| 1 | Tactile push button | Alternative page control: one button between GPIO 10 and GND, using INPUT_PULLUP in code. |

## Parts not needed

- No separate power supply: USB-C from a computer or USB charger
  powers the whole build. The SuperMini's 3.3 V regulator supplies up
  to about 500 mA; this build draws far less (OLED ~20 mA, DHT11
  ~0.3 mA measuring, encoder negligible).
- No level shifters: every module in this build runs at 3.3 V logic,
  except the PIR's power input, which is 5 V in with a 3.3 V logic
  output.
- No resistors for the module versions of the OLED and DHT11: their
  pull-ups are on the module boards.
