"""Pytest fixtures and S-expression parsers for RP3A0 Pico KiCad 10 automated tests."""

import glob
import json
import math
import os
import re
import subprocess

try:
    import pytest
except ImportError:
    class _MockPytest:
        @staticmethod
        def fixture(*args, **kwargs):
            return lambda fn: fn

        @staticmethod
        def fail(msg):
            raise AssertionError(msg)

    pytest = _MockPytest()

PCB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PCB_FILE = os.path.join(PCB_DIR, "rp3a0-mini.kicad_pcb")
SCH_FILE = os.path.join(PCB_DIR, "rp3a0-mini.kicad_sch")
PRO_FILE = os.path.join(PCB_DIR, "rp3a0-mini.kicad_pro")


class KiCadPCB:
    """Parser for KiCad 10 PCB S-expression format."""

    def __init__(self, pcb_path: str):
        self.path = pcb_path
        with open(pcb_path, "r", encoding="utf-8") as f:
            self.content = f.read()

        self._parse_nets()
        self._parse_segments()
        self._parse_vias()
        self._parse_edge_cuts()
        self._parse_footprints()

    def _parse_nets(self):
        self.nets = set()
        for m in re.finditer(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', self.content):
            name = m.group(1).strip()
            if name:
                self.nets.add(name)

    def _parse_segments(self):
        self.segments = []
        seg_pattern = re.finditer(
            r"\(segment\s+"
            r"\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+"
            r"\(end\s+([-\d\.]+)\s+([-\d\.]+)\)\s+"
            r"\(width\s+([-\d\.]+)\)\s+"
            r'\(layer\s+"([^"]+)"\)\s+'
            r'\(net\s+(?:\d+\s+)?"?([^"\)]+)"?\)',
            self.content,
        )
        for m in seg_pattern:
            x1, y1, x2, y2, w, layer, net_name = (
                float(m.group(1)),
                float(m.group(2)),
                float(m.group(3)),
                float(m.group(4)),
                float(m.group(5)),
                m.group(6),
                m.group(7).strip(),
            )
            length = math.hypot(x2 - x1, y2 - y1)
            self.segments.append(
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "width": w,
                    "layer": layer,
                    "net_name": net_name,
                    "length": length,
                }
            )

    def _parse_vias(self):
        self.vias = []
        via_pattern = re.finditer(
            r"\(via\s+"
            r"(?:\(blind\s+yes\)\s+)?"
            r"\(at\s+([-\d\.]+)\s+([-\d\.]+)\)\s+"
            r"\(size\s+([-\d\.]+)\)\s+"
            r"\(drill\s+([-\d\.]+)\)\s+"
            r"(?:[^\)]*?\)\s+)*?"
            r'\(net\s+(?:\d+\s+)?"?([^"\)]+)"?\)',
            self.content,
        )
        for m in via_pattern:
            x, y, s, d, net_name = (
                float(m.group(1)),
                float(m.group(2)),
                float(m.group(3)),
                float(m.group(4)),
                m.group(5).strip(),
            )
            self.vias.append(
                {
                    "x": x,
                    "y": y,
                    "size": s,
                    "drill": d,
                    "annular_ring": (s - d) / 2.0,
                    "net_name": net_name,
                }
            )

    def _parse_edge_cuts(self):
        self.edge_cuts = []
        line_pat = re.finditer(
            r"\(gr_line\s+"
            r"\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+"
            r"\(end\s+([-\d\.]+)\s+([-\d\.]+)\)"
            r"[\s\S]*?"
            r'\(layer\s+"Edge\.Cuts"\)',
            self.content,
        )
        for m in line_pat:
            self.edge_cuts.append(
                {
                    "type": "line",
                    "x1": float(m.group(1)),
                    "y1": float(m.group(2)),
                    "x2": float(m.group(3)),
                    "y2": float(m.group(4)),
                }
            )

    def _parse_footprints(self):
        self.footprints = {}
        fp_matches = list(re.finditer(r'\n\t\(footprint\s+"([^"]+)"', self.content))
        for i, m in enumerate(fp_matches):
            start_idx = m.start() + 1
            end_idx = (
                fp_matches[i + 1].start()
                if i + 1 < len(fp_matches)
                else len(self.content)
            )
            block = self.content[start_idx:end_idx]

            ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
            if not ref_match:
                continue
            ref = ref_match.group(1)

            val_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
            val = val_match.group(1) if val_match else ""

            at_match = re.search(
                r"\n\t\t\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)", block
            )
            pos_x = float(at_match.group(1)) if at_match else 0.0
            pos_y = float(at_match.group(2)) if at_match else 0.0
            rot = float(at_match.group(3)) if at_match and at_match.group(3) else 0.0

            models = re.findall(r'\(model\s+"([^"]+)"', block)

            pads = []
            for pad_m in re.finditer(
                r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s+'
                r"\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)\s+"
                r"\(size\s+([-\d\.]+)\s+([-\d\.]+)\)",
                block,
            ):
                pads.append(
                    {
                        "number": pad_m.group(1),
                        "type": pad_m.group(2),
                        "shape": pad_m.group(3),
                        "rel_x": float(pad_m.group(4)),
                        "rel_y": float(pad_m.group(5)),
                        "width": float(pad_m.group(7)),
                        "height": float(pad_m.group(8)),
                    }
                )

            self.footprints[ref] = {
                "footprint": m.group(1),
                "reference": ref,
                "value": val,
                "x": pos_x,
                "y": pos_y,
                "rotation": rot,
                "models": models,
                "pads": pads,
            }


