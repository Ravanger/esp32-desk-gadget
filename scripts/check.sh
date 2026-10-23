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

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed.")
    sys.exit(1)
print("All checks passed.")
