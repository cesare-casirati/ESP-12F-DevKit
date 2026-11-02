# ESP-12F Battery + USB Board (KiCad)

KiCad EDA hardware project, not a software repo. There is no package manager, test suite, lint, CI, or build step. Do not look for `package.json`, `requirements.txt`, `Makefile`, or `cargo` commands — none exist.

## Repo layout

- `ESP-12F.md` — architecture doc: 6 functional blocks, ERC result (0 errors, 0 warnings), list of generated files.
- `esp12f_battery_usb/` — the KiCad project:
  - `esp12f_battery_usb.kicad_pro` / `.kicad_sch` / `.kicad_pcb` / `.kicad_prl` — project, schematic, PCB, project settings
  - `build_project.py` — **regenerates `esp12f_battery_usb.kicad_sch`** from Python (imports `make_schematic`). The `.kicad_sch` is derived code. **Il progetto è stato creato da un agente, ma sono state apportate modifiche manuali dopo la generazione:** rigenerando con `build_project.py` si sovrascrivono quelle modifiche manuali. Prima di rigenerare, diffa il `.kicad_sch` generato contro quello committato, o preferisci l'editing diretto in KiCad GUI su `esp12f_battery_usb.kicad_pro`.
  - `make_schematic.py` — `SchematicBuilder` library + KiCad symbol extraction
  - `erc.rpt` — last ERC report: `0 Errors 0 Warnings`
  - `schematic.pdf` (A3) and `schematic_svg/esp12f_battery_usb.svg` — exports
  - `esp12f_battery_usb-backups/` — dated KiCad/zips; `**/__pycache__/` — Python cache. Safe to ignore.

## Circuit (summary)

USB-C 5V → PTC 500mA fuse → TP4056 LiPo charger (500 mA) → battery JST. Power-path AO3401A P-MOSFET auto-switches battery vs USB (USB wins, battery stays isolated from load). SW1 → AP2112K-3.3 LDO (600 mA) → +3.3V with 100 µF tantalum bulk cap (ESP8266 RF brownout protection). CH340C USB-UART bridge (powered only from VBUS, zero battery draw) with MMBT3904 DTR/RTS auto-reset (GPIO0 + RST) for esptool/Arduino IDE/PlatformIO flash. ESP-12F with boot strapping (GPIO15 pull-down, GPIO0/2/EN/RST pull-ups), ADC divider (100k/27k → 0.89 V at 4.2 V, jumper JP1 `BAT_ADC_EN`), and 1x8 breakout headers J3/J4.

## Verification

ERC is run with KiCad CLI (the only executable check):

```
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --report erc.rpt esp12f_battery_usb.kicad_sch
```

Run from `esp12f_battery_usb/`. Expected: `** ERC messages: 0 Errors 0 Warnings`. KiCad is installed at `/Applications/KiCad/KiCad.app` (macOS); `kicad-cli` lives under `Contents/MacOS/`.

## Regenerating the schematic

`python3 build_project.py` from `esp12f_battery_usb/` rewrites `esp12f_battery_usb.kicad_sch`.

**Gotcha:** both scripts hardcode absolute paths to the author's machine:

- `build_project.py`: `PROJECT_DIR = '/Users/mac/.gemini/antigravity/scratch/esp12f_battery_usb'` (writes the `.kicad_sch` there, not to the local repo)
- `make_schematic.py`: `SYMBOLS_DIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'`

If you run them here, edit those paths first (or run KiCad GUI on `esp12f_battery_usb.kicad_pro` instead).

## Board bring-up notes

- CH340C is off when USB is unplugged (powered from VBUS) — serial only works with USB connected.
- Auto-reset requires DTR/RTS; manual fallback: SW2 = RESET, SW3 = FLASH/BOOT (GPIO0).
- ADC reads battery through JP1; remove the solder jumper to free the ADC pin for an external sensor.

## Version control

- Remote: `git@github.com:cesare-casirati/ESP-12F-DevKit.git` (branch `main`, SSH autenticazione già configurata su questa macchina).
- Commit first, then push: `git push -u origin main` (già eseguito per il commit iniziale).
- Il `.gitignore` esclude `.DS_Store`, `__pycache__/`, `*.kicad_prl`, `esp12f_battery_usb-backups/`, e gli export generati (`schematic.pdf`, `schematic_svg/`, `erc.rpt`).