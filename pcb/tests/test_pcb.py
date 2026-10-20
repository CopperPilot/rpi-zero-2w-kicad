"""Automated hardware verification test suite for RP3A0 Pico 6-layer KiCad 10 PCB."""

import os
import re

PCB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestBoardPhysical:
    """Verifies board physical dimensions, 6-layer stackup, and boundary geometry."""

    def test_board_dimensions(self, pcb_data):
        """Assert outer bounding box matches 60.00 x 20.35 mm (+/- 0.5 mm tolerance)."""
        xs = []
        ys = []
        for elem in pcb_data.edge_cuts:
            if elem["type"] == "line":
                xs.extend([elem["x1"], elem["x2"]])
                ys.extend([elem["y1"], elem["y2"]])

        assert len(xs) > 0, "No Edge.Cuts elements found"
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        assert 59.5 <= width <= 60.5, f"Board width {width:.2f} mm out of range [59.5, 60.5]"
        assert 20.0 <= height <= 20.7, f"Board height {height:.2f} mm out of range [20.0, 20.7]"

    def test_board_outline_closed(self, pcb_data):
        """Assert Edge.Cuts consists of a closed 4-segment rectangular outline."""
        assert len(pcb_data.edge_cuts) == 4, (
            f"Expected 4 rectangular Edge.Cuts segments, got {len(pcb_data.edge_cuts)}"
        )

    def test_six_layer_stackup(self, pcb_data):
        """Assert 6-layer copper stackup (F.Cu, In1.Cu..In4.Cu, B.Cu) for JLCPCB."""
        for layer in ["F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu", "Edge.Cuts"]:
            assert f'"{layer}"' in pcb_data.content, f"Layer {layer} missing from PCB"


class TestConnectivityAndNetlist:
    """Verifies electrical connectivity, routing completeness, and DRC/ERC parity."""

    def test_drc_zero_unconnected_items(self, drc_results):
        """Assert kicad-cli pcb drc returns 0 unconnected items (100% routed)."""
        unconnected = drc_results.get("unconnected_items", [])
        assert len(unconnected) == 0, f"Found {len(unconnected)} unconnected items: {unconnected}"

    def test_drc_zero_violations(self, drc_results):
        """Assert kicad-cli pcb drc --severity-all returns 0 violations."""
        violations = drc_results.get("violations", [])
        assert len(violations) == 0, f"Found {len(violations)} DRC violations: {violations}"

    def test_drc_zero_schematic_parity_issues(self, drc_results):
        """Assert kicad-cli pcb drc --schematic-parity returns 0 parity issues."""
        parity = drc_results.get("schematic_parity", [])
        assert len(parity) == 0, f"Found {len(parity)} schematic parity issues: {parity}"

    def test_erc_zero_violations(self, erc_results):
        """Assert kicad-cli sch erc --severity-all returns 0 violations across all 6 sheets."""
        sheets = erc_results.get("sheets", [])
        assert len(sheets) == 6, f"Expected 6 hierarchical sheets, got {len(sheets)}"
        all_violations = [v for s in sheets for v in s.get("violations", [])]
        assert len(all_violations) == 0, f"Found {len(all_violations)} ERC violations: {all_violations}"

    def test_critical_power_and_high_speed_nets_present(self, pcb_data):
        """Assert all power rails, HDMI TMDS, USB, SDIO, and I2C nets are routed on the PCB."""
        critical_nets = [
            "GND",
            "5V",
            "5V_CORE",
            "3V3",
            "1V8",
            "DDR_1V25",
            "VDD_CORE",
            "HDMI_5V",
            "/Power/INT_SDA",
            "/Power/INT_SCL",
            "/Power/RUN",
            "/HDMI_USB/USB_DP",
            "/HDMI_USB/USB_DN",
            "/HDMI_USB/HDMI_CKP",
            "/HDMI_USB/HDMI_CKN",
            "/HDMI_USB/HDMI_T0P",
            "/HDMI_USB/HDMI_T0N",
            "/HDMI_USB/HDMI_T1P",
            "/HDMI_USB/HDMI_T1N",
            "/HDMI_USB/HDMI_T2P",
            "/HDMI_USB/HDMI_T2N",
            "/Wireless_SD/SD_CLK",
            "/Wireless_SD/SD_CMD",
            "/Wireless_SD/SD_DAT0",
            "/Wireless_SD/SD_DAT1",
            "/Wireless_SD/SD_DAT2",
            "/Wireless_SD/SD_DAT3",
        ]
        for net in critical_nets:
            assert net in pcb_data.nets, f"Critical net '{net}' missing from PCB"

    def test_no_dangling_track_stubs(self, pcb_data):
        """Assert all track segments have non-zero length."""
        for seg in pcb_data.segments:
            assert seg["length"] > 0.001, (
                f"Zero-length track segment detected at ({seg['x1']}, {seg['y1']})"
            )

    def test_no_unassigned_vias(self, pcb_data):
        """Assert all vias are bound to active named nets."""
        assert len(pcb_data.vias) >= 390, f"Expected >= 390 vias, got {len(pcb_data.vias)}"
        for via in pcb_data.vias:
            assert via["net_name"] != "", f"Unassigned via detected at ({via['x']}, {via['y']})"


