#!/usr/bin/env python3
"""Local guardrail checks for the ESP32 Desk Gadget repository.

Run from the repository root:  ./scripts/check.sh
(or: python3 scripts/check.sh)

Exit code 0 = all checks passed. Any failure prints FAIL and exits 1.
No network access, no hosted CI, no cost. See AGENTS.md for the rules
these checks enforce.

Checks:
  1. Sketch pin defines match the frozen SuperMini assignment.
  2. Forbidden classic-ESP32 pins do not appear as assignments
     (allowed only in explicit "do not use" warnings in wiring.md).
  3. codeText() WMO cases exactly match Open-Meteo's official list.
  4. Config constant names match across sketch, README, and docs.
  5. No real WiFi credentials (placeholders only).
  6. No personal/kit/cost phrases in docs.
  7. All internal markdown links resolve.
  8. Wiring table in docs/wiring.md matches the sketch pin defines.
  9. Sketch compiles for esp32-c3-devkitm-1 with PlatformIO
     (skipped, not failed, when PlatformIO is not installed).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES = []


def check(name, ok, detail=""):
    status = "ok  " if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


# --- 1. Frozen pins -------------------------------------------------------
EXPECTED_PINS = {
    "OLED_SDA": "4",
    "OLED_SCL": "5",
    "DHT_PIN": "3",
    "ENC_CLK": "6",
    "ENC_DT": "7",
    "ENC_SW": "10",
    "POT_PIN": "1",
    "PIR_PIN": "0",
}
sketch = read("firmware/desk_gadget.ino")
defines = dict(re.findall(r"#define\s+(\w+)\s+(\d+)", sketch))
for name, want in EXPECTED_PINS.items():
    check(f"pin {name} == {want}", defines.get(name) == want,
          f"found {defines.get(name)}")
check("Wire.begin uses OLED_SDA/OLED_SCL",
      "Wire.begin(OLED_SDA, OLED_SCL)" in sketch)

# --- 2. Forbidden pins ----------------------------------------------------
# wiring.md is allowed to name forbidden pins in its warning paragraph;
# strip lines that explicitly say "do not exist" / "do not use" first.
FORBIDDEN = ["GPIO 21", "GPIO 22", "GPIO 25", "GPIO 26", "GPIO 27",
             "GPIO 34"]
for md in sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
    text = md.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines()
             if "do not exist" not in ln and "do not use" not in ln
             and "do not apply" not in ln]
    body = "\n".join(lines)
    for pin in FORBIDDEN:
        check(f"no assignment of {pin} in {md.relative_to(ROOT)}",
              pin not in body, f"found '{pin}'")

# --- 3. WMO codes ----------------------------------------------------------
# Open-Meteo official WMO interpretation codes (see docs/verified-specs.md).
# Note: 97 (Heavy thunderstorm) IS in the official list; models without
# an explicit hail forecast report 95 and 97, hail models report 96/99.
EXPECTED_WMO = {0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
                71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 97, 99}
found = set()
for line in sketch.splitlines():
    if "case " in line and "return" in line:
        found.update(int(n) for n in re.findall(r"case (\d+)", line))
check("WMO codes in codeText() match Open-Meteo list",
      found == EXPECTED_WMO,
      f"missing {sorted(EXPECTED_WMO - found)}, extra {sorted(found - EXPECTED_WMO)}")

# --- 4. Config names -------------------------------------------------------
CONFIG_NAMES = ["LOCATION_LAT", "LOCATION_LON", "LOCATION_TZ",
                "LOCATION_NAME", "TIMEZONE_POSIX",
                "WIFI_SSID", "WIFI_PASSWORD"]
for name in CONFIG_NAMES:
    check(f"config {name} in sketch", name in sketch)
for doc in ["README.md", "docs/libraries-and-setup.md"]:
    text = read(doc)
    for name in ["LOCATION_LAT", "LOCATION_LON", "LOCATION_TZ",
                 "LOCATION_NAME", "TIMEZONE_POSIX"]:
        check(f"config {name} in {doc}", name in text)

# --- 5. No real credentials -------------------------------------------------
check("WIFI_SSID is placeholder",
      '"YOUR_WIFI_NAME"' in sketch)
check("WIFI_PASSWORD is placeholder",
      '"YOUR_WIFI_PASSWORD"' in sketch)

# --- 6. No personal / kit / cost phrases -----------------------------------
BANNED = ["starter kit", "45-in-1", "parts on hand", "micro USB",
          "$0, all parts"]
for md in sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
    text = md.read_text(encoding="utf-8").lower()
    for phrase in BANNED:
        check(f"no '{phrase}' in {md.relative_to(ROOT)}",
              phrase.lower() not in text)

# --- 7. Internal links resolve ----------------------------------------------
for md in sorted(ROOT.rglob("*.md")):
    text = md.read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith("http") or link.startswith("#"):
            continue
        target = (md.parent / link.split("#")[0]).resolve()
        check(f"link {link} from {md.relative_to(ROOT)}",
              target.exists(), "missing file")

# --- 8. Wiring table vs sketch ------------------------------------------
# Parse the wiring table in docs/wiring.md and compare every signal
# and power connection against the sketch defines and the frozen rules.
import shutil
import subprocess
import tempfile

wiring = read("docs/wiring.md")
rows = []
current_module = ""
in_table = False
for line in wiring.splitlines():
    if line.startswith("| Module |"):
        in_table = True
        continue
    if in_table:
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Empty first cell = continuation row for the previous module;
        # a cell of only dashes = the separator row, which is skipped.
        if len(cells) < 3 or (cells[0] and set(cells[0]) <= {"-", " "}):
            continue
        if cells[0]:
            current_module = cells[0]
        rows.append((current_module, cells[1], cells[2]))

SIGNAL_PINS = {
    ("OLED (SSD1306)", "SDA"): "4",
    ("OLED (SSD1306)", "SCL"): "5",
    ("DHT11", "DATA (OUT)"): "3",
    ("Rotary encoder", "CLK"): "6",
    ("Rotary encoder", "DT"): "7",
    ("Rotary encoder", "SW"): "10",
    ("Potentiometer (10K)", "Wiper (middle)"): "1",
    ("PIR (optional)", "OUT"): "0",
}
found_signals = {}
for module, pin, target in rows:
    gpio = re.search(r"GPIO (\d+)", target)
    if gpio:
        found_signals[(module, pin)] = gpio.group(1)
        check(f"wiring {module} {pin} not a strapping/classic pin",
              gpio.group(1) not in {"2", "8", "9", "21", "22", "25",
                                    "26", "27", "34"},
              f"assigned GPIO {gpio.group(1)}")
for key, want in SIGNAL_PINS.items():
    check(f"wiring {key[0]} {key[1]} == GPIO {want}",
          found_signals.get(key) == want,
          f"found {found_signals.get(key)}")

POWER = {
    ("OLED (SSD1306)", "VCC"): "3V3",
    ("DHT11", "VCC"): "3V3",
    ("Rotary encoder", "+ / VCC"): "3V3",
    ("Potentiometer (10K)", "End 1"): "3V3",
    ("Potentiometer (10K)", "End 2"): "GND",
    ("PIR (optional)", "VCC"): "5V",
}
for (module, pin), want in POWER.items():
    hit = [t for (m, p, t) in rows if m == module and p == pin]
    check(f"wiring {module} {pin} -> {want}",
          hit and want in hit[0], f"found {hit}")

# --- 9. Compile check (PlatformIO, skipped if absent) ---------------------
pio = shutil.which("pio")
if not pio:
    for cand in [Path.home() / ".local/bin/pio",
                 Path.home() / "workspace/.pio-venv/bin/pio"]:
        if cand.exists():
            pio = str(cand)
            break
if pio:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "platformio.ini").write_text(
            "[env:esp32-c3-devkitm-1]\n"
            "platform = espressif32\n"
            "board = esp32-c3-devkitm-1\n"
            "framework = arduino\n"
            "lib_deps =\n"
            "    adafruit/Adafruit GFX Library\n"
            "    adafruit/Adafruit SSD1306\n"
            "    adafruit/DHT sensor library\n"
            "    bblanchon/ArduinoJson\n"
            "build_flags =\n"
            "    -DUSB_CDC_ON_BOOT=1\n")
        src = td / "src"
        src.mkdir()
        (src / "main.cpp").write_text(
            "#include <Arduino.h>\n" + read("firmware/desk_gadget.ino"))
        env = dict(__import__("os").environ)
        core_dir = Path.home() / "workspace/.platformio"
        if core_dir.exists():
            env["PLATFORMIO_CORE_DIR"] = str(core_dir)
        proc = subprocess.run([pio, "run", "-e", "esp32-c3-devkitm-1"],
                              cwd=td, capture_output=True, text=True,
                              env=env, timeout=900)
        check("sketch compiles for esp32-c3-devkitm-1 (PlatformIO)",
              proc.returncode == 0 and
              (td / ".pio/build/esp32-c3-devkitm-1/firmware.bin").exists(),
              (proc.stdout + proc.stderr)[-500:] if proc.returncode else "")
else:
    print("[skip] compile check — PlatformIO (pio) not found; "
          "install it and re-run to include the compile check")

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed.")
    sys.exit(1)
print("All checks passed.")
