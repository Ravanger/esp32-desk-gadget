# Wiring

Everything except the optional PIR runs at 3.3 V from the ESP32's 3V3
pin — the HC-SR501's VCC goes to 5V/VIN (its OUT pin is still 3.3 V
logic, safe for GPIO 13). Wire it unpowered, double-check against the
table, then plug in USB.

| Module | Module pin | Connects to | Why / notes |
| ------ | ---------- | ----------- | ----------- |
| OLED (SSD1306) | VCC | ESP32 3V3 | I2C bus. Only two signal wires for the whole display. |
| | GND | ESP32 GND | |
| | SDA | ESP32 GPIO 21 | |
| | SCL | ESP32 GPIO 22 | |
| DHT11 | VCC | ESP32 3V3 | The module version includes its own pull-up resistor. |
| | GND | ESP32 GND | |
| | DATA (OUT) | ESP32 GPIO 4 | |
| Rotary encoder | + / VCC | ESP32 3V3 | All three signal pins use INPUT_PULLUP in code. If your module has no "+" pin, it's a bare encoder: wire CLK/DT/SW the same and skip power. |
| | GND | ESP32 GND | |
| | CLK | ESP32 GPIO 25 | |
| | DT | ESP32 GPIO 26 | |
| | SW | ESP32 GPIO 27 | |
| Potentiometer (10K) | End 1 | ESP32 3V3 | GPIO 34 is input-only and ADC1 — perfect for a pot, and ADC1 keeps working while WiFi is on (ADC2 doesn't). |
| | Wiper (middle) | ESP32 GPIO 34 | |
| | End 2 | ESP32 GND | |
| PIR (optional) | VCC | ESP32 5V / VIN | HC-SR501 wants 5 V in; its OUT pin is 3.3 V logic, safe for the ESP32. Only add after the base build works. |
| | GND | ESP32 GND | |
| | OUT | ESP32 GPIO 13 | |

## ⚠ Check your board's I2C pins before you wire the OLED

On most ESP32 dev boards the default I2C pins are SDA = GPIO 21,
SCL = GPIO 22, and that's what the table above and the code use. But
it's a board default, not a law: the MakerGuides weather station used an
ESP32-Lite whose defaults are SDA 19 / SCL 23 — look at their wiring
photo below and you'll see exactly those labels. If your OLED stays
black, this mismatch (or SDA/SCL simply swapped) is the first suspect.

Not sure what your board uses? Run this sketch and the Serial Monitor
will tell you:

```cpp
void setup() { Serial.begin(115200); }
void loop() {
  Serial.printf("SDA = GPIO %d  SCL = GPIO %d\n", SDA, SCL);
  delay(2000);
}
```

![Wiring diagram from MakerGuides connecting an ESP32-Lite to an SSD1306 OLED](../assets/esp32-oled-wiring.png)

ESP32 → OLED wiring. Four wires: GND, 3.3 V, SCL, SDA. Note the
SDA 19 / SCL 23 labels on this particular board — yours is most likely
21 / 22; wire to your board's pins. Diagram: MakerGuides.

![Wiring diagram from LastMinuteEngineers connecting a rotary encoder module to an ESP32](../assets/encoder-wiring.png)

Rotary encoder → ESP32. The reference wiring from LastMinuteEngineers
uses different GPIOs than this guide; keep the pattern (CLK, DT, SW each
to a GPIO, module powered from the board) and use this guide's pins:
CLK 25, DT 26, SW 27. Diagram: LastMinuteEngineers.

## Swapping the encoder for something else

A tactile button between GPIO 27 and GND (with INPUT_PULLUP) steps to
the next page per press. A TTP223 touch module wires VCC→3V3, GND→GND,
OUT→GPIO 27 and behaves like that button. A bare capacitive touch pad
is just a wire or foil on GPIO 15 using the ESP32's built-in touch
peripheral — no module at all. The encoder is still the nicest of the
four: it goes backwards as well as forwards.
