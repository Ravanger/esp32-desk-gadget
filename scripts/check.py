#!/usr/bin/env python3
"""Local guardrail checks for the ESP32 Desk Gadget repository.

Run from the repository root:  python scripts/check.py [--quick]
(python3 also works). --quick skips the PlatformIO compile check.

Exit code 0 = all checks passed. Any failure prints FAIL and exits 1.
The compile check clones pinned libraries from GitHub (git clone); the
other checks need no network. No hosted CI, no cost. See AGENTS.md for the rules
these checks enforce.

Checks:
  1. Sketch pin defines match the frozen SuperMini assignment.
  2. Forbidden classic-ESP32 pins do not appear as assignments
     (allowed only in explicit "do not use" warnings in wiring.md).
  3. codeText() WMO cases exactly match Open-Meteo's official list.
  4. Config constant names match across sketch, README, and docs.
  5. No real WiFi credentials (placeholders only).
  6. No personal/kit/cost phrases in docs.
  7. All internal markdown links resolve; no hotlinked images
     (excluding ESPHome's local build output under any .esphome/
     directory, which holds third-party component READMEs).
  8. Wiring table in docs/wiring.md matches the sketch pin defines.
  9. Sketch avoids strapping/classic pins, uses an ADC1 pot pin, makes
     no blocking getLocalTime(&t), and has no long delay() in loop().
 10. Docs have no price/cost wording and end with a Contents nav line.
 11. No secrets; tracked text files use LF line endings.
 12. Sketch compiles for esp32-c3-devkitm-1 with PlatformIO, both as
     shipped and with every option define set to 1
     (skipped, not failed, when PlatformIO is not installed or --quick).
 13. ESPHome YAML exists, assigns the frozen pins to the same roles
     and uses no other GPIO, ships a secrets example, gitignores
     secrets.yaml, and passes `esphome config` against throwaway
     secrets (skipped, not failed, when esphome is absent or --quick).
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUICK = "--quick" in sys.argv[1:]
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
    "BUTTON_PIN": "10",
    "ENC_CLK": "6",
    "ENC_DT": "7",
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
for _name, _value in [("WIFI_SSID", "YOUR_WIFI_NAME"),
                      ("WIFI_PASSWORD", "YOUR_WIFI_PASSWORD")]:
    _exact = re.findall(
        rf'^[ \t]*const[ \t]+char[ \t]*\*[ \t]*{_name}[ \t]*=[ \t]*"{_value}"[ \t]*;[ \t]*(?://.*)?$',
        sketch, re.M)
    _assigns = re.findall(rf'\b{_name}\b[ \t]*=(?!=)|#[ \t]*define[ \t]+{_name}\b',
                          sketch)
    check(f"{_name} is the placeholder, assigned exactly once",
          len(_exact) == 1 and len(_assigns) == 1)

# --- 6. No personal / kit / cost phrases -----------------------------------
BANNED = ["starter kit", "45-in-1", "parts on hand", "micro USB",
          "$0, all parts", "price", "cheap"]
for md in sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
    text = md.read_text(encoding="utf-8").lower()
    for phrase in BANNED:
        check(f"no '{phrase}' in {md.relative_to(ROOT)}",
              phrase.lower() not in text)

# --- 7. Internal links resolve ----------------------------------------------
# ESPHome's local build output (esphome/.esphome/) holds third-party
# component READMEs with hotlinked images and relative links that do
# not resolve in this tree; it is gitignored build output, not repo
# content, so it is skipped here.
for md in sorted(ROOT.rglob("*.md")):
    if ".esphome" in md.parts:
        continue
    text = md.read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith("http") or link.startswith("#"):
            continue
        target = (md.parent / link.split("#")[0]).resolve()
        check(f"link {link} from {md.relative_to(ROOT)}",
              target.exists(), "missing file")
    remote_imgs = re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", text)
    check(f"no hotlinked images in {md.relative_to(ROOT)} (use assets/)",
          not remote_imgs, f"{remote_imgs}")

# --- 8. Wiring table vs sketch ------------------------------------------
# Parse the wiring table in docs/wiring.md and compare every signal
# and power connection against the sketch defines and the frozen rules.
import os
import shutil
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
    ("Push button", "Leg A"): "10",
    ("Rotary encoder (optional)", "CLK"): "6",
    ("Rotary encoder (optional)", "DT"): "7",
    ("Rotary encoder (optional)", "SW"): "10",
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
    ("Push button", "Leg B"): "GND",
    ("Rotary encoder (optional)", "+ / VCC"): "3V3",
    ("Potentiometer (10K)", "End 1"): "3V3",
    ("Potentiometer (10K)", "End 2"): "GND",
    ("PIR (optional)", "VCC"): "5V",
}
for (module, pin), want in POWER.items():
    hit = [t for (m, p, t) in rows if m == module and p == pin]
    check(f"wiring {module} {pin} -> {want}",
          hit and want in hit[0], f"found {hit}")

# --- 9. Sketch rules (AGENTS.md) ----------------------------------------
BAD_PINS = {2, 8, 9, 21, 22, 25, 26, 27, 34}
SUPERMINI_PINS = set(range(0, 11)) | {20, 21}
pin_defs = {n: int(v) for n, v in defines.items()
            if re.search(r"(_PIN|^OLED_|^ENC_)", n)}
bad = {n: v for n, v in pin_defs.items()
       if v in BAD_PINS or v not in SUPERMINI_PINS}
check("sketch pin defines avoid strapping/classic pins and fit SuperMini",
      bool(pin_defs) and not bad, f"bad {bad}" if bad else "no pin defines")
check("pot pin is ADC1 (GPIO 0-4)", 0 <= pin_defs.get("POT_PIN", -1) <= 4,
      f"POT_PIN={pin_defs.get('POT_PIN')}")
check("no blocking getLocalTime(&t) (use getLocalTime(&t, 0))",
      not re.search(r"getLocalTime\(\s*&\w+\s*\)", sketch))
loop_src = sketch[sketch.find("void loop()"):]
long_delays = [int(n) for n in re.findall(r"delay\((\d+)\)", loop_src)
               if int(n) > 10]
check("no delay() > 10 ms inside loop()",
      "void loop()" in sketch and not long_delays, f"found {long_delays}")

# --- 10. Doc wording and navigation ---------------------------------------
PRICE_RE = re.compile(r"\$\s?\d|price|cheap", re.IGNORECASE)
for md in sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
    hits = PRICE_RE.findall(md.read_text(encoding="utf-8"))
    check(f"no price/cost wording in {md.relative_to(ROOT)}", not hits,
          f"found {hits[:5]}")
for md in sorted((ROOT / "docs").glob("*.md")):
    tail = md.read_text(encoding="utf-8").rstrip().splitlines()[-1:]
    check(f"nav line with [Contents](../README.md) in {md.relative_to(ROOT)}",
          bool(tail) and "[Contents](../README.md)" in tail[0])

# --- 11. Secrets and line endings -----------------------------------------
try:
    ls = subprocess.run(["git", "ls-files", "--eol"], cwd=ROOT,
                        capture_output=True, text=True)
    tracked = ls.stdout.splitlines() if ls.returncode == 0 else []
except FileNotFoundError:
    tracked = []
if not tracked:
    print("[skip] secrets / LF checks — git ls-files returned nothing "
          "(git missing or not a git checkout?)")
SECRET_RE = re.compile(
    r'(?i)(password|passwd|psk)\s*=\s*"(?!YOUR_)[^"]+"'
    r'|#define\s+WIFI_(SSID|PASSWORD)\s+"(?!YOUR_)[^"]*[^"\s][^"]*"')
secret_hits, crlf_files = [], []
for row in tracked:
    meta, _, rel = row.partition("	")
    index_eol = meta.split()[0]
    if index_eol == "i/-text":
        continue
    if index_eol in ("i/crlf", "i/mixed"):
        crlf_files.append(rel)
    if rel == "scripts/check.py":
        continue
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    if SECRET_RE.search(text):
        secret_hits.append(rel)
if tracked:
    check("no credential assignments other than YOUR_ placeholders",
          not secret_hits, f"in {secret_hits}")
    check("tracked text files use LF line endings (index)", not crlf_files,
          f"CRLF in {crlf_files}")

# --- 12. Compile check (PlatformIO, skipped if absent or --quick) --------
PINNED_LIBS = [
    ("adafruit/Adafruit-GFX-Library", "1.13.0"),
    ("adafruit/Adafruit_BusIO", "1.17.4"),
    ("adafruit/Adafruit_SSD1306", "2.5.17"),
    ("adafruit/Adafruit_Sensor", "1.1.15"),
    ("adafruit/DHT-sensor-library", "1.4.7"),
    ("bblanchon/ArduinoJson", "v7.4.3"),
]
pio = None if QUICK else shutil.which("pio")
if not pio and not QUICK:
    for cand in [Path.home() / ".platformio/penv/Scripts/pio.exe",
                 Path.home() / ".platformio/penv/bin/pio",
                 Path.home() / ".local/bin/pio",
                 Path.home() / "workspace/.pio-venv/bin/pio"]:
        if cand.exists():
            pio = str(cand)
            break
if pio:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "platformio.ini").write_text(
            "[env:esp32-c3-devkitm-1]\n"
            "platform = espressif32@6.9.0\n"
            "board = esp32-c3-devkitm-1\n"
            "framework = arduino\n"
            "build_flags =\n"
            "    -DARDUINO_USB_CDC_ON_BOOT=1\n"
            "    -DARDUINO_USB_MODE=1\n")
        # Cloned into lib/ rather than lib_deps: PlatformIO resolves lib_deps
        # dependencies through its registry, which some networks block.
        clone_failed = False
        for repo, tag in PINNED_LIBS:
            try:
                clone = subprocess.run(
                    ["git", "clone", "-q", "--depth", "1", "--branch", tag,
                     f"https://github.com/{repo}.git",
                     str(td / "lib" / repo.split("/")[1])],
                    capture_output=True, text=True, timeout=300)
                err = (clone.stderr.strip() or f"exit {clone.returncode}") if clone.returncode else ""
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                err = str(e)
            if err:
                clone_failed = True
                print(f"[skip] git clone {repo}@{tag} failed: {err}")
        src = td / "src"
        src.mkdir()
        sketch = read("firmware/desk_gadget.ino")
        all_on, n_opts = re.subn(
            r"^(#define (?:USE_PIR|USE_ENCODER|WIFI_LOW_TX_POWER)) 0\b",
            r"\1 1", sketch, flags=re.MULTILINE)
        check("all 3 option defines found for the all-options build",
              n_opts == 3, f"matched {n_opts}")
        variants = [("default options", sketch), ("all options = 1", all_on)]
        env = dict(os.environ)
        core_dir = Path.home() / "workspace/.platformio"
        if core_dir.exists():
            env["PLATFORMIO_CORE_DIR"] = str(core_dir)
        if clone_failed:
            print("[skip] compile — a library clone failed (network?); the sketch "
                  "is NOT compile-verified by this run")
        else:
            fw = td / ".pio/build/esp32-c3-devkitm-1/firmware.bin"
            for label, code in variants:
                (src / "main.cpp").write_text("#include <Arduino.h>\n" + code)
                fw.unlink(missing_ok=True)
                proc = subprocess.run([pio, "run", "-e", "esp32-c3-devkitm-1"],
                                      cwd=td, capture_output=True, text=True,
                                      env=env, timeout=900)
                check(f"sketch compiles for esp32-c3-devkitm-1, {label} (PlatformIO)",
                      proc.returncode == 0 and fw.exists(),
                      (proc.stdout + proc.stderr)[-1500:] if proc.returncode else "")
elif QUICK:
    print("[skip] compile check — --quick")
else:
    print("[skip] compile check — PlatformIO (pio) not found; "
          "install it and re-run to include the compile check")

# --- 13. ESPHome (default firmware) -------------------------------------
esphome_yaml = ROOT / "esphome" / "desk_gadget.yaml"
check("ESPHome YAML exists", esphome_yaml.exists())
if esphome_yaml.exists():
    yaml_text = esphome_yaml.read_text(encoding="utf-8")
    ESPHOME_PIN_PATTERNS = {
        "OLED_SDA": r"\bsda:\s*GPIO(\d+)",
        "OLED_SCL": r"\bscl:\s*GPIO(\d+)",
        "DHT_PIN": r"platform: dht\s+pin:\s*GPIO(\d+)",
        "POT_PIN": r"platform: adc\s+pin:\s*GPIO(\d+)",
        "BUTTON_PIN": r"id: nav_button\s+pin:\s+number:\s*GPIO(\d+)",
        "PIR_PIN": r"id: pir_sensor\s+device_class: motion\s+pin:\s+number:\s*GPIO(\d+)",
        "ENC_CLK": r"pin_a:\s+number:\s*GPIO(\d+)",
        "ENC_DT": r"pin_b:\s+number:\s*GPIO(\d+)",
    }
    for name, pattern in ESPHOME_PIN_PATTERNS.items():
        m = re.search(pattern, yaml_text)
        want = EXPECTED_PINS[name]
        check(f"ESPHome {name} == GPIO{want}", bool(m) and m.group(1) == want,
              f"found {m.group(1) if m else 'nothing'}")
    used = set(re.findall(r"\bGPIO(\d+)\b", yaml_text))
    check("ESPHome YAML uses only the frozen pins",
          used == set(EXPECTED_PINS.values()),
          f"uses GPIO {sorted(used, key=int)}")
    check("ESPHome secrets example exists",
          (ROOT / "esphome" / "secrets.example.yaml").exists())
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8") \
        if (ROOT / ".gitignore").exists() else ""
    check(".gitignore covers esphome/secrets.yaml",
          "esphome/secrets.yaml" in gitignore)
    esphome_bin = shutil.which("esphome")
    if esphome_bin and not QUICK:
        # Validate a copy next to throwaway secrets, so the check needs no
        # real secrets.yaml. The directory is under gitignored .esphome/.
        import base64
        work = ROOT / "esphome" / ".esphome" / "check"
        work.mkdir(parents=True, exist_ok=True)
        shutil.copy(esphome_yaml, work / "desk_gadget.yaml")
        (work / "secrets.yaml").write_text(
            'wifi_ssid: "check"\nwifi_password: "check-password"\n'
            f'api_key: "{base64.b64encode(os.urandom(32)).decode()}"\n',
            encoding="utf-8")
        proc = subprocess.run(
            [esphome_bin, "config", str(work / "desk_gadget.yaml")],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
        check("esphome config validates desk_gadget.yaml",
              proc.returncode == 0,
              (proc.stdout + proc.stderr)[-1500:] if proc.returncode else "")
    else:
        print("[skip] esphome config — esphome tool not found or --quick; "
              "the YAML is NOT config-validated by this run")

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed.")
    sys.exit(1)
print("All checks passed.")
