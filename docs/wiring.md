# Wiring — ESP32-C3 SuperMini

This build is for the **ESP32-C3 SuperMini**, not a classic ESP32
development board. Pin numbers from classic ESP32 guides (SDA 21 /
SCL 22, encoder 25 / 26 / 27, pot on GPIO 34) **do not exist on this
board** — do not use them. The SuperMini breaks out only 13 GPIOs:
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21.

Everything except the optional PIR runs at 3.3 V from the SuperMini's
3V3 pin — the HC-SR501's VCC goes to the 5V pin (its OUT pin is still
3.3 V logic, safe for GPIO 0). Wire the circuit unpowered,
double-check every connection against the table, then plug in USB-C.

| Module | Module pin | Connects to | Why / notes |
| ------ | ---------- | ----------- | ----------- |
| OLED (SSD1306) | VCC | SuperMini 3V3 | I2C bus. Only two signal wires for the whole display. |
| | GND | SuperMini GND | |
| | SDA | SuperMini GPIO 4 | See the I2C warning below — deliberately **not** GPIO 8. |
| | SCL | SuperMini GPIO 5 | Deliberately **not** GPIO 9. |
| DHT11 | VCC | SuperMini 3V3 | The module version includes its own pull-up resistor. |
| | GND | SuperMini GND | |
| | DATA (OUT) | SuperMini GPIO 3 | Digital input; GPIO 3 is also ADC1_CH3, but here it's used digitally. |
| Rotary encoder | + / VCC | SuperMini 3V3 | All three signal pins use INPUT_PULLUP in code. If your module has no "+" pin, it's a bare encoder: wire CLK/DT/SW the same and skip power. |
| | GND | SuperMini GND | |
| | CLK | SuperMini GPIO 6 | |
| | DT | SuperMini GPIO 7 | |
| | SW | SuperMini GPIO 10 | Safe, non-strapping GPIO. |
| Potentiometer (10K) | End 1 | SuperMini 3V3 | Must be an ADC1 pin: GPIO 1 is ADC1_CH1. Do **not** use GPIO 5 for the pot — GPIO 5 is ADC2, and ADC2 readings are unreliable while WiFi is on. |
| | Wiper (middle) | SuperMini GPIO 1 | |
| | End 2 | SuperMini GND | |
| PIR (optional) | VCC | SuperMini 5V | HC-SR501 requires 5 V input; its OUT pin is 3.3 V logic, safe for the SuperMini. Only add after the base build works. |
| | GND | SuperMini GND | |
| | OUT | SuperMini GPIO 0 | GPIO 0–5 are RTC GPIOs, so this pin can also wake the chip from deep sleep in a future variant. |

## ⚠ The C3 SuperMini I2C trap — read this before wiring the OLED

On the ESP32-C3, I2C is **not** fixed to specific pins at chip level —
it runs through the GPIO matrix, so the sketch must say which pins to
use, and it does: `Wire.begin(4, 5)`.

Do **not** use the pins many online guides call the "default" I2C
pins, GPIO 8 / GPIO 9:

- **GPIO 8** is a strapping pin, and on most SuperMini boards it also
  drives the onboard LED (WS2812 on some variants). Using it for SDA
  fights the LED and can disturb boot.
- **GPIO 9** is a strapping pin and the BOOT button: pulling it low at
  reset puts the chip in download mode instead of running your program.
  An I2C device pulling SCL low at the wrong moment can do exactly that.

The third strapping pin, **GPIO 2**, is likewise left unused in this
build. GPIO 20 / 21 (UART0 RX/TX) are also left free, so Serial debug
output stays available.

If your OLED stays black, check in this order: SDA/SCL are on GPIO 4/5
(not 8/9, not 21/22), the sketch's `Wire.begin(4, 5)` matches, the I2C
address is 0x3C (a few modules are 0x3D), and VCC is on 3V3, not 5V.
SuperMini board variants differ slightly (standard boards have a
simple blue LED on GPIO 8; "Plus" variants have a WS2812 RGB LED on
GPIO 8), and printed labels can vary by manufacturer — always go by
the GPIO number, and compare the board in hand with its printed labels
before wiring. Either way, GPIO 8 stays unused in this build.

![Wiring diagram from MakerGuides connecting an ESP32-Lite to an SSD1306 OLED](../assets/esp32-oled-wiring.png)

ESP32 → OLED wiring from MakerGuides. Four wires: GND, 3.3 V, SCL, SDA
— but note this diagram is for an ESP32-Lite (SDA 19 / SCL 23) and is
shown here only for the four-wire pattern. On the SuperMini, use
SDA GPIO 4 / SCL GPIO 5. Diagram: MakerGuides.

![Wiring diagram from LastMinuteEngineers connecting a rotary encoder module to an ESP32](../assets/encoder-wiring.png)

Rotary encoder → ESP32. The reference wiring from LastMinuteEngineers
uses different GPIOs than this guide; keep the pattern (CLK, DT, SW each
to a GPIO, module powered from the board) and use this guide's pins:
CLK 6, DT 7, SW 10. Diagram: LastMinuteEngineers.

![Rotary encoder module pinout: GND, +, SW, DT, CLK](https://lastminuteengineers.com/wp-content/uploads/arduino/rotary-encoder-module-pinout.png)

The encoder module's pins, labelled: GND, + (power), SW (push-button),
DT and CLK (the two quadrature signals). If your module's pin order
differs, go by the labels, not the positions. Diagram:
LastMinuteEngineers.

## Swapping the encoder for something else

A tactile button between GPIO 10 and GND (with INPUT_PULLUP) steps to
the next page per press. A TTP223 touch module wires VCC→3V3, GND→GND,
OUT→GPIO 10 and behaves like that button.

Note: the classic ESP32's bare capacitive-touch trick does **not**
work here — the ESP32-C3 has no capacitive touch peripheral, unlike
the classic ESP32. On this board, touch means the TTP223 module, not a
bare wire or foil pad.

---

[← Previous: Parts](parts.md) · [Contents](../README.md) · [Next: Libraries & setup →](libraries-and-setup.md)
