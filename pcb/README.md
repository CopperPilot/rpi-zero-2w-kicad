# RP3A0 Pico PCB — KiCad 10 Design & JLCPCB 6-Layer Manufacturing

This directory contains the native **KiCad 10** schematic, 6-layer PCB layout, project-local symbol/footprint libraries, PyTest verification suite, and automated JLCPCB fabrication/assembly export pipeline for the **RP3A0 Pico**.

## 1. Hierarchical Schematic Sheets

| Sheet Name | File | Contents |
|---|---|---|
| `Root` | `rp3a0-mini.kicad_sch` | Top-level hierarchical sheet linking the 5 functional subsheets |
| `Power` | `rp3a-mini-power.kicad_sch` | `U4` (`PAM2306AYPKE`), `U3` (`RT8088AWSC`), `U2` (`RT9081A-1BGQZA(2)`), `Q1` (`DMG2305UX-7`), `Y1` (19.2 MHz crystal), decoupling, and `U1` Power/GND/PLL units |
| `GPIO` | `rp3a0-mini-gpio.kicad_sch` | `U1` GPIO bank (`GPIO0`–`GPIO27`), I2C pull-ups (`R1`, `R2`), and 40-pin Raspberry Pi Pico castellated edge header (`J5`) |
| `HDMI_USB` | `rp3a0-mini-hdmi.kicad_sch` | Micro-HDMI (`J2`), TMDS common-mode chokes (`FL1`–`FL4`), CEC/HPD level shifter (`U5`), Schottky diode (`D2`), USB-C (`J3`), and `USB_ID` jumper (`J4`) |
| `Wireless_SD` | `rp3a0-mini-wireless-sd.kicad_sch` | MicroSD card slot (`J1`), `SD_CLK` termination (`R14`, `R15`), and top-side Wi-Fi SDIO / Bluetooth UART test points (`TP10`–`TP22`, `TP28`) |
| `Misc_JTAG` | `rp3a0-mini-misc.kicad_sch` | JTAG test points (`TP23`–`TP27`), activity LED (`D1`, `R11`), calibration resistors (`R12`, `R13`, `R16`, `R17`, `R18`), and 86 NC balls |

## 2. Manufacturing Export (`make fab`)

Running `make fab` (or `make build-pcb` from the repository root) executes `export_manufacturing.py --all` to generate:
- `build/gerbers/` & `build/gerbers.zip` — 6 copper layers (`F.Cu`, `In1.Cu`..`In4.Cu`, `B.Cu`), solder mask, paste, silkscreen, `Edge.Cuts`, and Excellon PTH/NPTH drill files referenced to the lower-left board origin.
- `build/rp3a0-mini-bom.csv` & `.xlsx` — JLCPCB-formatted grouped Bill of Materials with 100% LCSC `C#####` part numbers for all 93 SMT-assembled components.
- `build/rp3a0-mini-cpl.csv` & `.xlsx` — JLCPCB-formatted Pick-and-Place (CPL) centroid table.
- `build/rp3a0-mini.d356` — IPC-D-356 bare-board electrical test netlist.
- `build/rp3a0-mini_Schematic.pdf` & `build/rp3a0-mini_PCB_Layers.pdf` — Complete schematic and layer plot PDFs.
- `build/ORDER_SPEC.md` & `build/rp3a0-mini_JLCPCB_Release.zip` — Turnkey release bundle.
