# ==============================================================================
# RP3A0 Pico PCB - Hardware Verification & JLCPCB 6-Layer Fabrication Makefile
# ==============================================================================

PROJECT_NAME := rp3a0-mini
PCB_FILE     := $(PROJECT_NAME).kicad_pcb
SCH_FILE     := $(PROJECT_NAME).kicad_sch
PRO_FILE     := $(PROJECT_NAME).kicad_pro
BUILD_DIR    := build
GERBER_DIR   := $(BUILD_DIR)/gerbers
RELEASE_ZIP  := $(BUILD_DIR)/$(PROJECT_NAME)_JLCPCB_Release.zip
GERBERS_ZIP  := $(BUILD_DIR)/gerbers.zip

PYTHON       := $(shell if [ -x "$$HOME/.local/share/kikit-venv/bin/python3" ]; then echo "$$HOME/.local/share/kikit-venv/bin/python3"; else echo "python3"; fi)
PYTEST       := $(shell if python3 -m pytest --version >/dev/null 2>&1; then echo "python3 -m pytest"; elif command -v uv >/dev/null 2>&1; then echo "uv run --with pytest pytest"; else echo "pytest"; fi)
KICAD_CLI    := kicad-cli
KIKIT        := $(shell which kikit 2>/dev/null || echo "$$HOME/.local/bin/kikit")

.PHONY: all help erc drc test netlist gerbers drill zip-gerbers pos cpl bom d356 pdf spec fab kikit clean

all: test drc erc

help:
	@echo "RP3A0 Pico PCB Targets:"
	@echo "  make test        - Run automated hardware verification suite (PyTest)"
	@echo "  make drc         - Run KiCad CLI Design Rule Check (asserts 0 errors, 0 unconnected, 0 parity)"
	@echo "  make erc         - Run KiCad CLI Electrical Rule Check (asserts 0 errors)"
	@echo "  make kikit       - Run KiKit JLCPCB export (kikit fab jlcpcb)"
	@echo "  make gerbers     - Export RS-274X Gerbers for JLCPCB 6-layer production"
	@echo "  make drill       - Export Excellon NC drill files (metric, plated + non-plated)"
	@echo "  make zip-gerbers - Package gerbers and drills into gerbers.zip"
	@echo "  make pos         - Export SMT pick-and-place component centroid file (CPL/POS)"
	@echo "  make bom         - Export structured Bill of Materials with 100% LCSC/MPN mapping"
	@echo "  make d356        - Export IPC-D-356 electrical test netlist"
	@echo "  make pdf         - Export schematic and multipage PCB layer PDFs"
	@echo "  make spec        - Generate JLCPCB 6-layer manufacturing ORDER_SPEC.md"
	@echo "  make fab         - Generate all manufacturing outputs and package into release zip"
	@echo "  make clean       - Remove build outputs, temporary reports, and test caches"

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)
	@mkdir -p $(GERBER_DIR)

erc: $(BUILD_DIR)
	@echo "==> Running KiCad Electrical Rule Check (ERC)..."
	@$(KICAD_CLI) sch erc --format json -o $(BUILD_DIR)/erc_report.json $(SCH_FILE) > /dev/null
	@$(PYTHON) -c "import json, sys; \
		data = json.load(open('$(BUILD_DIR)/erc_report.json')); \
		errors = [v for s in data.get('sheets', []) for v in s.get('violations', []) if v.get('severity') == 'error']; \
		print(f'ERC Results: {len(errors)} errors'); \
		sys.exit(1 if errors else 0)"
	@rm -f $(BUILD_DIR)/erc_report.json
	@echo "ERC Clean: 0 errors."

drc: $(BUILD_DIR)
	@echo "==> Running KiCad Design Rule Check (DRC)..."
	@$(KICAD_CLI) pcb drc --format json --refill-zones --schematic-parity -o $(BUILD_DIR)/drc_report.json $(PCB_FILE) > /dev/null
	@$(PYTHON) -c "import json, sys; \
		data = json.load(open('$(BUILD_DIR)/drc_report.json')); \
		errors = [v for v in data.get('violations', []) if v.get('severity') == 'error']; \
		unconnected = data.get('unconnected_items', []); \
		parity = data.get('schematic_parity', []) or data.get('schematic_parity_issues', []); \
		print(f'DRC Results: {len(errors)} errors, {len(unconnected)} unconnected items, {len(parity)} parity issues'); \
		sys.exit(1 if (errors or unconnected or parity) else 0)"
	@rm -f $(BUILD_DIR)/drc_report.json
	@echo "DRC Clean: 0 errors, 0 unconnected items (100% routed), 0 parity issues."

test:
	@echo "==> Running automated PCB hardware test suite with PyTest..."
	@$(PYTEST) tests/test_pcb.py -v

netlist: $(BUILD_DIR)
	@echo "==> Exporting schematic netlist..."
	@$(KICAD_CLI) sch export netlist --format kicadxml -o $(BUILD_DIR)/$(PROJECT_NAME).xml $(SCH_FILE)
	@echo "Saved netlist to $(BUILD_DIR)/$(PROJECT_NAME).xml"

gerbers: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --gerbers

drill: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --drill

zip-gerbers: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --zip-gerbers

pos: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --cpl

cpl: pos

bom: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --bom

d356: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --d356

pdf: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --pdf

spec: $(BUILD_DIR)
	@$(PYTHON) export_manufacturing.py --spec

kikit: $(BUILD_DIR)
	@echo "==> Running KiKit JLCPCB export (kikit fab jlcpcb)..."
	@mkdir -p $(BUILD_DIR)/kikit
	@$(KIKIT) fab jlcpcb --assembly --schematic $(SCH_FILE) --missingError $(PCB_FILE) $(BUILD_DIR)/kikit
	@echo "KiKit export complete in $(BUILD_DIR)/kikit/"

fab: $(BUILD_DIR)
	@echo "==> Packaging complete manufacturing release bundle for JLCPCB..."
	@$(PYTHON) export_manufacturing.py --all

clean:
	@rm -rf $(BUILD_DIR) .pytest_cache tests/__pycache__ *.json
	@echo "PCB build directory cleaned."