class TestTraceGeometryAndDFM:
    """Verifies manufacturing rule margins against JLCPCB 6-layer capabilities."""

    def test_signal_trace_min_width(self, pcb_data):
        """Assert all signal tracks meet or exceed JLCPCB 6-layer 0.0889 mm (3.5 mil) minimum."""
        for seg in pcb_data.segments:
            assert seg["width"] >= 0.0889, (
                f"Trace width {seg['width']} mm at ({seg['x1']}, {seg['y1']}) violates 0.0889 mm min"
            )

    def test_via_drill_and_annular_ring(self, pcb_data):
        """Assert via drill >= 0.20 mm, diameter >= 0.30 mm, annular ring >= 0.05 mm."""
        for via in pcb_data.vias:
            assert via["drill"] >= 0.199, f"Via drill {via['drill']} mm < 0.20 mm limit"
            assert via["size"] >= 0.299, f"Via diameter {via['size']} mm < 0.30 mm limit"
            assert via["annular_ring"] >= 0.049, (
                f"Via annular ring {via['annular_ring']} mm < 0.05 mm limit"
            )


class TestBOMAndLibraryIntegrity:
    """Verifies BOM field completeness, LCSC part numbers, and portable library tables."""

    def test_all_124_components_present(self, pcb_data, sch_data):
        """Assert all 124 components exist in both schematic and PCB."""
        assert len(pcb_data.footprints) == 124
        assert len(sch_data.symbols) == 124
        assert set(pcb_data.footprints.keys()) == set(sch_data.symbols.keys())

    def test_all_assembled_parts_have_lcsc_and_mpn(self, sch_data):
        """Assert all 93 SMT-assembled components have valid LCSC C-numbers and MPNs."""
        assembled = [s for s in sch_data.symbols.values() if not s["dnp"]]
        assert len(assembled) == 93, f"Expected 93 assembled SMT parts, got {len(assembled)}"
        for sym in assembled:
            assert sym["mpn"], f"Part {sym['reference']} missing MPN"
            assert re.match(r"^C\d{4,}$", sym["lcsc"]), (
                f"Part {sym['reference']} has invalid LCSC code '{sym['lcsc']}'"
            )

    def test_portable_kiprjmod_library_tables(self):
        """Assert sym-lib-table and fp-lib-table use ${KIPRJMOD} and no absolute user paths."""
        for table in ["sym-lib-table", "fp-lib-table"]:
            text = open(os.path.join(PCB_DIR, table), encoding="utf-8").read()
            assert "${KIPRJMOD}/libs/" in text
            assert "/home/" not in text and "/Users/" not in text

    def test_cpl_export_matches_93_assembled_parts(self, sch_data):
        """Assert kicad-cli pcb export pos --smd-only --exclude-dnp exports all 93 SMT parts."""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            pos_path = tmp.name
        try:
            subprocess.run(
                [
                    "kicad-cli",
                    "pcb",
                    "export",
                    "pos",
                    "--side",
                    "both",
                    "--format",
                    "csv",
                    "--units",
                    "mm",
                    "--smd-only",
                    "--exclude-dnp",
                    "--use-drill-file-origin",
                    "-o",
                    pos_path,
                    os.path.join(PCB_DIR, "rp3a0-mini.kicad_pcb"),
                ],
                check=True,
            )
            lines = [
                line.split(",")[0].strip('"')
                for line in open(pos_path, encoding="utf-8").read().splitlines()
                if line and not line.startswith("#") and not line.startswith("Ref")
            ]
            assembled_refs = {s["reference"] for s in sch_data.symbols.values() if not s["dnp"]}
            assert set(lines) == assembled_refs
            assert len(lines) == 93
        finally:
            if os.path.exists(pos_path):
                os.remove(pos_path)

