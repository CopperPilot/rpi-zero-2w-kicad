# Validation Notes

Detailed check results for the KiCad port. These are design-rule and static checks only. They tell you the files are internally consistent and match JLCPCB's capabilities. They do **not** prove the KiCad port boots; see the [README](../README.md#status) for build status.

The original design is by [jonny12375](https://github.com/jonny12375) ([rp3a0](https://github.com/jonny12375/rp3a0)).

## Summary

- KiCad ERC: 0 errors
- KiCad DRC: 0 errors, 100% routed
- PyTest hardware suite (`pcb/tests/`): 16/16 passing
- `copper-pilot validate`: 15 pass, 9 warn, 0 fail

## `copper-pilot validate` results

| Stage | Check IDs | Result | Summary |
|---|---|---|---|
| **S0 Intake** | `intake.tools`, `intake.project`, `intake.intent` | **PASS** | `kicad-cli 10.0.4`, 124 parts, 232 nets, 6 sheets, 6 copper layers |
| **S1 Architecture** | `arch.review` | **WARN (0 P0/P1)** | Power budget, reset supervisor, and `19.2 MHz` crystal load verified |
| **S2 Parts** | `parts.bom_fields`, `parts.lcsc`, `parts.symbols`, `parts.footprints` | **PASS / WARN (0 P0/P1)** | 100% LCSC/MPN/Datasheet coverage across all 93 assembled SMT parts |
| **S3 Schematic** | `sch.erc`, `sch.conventions`, `sch.circuits`, `sch.ratings` | **PASS / WARN (0 P0/P1)** | `0` ERC errors; all regulator feedback dividers and ratings verified |
| **S4 Netlist/Rules** | `pcb.parity`, `pcb.rules` | **PASS** | `0` schematic-to-PCB parity issues, `0` unconnected items, JLCPCB rules clean |
| **S5 Placement** | `pcb.placement` | **PASS** | 100% single-sided Top SMT placement with tight PMIC/BGA decoupling loops |
| **S6 Routing SI/PI** | `pcb.power_routing`, `pcb.signal_integrity` | **WARN (0 P0/P1)** | Continuous `In1.Cu`/`In4.Cu` GND planes, `0.50 mm` `5V` trunk, 107 GND vias |
| **S7 DFM/DFA** | `pcb.drc`, `dfm.fab`, `dfa.assembly`, `pcb.silkscreen` | **PASS / WARN (0 Fail)** | `0` DRC errors, `>=0.15 mm` solder mask webs, 3 global fiducials (`FID1`–`FID3`) |
| **S8 Release** | `release.outputs`, `release.repo`, `release.cpl` | **PASS** | 35 Gerber/drill files, portable `${KIPRJMOD}` tables, verified BOM/CPL exports |

## Changes from the Altium original, in detail

| Domain | Upstream Altium (`v1.1`) | This KiCad port |
|---|---|---|
| **EDA format & libraries** | Binary Altium `.PrjPcb`/`.SchDoc`/`.PcbDoc` | Native KiCad 10 (`.kicad_pro`/`.kicad_sch`/`.kicad_pcb`) with portable `${KIPRJMOD}` libraries |
| **19.2 MHz crystal (`Y1`) load** | `18 pF` caps (`C6`, `C9`) giving `11.5 pF` effective load vs. `18 pF` crystal spec | `C6`, `C9` changed to `27 pF` (`C0G`, LCSC `C1656`) for `16.0 pF` effective load |
| **`In4.Cu` return plane** | Bare signal layer (`<5%` copper), unreferenced `B.Cu` high-speed pairs | Stitched `GND` pour on `In4.Cu` + 27 extra `GND` stitching vias (`107` total) |
| **`5V` input trunk** | `0.15 mm` neck between `J3` VBUS and `U4`/`Q1` | Widened to `0.50 mm` + 3 parallel `5V` vias |
| **Fine-pitch solder mask webs** | `0.00 mm` mask web on `U3` (`0.40 mm` WLCSP) and `J2` (`0.40 mm` Micro-HDMI) | Pad mask margins giving `0.15 mm` (`U3`) and `0.202 mm` (`J2`) webs |
| **Fiducials & teardrops** | No fiducials | 3 global fiducials (`FID1`–`FID3`), teardrops on pads/vias |
| **BOM sourcing** | Discontinued/unstocked parts (`RT9081A`, `DMG1024UV`, `0475710001`, generic LED) | LCSC-stocked equivalents (`NCP133AMX125TCG` `C603545`, `DMN601VK-7` `C145714`, `47309-2651` `C504691`, `KT-0603G` `C12624`) |
| **CPL rotations** | Raw Altium exports | CPL exporter with JLCPCB rotation corrections for all 93 top-side parts |

![Altium vs. KiCad 6-Layer Copper Artwork Comparison](images/altium-vs-kicad-layers-comparison.png)

## Running the checks

```bash
make all        # PyTest suite + KiCad ERC + DRC + lint
make erc
make drc
make validate   # requires the copper-pilot CLI
```
