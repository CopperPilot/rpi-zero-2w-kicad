# RP3A0 Pico: 6-Layer Raspberry Pi Zero 2W SiP Carrier in Pi Pico Form Factor

![KiCad](https://img.shields.io/badge/KiCad-v10.0.4-blue)
![DRC](https://img.shields.io/badge/DRC-Zero_Errors_%7C_100%25_Routed-brightgreen)
![ERC](https://img.shields.io/badge/ERC-Zero_Errors-brightgreen)
![Fab](https://img.shields.io/badge/JLCPCB-6--Layer_ENIG-orange)
![Tests](https://img.shields.io/badge/Tests-PyTest_Hardware_Suite-blueviolet)

Native **KiCad 10** hardware translation and JLCPCB 6-layer manufacturing release of the open-source **RP3A0 Pico** (`https://github.com/jonny12375/rp3a0`), integrating the **Raspberry Pi RP3A0-AU System-in-Package** (Quad-core 64-bit ARM Cortex-A53 @ 1 GHz + 512 MiB LPDDR2 SDRAM) into a Raspberry Pi Pico castellated module with Micro-HDMI, USB-C OTG, and microSD storage.

---

## 1. System Architecture

```text
+-----------------------------------------------------------------------------------+
|                                 RP3A0 PICO (6-LAYER)                              |
|                                                                                   |
|  [J3: USB-C 5V/OTG] ---> [Q1: DMG2305UX] ---> 5V_CORE ---> [U3: RT8088AWSC]       |
|         |                                       (I2C)           |                 |
|         +--------------> [U4: PAM2306AYPKE]                     v                 |
|         |                  |            |                  VDD_CORE (0.6-1.35V)   |
|         |                  v            v                       |                 |
|         |             3V3 (1A)      1V8 (1A) ---> [U2: RT9081A] |                 |
|         |                  |            |              |        |                 |
|         |                  |            |         DDR_1V25      |                 |
|         v                  v            v              v        v                 |
|  [D2: DFLS130L]        +-----------------------------------------------+          |
|         |              |               U1: RP3A0-AU SiP                |          |
|         v              |   4x Cortex-A53 @ 1GHz + 512MiB LPDDR2 BGA    |          |
|  [J2: Micro-HDMI] <----+-- 4x TMDS (FL1-FL4 EXC24CH900U) + CEC/HPD (U5)|          |
|                        |                                               |          |
|  [J1: MicroSD]    <----+-- 4-bit SDIO (SD_CLK, SD_CMD, SD_DAT0..3)     |          |
|  [Y1: 19.2MHz]    <----+-- Primary Crystal Oscillator (18pF C6, C9)    |          |
|  [J5: Pico 40-Pin]<----+-- Castellated GPIO0..GPIO25, 3V3, VBUS, GND   |          |
+-----------------------------------------------------------------------------------+
```

---

## 2. Hardware Specifications

- **SoC / SiP (`U1`):** Broadcom / Raspberry Pi `RP3A0-AU` (323-ball 0.65 mm pitch BGA, 15 × 15 mm; harvested and reballed with 0.3 mm solder balls from a donor Raspberry Pi Zero 2W).
- **Form Factor & Dimensions:** `60.00 mm × 20.35 mm` overall (`51.00 mm × 20.35 mm` standard Raspberry Pi Pico 40-pin castellated footprint + `9.00 mm` right-side overhang for Micro-HDMI and USB-C receptacles).
- **6-Layer JLCPCB Stackup (`1.6 mm` ENIG):**
  - `F.Cu` (1 oz): All 93 SMT components, `U1` BGA fanout, `TP10`–`TP22`/`TP28` Wi-Fi/BT SDIO/UART test pads, and local power polygons.
  - `In1.Cu` (0.5 oz): Continuous `GND` reference plane + inner BGA escape routing.
  - `In2.Cu` (0.5 oz): Split power planes (`5V`, `1V8`, `DDR_1V25`, `VDD_CORE`) + high-speed routing.
  - `In3.Cu` (0.5 oz): Split power planes (`3V3`, `HDMI_5V`, `VDD_CORE`) + signal routing.
  - `In4.Cu` (0.5 oz): GPIO, SDIO, and HDMI routing layer.
  - `B.Cu` (1 oz): Solid `GND` pour, bottom power/JTAG test points (`TP1`–`TP9`, `TP23`–`TP27`), and `J4` USB Host `USB_ID` solder jumper.
- **Power Management:**
  - `U4` (`PAM2306AYPKE`, LCSC `C508236`): Dual 1 A synchronous buck converter generating `3V3` (`L2` = 4.7 µH) and `1V8` (`L3` = 2.2 µH).
  - `U3` (`RT8088AWSC`, LCSC `C5739348`): I2C-programmable 3 A synchronous buck regulator generating `VDD_CORE` (`L1` = 470 nH).
  - `U2` (`RT9081A-1BGQZA(2)`, LCSC `C7303451`): 500 mA ultra-low-dropout LDO generating `DDR_1V25` from `1V8` (`VBIAS` = `3V3`).
  - `Q1` (`DMG2305UX-7`, LCSC `C150470`): High-side P-MOSFET switch gating `5V_CORE`.

---

## 3. Repository Structure

```text
.
├── Makefile                        # Unified root build, lint, test, validate & fab interface
├── README.md                       # System architecture & project documentation
└── pcb/
    ├── Makefile                    # Hardware verification (ERC/DRC/PyTest) & JLCPCB fab targets
    ├── README.md                   # Detailed PCB stackup, BOM & manufacturing guide
    ├── export_manufacturing.py     # Automated JLCPCB Gerber, Drill, BOM, CPL, D356 & PDF exporter
    ├── fp-lib-table                # Project-local footprint library table (${KIPRJMOD})
    ├── sym-lib-table               # Project-local symbol library table (${KIPRJMOD})
    ├── rp3a0-mini.kicad_pro        # KiCad 10 project & JLCPCB 6-layer design rules
    ├── rp3a0-mini.kicad_dru        # Custom DRC rule for J5 castellated edge pads
    ├── rp3a0-mini.kicad_sch        # Root hierarchical schematic sheet
    ├── rp3a-mini-power.kicad_sch   # Power distribution, PMICs, crystal & U1 power/GND banks
    ├── rp3a0-mini-gpio.kicad_sch   # 40-pin Pi Pico castellated header (J5) & GPIO bank
    ├── rp3a0-mini-hdmi.kicad_sch   # Micro-HDMI (J2), TMDS chokes (FL1-FL4) & USB-C OTG (J3)
    ├── rp3a0-mini-wireless-sd.kicad_sch # MicroSD socket (J1) & Wi-Fi/BT breakout test pads
    ├── rp3a0-mini-misc.kicad_sch   # VideoCore/ARM JTAG test pads, status LED & NC balls
    ├── rp3a0-mini.kicad_pcb        # 6-layer routed PCB layout (0 DRC errors, 100% routed)
    ├── libs/
    │   ├── symbols/rp3a0.kicad_sym # Consolidated project symbol library (34 symbols)
    │   └── rp3a0.pretty/           # Consolidated project footprint library (23 footprints)
    └── tests/
        ├── conftest.py             # KiCad 10 S-expression parsers & ERC/DRC pytest fixtures
        └── test_pcb.py             # Automated hardware verification test suite
```

---

## 4. Quickstart & Verification Commands

```bash
# Run full test suite and static analysis (PyTest + ERC + DRC + Ruff)
make all

# Run KiCad CLI Electrical & Design Rule Checks directly
make erc
make drc

# Run CopperPilot stage-gated validation
make validate

# Generate complete JLCPCB 6-layer manufacturing release bundle in pcb/build/
make build-pcb
```
