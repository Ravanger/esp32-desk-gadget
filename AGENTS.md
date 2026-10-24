# AGENTS.md — rules for working on this repository

These rules exist because past agent edits broke this project in
specific, repeatable ways: classic-ESP32 pins leaked in, strapping
pins were used for I2C, a WMO code was both invented and omitted,
personal details crept into a general-purpose guide, and the web
guide drifted from the repository. Follow this file. If a rule here
conflicts with a general instruction, this file wins for this repo.

## Source of truth

- This repository is canonical. The web build guide is derived from
  it. Never edit the web guide without first changing this repo, and
  never treat the web guide's sketch or config names as authoritative
  if they differ from `firmware/desk_gadget.ino`.
- One concern per change, small diffs. A pin change must not rewrite
  all the docs. A rewrite that loses verified facts is a regression,
  even if the new text reads better.

## Board and pins (frozen)

- Board: ESP32-C3 SuperMini only. It breaks out GPIOs 0–10, 20, 21.
- Frozen pin assignment (also the single source in the sketch):

  | Function | GPIO |
  | -------- | ---- |
  | OLED SDA | 4 |
  | OLED SCL | 5 |
  | DHT11 DATA | 3 |
  | Nav push button (also encoder SW) | 10 |
  | Encoder CLK / DT (optional) | 6 / 7 |
  | Potentiometer wiper | 1 (ADC1_CH1) |
  | PIR OUT (optional) | 0 |

- Never use GPIO 2, 8, or 9. They are strapping pins; GPIO 8 also
  drives the onboard LED (simple blue LED on standard boards, WS2812
  on "Plus" variants) and GPIO 9 is the BOOT button.
- Never use classic-ESP32 pins (21/22 for I2C, 25/26/27 for the
  encoder, 34 for the pot) except in a "do not use" warning.
- The pot must be on an ADC1 pin (GPIO 0–4). GPIO 5 is ADC2, and ADC2
  readings are unreliable while WiFi is running. Digital use of
  GPIO 5 as I2C SCL is fine; analog use is not.
- I2C on the C3 runs through the GPIO matrix — there are no fixed
  I2C pins. The sketch must call `Wire.begin(OLED_SDA, OLED_SCL)`
  explicitly, where those defines are 4 and 5.
- The ESP32-C3 has no capacitive-touch peripheral. Touch means the
  TTP223 module, never a bare wire or foil pad.
- The C3 has no 5 GHz radio. All WiFi instructions must say 2.4 GHz.

## ESPHome (default firmware)

- `esphome/desk_gadget.yaml` is the default firmware, for Home
  Assistant. The Arduino sketch is the standalone backup for builders
  without Home Assistant, on the same hardware and wiring. Keep both
  working and in parity: never remove the sketch, never let a
  behaviour change land in one without the other (or a recorded
  deliberate difference in docs/esphome.md), and never change the
  wiring for one firmware alone.
- The ESPHome YAML must use the frozen pins above. Its
  `use_encoder` / `use_pir` substitutions are the ESPHome form of
  the sketch's `USE_ENCODER` / `USE_PIR` defines: changing them
  needs a recompile.
- Outdoor weather in the ESPHome build comes from a Home Assistant
  weather entity, not Open-Meteo. The WMO code table does not apply
  to it; condition labels are mapped from Home Assistant condition
  strings (see docs/esphome.md for the mapping and the other
  deliberate differences). Do not "fix" the ESPHome condition labels
  back to WMO codes.
- Never commit `esphome/secrets.yaml` or ESPHome build output. Both
  are gitignored. The example file is `esphome/secrets.example.yaml`.
- `scripts/check.py` validates the ESPHome YAML (each frozen pin in
  its role, no other GPIO, secrets example, gitignore) and, on a full
  run with the `esphome` tool installed, runs `esphome config` on a
  copy with throwaway secrets; otherwise that step prints SKIP. An
  ESPHome change that fails the static checks is not done, same as a
  sketch change. `esphome config` does not compile: record compile
  results in docs/verified-specs.md, as for the sketch.
- ESPHome behaviour claims (what a component publishes on failure,
  defaults such as WiFi `reboot_timeout`, version floors) must be
  checked against the ESPHome source for the recorded version, not
  assumed from the sketch.

## Facts, not memory

- Never assert a specification, pin, or weather code from memory.
  Check it against the source listed in `docs/verified-specs.md`
  or `docs/sources.md`, and update the source and check date there
  if a fact changes.
- WMO weather codes must match Open-Meteo's official table exactly,
  including code 97 (Heavy thunderstorm). The full pinned list is in
  `scripts/check.py`. Do not add, drop, or renumber codes.
- DHT11 limits are ±2 °C / ±5 % RH, 1 Hz maximum sampling. Do not
  present it as a precision instrument.
- Do not invent prices, costs, or availability. This guide makes no
  cost claims.

## General audience, no personal data

- This is a general-purpose guide. No kit provenance ("starter kit",
  "45-in-1 kit"), no "parts on hand", no personal location as the
  project's location.
- Toronto values in the sketch are a labelled example only. The
  configurable settings are `LOCATION_LAT`, `LOCATION_LON`,
  `LOCATION_TZ`, `LOCATION_NAME`, and `TIMEZONE_POSIX`. Those names
  must match across the sketch, README, and docs.
- Never commit real WiFi credentials. The sketch must keep the
  `YOUR_WIFI_NAME` / `YOUR_WIFI_PASSWORD` placeholders. Never commit
  a personal address, phone number, or account detail.

## Verification before claiming

- Run `python scripts/check.py` before pushing, and include its
  output in the change summary. A change that fails the checks is
  not done. The script includes a wiring-consistency check
  (docs/wiring.md vs the sketch defines) and a PlatformIO compile
  check; if PlatformIO is absent, the compile check prints SKIP
  rather than failing — say so explicitly and do not claim the
  sketch compiles.
- Verify live before claiming a push, merge, or publication: fetch
  the file from GitHub and confirm the expected content is there.
  A successful API response for one file is not proof the whole
  change landed.
- If an audit or review raises a finding, resolve it or record it as
  explicitly unresolved. Never silently drop a finding, and never
  claim a build "passed" while a P1 finding is open.

## Workflow and cost

- Work on a branch, never push directly to `main`. Open a pull
  request; merge via the pull request (web UI or API — API merges
  were proven to work with the current token on 2026-10-23).
- Tag known-good states (for example `v1-c3-pins`) so rollback is a
  checkout, not a reconstruction.

## Local checks and hooks

There is no hosted CI (private repo, GitHub Actions is metered), and
no server-side branch protection (GitHub Free private repos cannot
enable rulesets or protected branches). The hooks below are the only
enforcement, so they must be enabled in every clone. They are a local convenience, not a guarantee: they do not run for pushes made through the GitHub web UI or contents API, or in clones without `core.hooksPath` set.

- One-time setup: `git config core.hooksPath .githooks`
- pre-commit refuses commits on `main`/`master`, then runs
  `scripts/check.py --quick` (no compile).
- pre-push runs the full `scripts/check.py` and blocks pushes to
  `main`/`master`.
- Never bypass hooks with `--no-verify`.
- Agents without hook support must run `python scripts/check.py`
  manually and paste its output.
