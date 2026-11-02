# ESP-12F Battery + USB Board (KiCad)

KiCad EDA hardware project. Firmware for the ESP-12F will also live in this repo (not yet present). There is no package manager, test suite, lint, CI, or build step yet. Do not look for `package.json`, `requirements.txt`, `Makefile`, or `cargo` commands — none exist until firmware is added.

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

## Firmware ESP-12F (software)

**Stato:** il firmware va nella cartella `src/` (presente, con un `README.md` placeholder). Mantenerla separata dal progetto KiCad in `esp12f_battery_usb/`.

**Pinout rilevante per il firmware** (da `ESP-12F.md` e dallo schema):
- UART: `ESP_TXD` / `ESP_RXD` collegati al CH340C tramite R11/R12 (470 Ω) — seriale per debug e flash.
- Boot strapping: `GPIO15` pull-down (boot da flash SPI interno), `GPIO0`/`GPIO2`/`EN`/`RST` pull-up (10 kΩ).
  - `GPIO0 = HIGH`: boot normale. `GPIO0 = LOW`: modalità flash/bootloader.
- ADC: pin `ADC` (TOUT) dell'ESP-12F, range 0–1,0 V. Partitore R20 (100 kΩ) / R21 (27 kΩ) su VBAT → 0,89 V a 4,2 V. Jumper `JP1` (`BAT_ADC_EN`) disconnette il partitore per liberare l'ADC per sensori esterni.
- LED: `LED3` (blu) segnala +3,3 V attivo.
- Headers J3/J4: breakout 1×8 su GPIO, +3,3 V e GND.

**Flash / upload:**
- L'hardware supporta già esptool, Arduino IDE, PlatformIO e VS Code (auto-reset DTR/RTS su GPIO0 + RST, ponte CH340C).
- CH340C è alimentato solo da VBUS: la seriale funziona solo con USB collegato.
- Fallback manuale: `SW2` = RESET, `SW3` = FLASH/BOOT (porta GPIO0 a GND).

**Note operative:**
- Non usare `GPIO0` come output generico se devi entrare spesso in modalità flash: è usato per il boot strapping.
- L'ADC dell'ESP8266 è a singola posizione e sensibile: tieni il partitore se leggi la batteria, altrimenti togli JP1 per sensori esterni.

## Version control

- Remote: `git@github.com:cesare-casirati/ESP-12F-DevKit.git` (branch `main`, SSH autenticazione già configurata su questa macchina).
- Commit first, then push: `git push -u origin main` (già eseguito per il commit iniziale).
- Il `.gitignore` esclude `.DS_Store`, `__pycache__/`, `*.kicad_prl`, `esp12f_battery_usb-backups/`, e gli export generati (`schematic.pdf`, `schematic_svg/`, `erc.rpt`).