class KiCadSCH:
    """Parser for hierarchical KiCad 10 Schematic sheets."""

    def __init__(self, sch_dir: str):
        self.sch_files = sorted(glob.glob(os.path.join(sch_dir, "*.kicad_sch")))
        self.symbols = {}
        self.labels = set()
        for path in self.sch_files:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for block in content.split("\n\t(symbol\n")[1:]:
                lib_m = re.search(r'\(lib_id\s+"([^"]+)"\)', block)
                ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
                val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
                fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', block)
                mpn_m = re.search(r'\(property\s+"MPN"\s+"([^"]*)"', block)
                lcsc_m = re.search(r'\(property\s+"LCSC"\s+"([^"]*)"', block)
                dnp_m = re.search(r"\(dnp\s+(yes|no)\)", block)
                if ref_m and not ref_m.group(1).startswith("#"):
                    ref = ref_m.group(1)
                    self.symbols[ref] = {
                        "lib_id": lib_m.group(1) if lib_m else "",
                        "reference": ref,
                        "value": val_m.group(1) if val_m else "",
                        "footprint": fp_m.group(1) if fp_m else "",
                        "mpn": mpn_m.group(1) if mpn_m else "",
                        "lcsc": lcsc_m.group(1) if lcsc_m else "",
                        "dnp": dnp_m.group(1) == "yes" if dnp_m else False,
                    }
            for m in re.finditer(r'\(label\s+"([^"]+)"', content):
                self.labels.add(m.group(1))


@pytest.fixture(scope="session")
def pcb_data():
    return KiCadPCB(PCB_FILE)


@pytest.fixture(scope="session")
def sch_data():
    return KiCadSCH(PCB_DIR)


@pytest.fixture(scope="session")
def drc_results():
    """Run kicad-cli pcb drc --severity-all --schematic-parity and return parsed JSON."""
    report_file = os.path.join(PCB_DIR, ".drc_test_report.json")
    cmd = [
        "kicad-cli",
        "pcb",
        "drc",
        "--format",
        "json",
        "--severity-all",
        "--schematic-parity",
        "-o",
        report_file,
        PCB_FILE,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not os.path.exists(report_file):
        pytest.fail(f"kicad-cli pcb drc failed: {res.stderr}\n{res.stdout}")

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if os.path.exists(report_file):
        os.remove(report_file)

    return data


@pytest.fixture(scope="session")
def erc_results():
    """Run kicad-cli sch erc --severity-all and return parsed JSON."""
    report_file = os.path.join(PCB_DIR, ".erc_test_report.json")
    cmd = [
        "kicad-cli",
        "sch",
        "erc",
        "--format",
        "json",
        "--severity-all",
        "-o",
        report_file,
        SCH_FILE,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not os.path.exists(report_file):
        pytest.fail(f"kicad-cli sch erc failed: {res.stderr}\n{res.stdout}")

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if os.path.exists(report_file):
        os.remove(report_file)

    return data
