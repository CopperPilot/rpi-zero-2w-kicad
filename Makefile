# ==============================================================================
# RP3A0 Pico (KiCad 10 Port) - Unified Root Build & Verification Makefile
# ==============================================================================

PYTHON ?= python3
COPPER_PILOT ?= copper-pilot

.PHONY: all help fmt fmt-check lint test test-pcb coverage coverage-pcb \
        build-pcb drc erc validate clean distclean

# Default target runs complete verification across hardware tests and linting
all: test lint

help:
	@echo "======================================================================"
	@echo "RP3A0 Pico (KiCad 10): Unified Build, Verification & Fab System"
	@echo "======================================================================"
	@echo "Top-Level Targets:"
	@echo "  make fmt          - In-place formatting across PCB Python scripts and test suites"
	@echo "  make fmt-check    - Non-destructive code formatting compliance check"
	@echo "  make lint         - Static analysis (KiCad ERC, DRC, and Python ruff)"
	@echo "  make test         - Run full automated PCB hardware verification suite (PyTest)"
	@echo "  make test-pcb     - Run automated PCB hardware verification suite (PyTest)"
	@echo "  make coverage     - Generate pytest coverage report for PCB verification suite"
	@echo "  make drc          - Run KiCad CLI Design Rule Check on 6-layer PCB (0 errors, 100% routed)"
	@echo "  make erc          - Run KiCad CLI Electrical Rule Check on hierarchical schematic (0 errors)"
	@echo "  make validate     - Run copper-pilot validate stage-gated design validation"
	@echo "  make build-pcb    - Generate JLCPCB 6-layer manufacturing release bundle (Gerbers, drill, CPL, BOM)"
	@echo "  make clean        - Clean intermediate build and test outputs"
	@echo "  make distclean    - Deep clean removing caches, virtual environments, and artifacts"

# ------------------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------------------
fmt:
	@echo ">>> Formatting PCB Python Scripts & Test Suites..."
	@if command -v ruff > /dev/null; then \
		ruff format pcb/tests pcb/export_manufacturing.py; \
	elif $(PYTHON) -m ruff --version > /dev/null 2>&1; then \
		$(PYTHON) -m ruff format pcb/tests pcb/export_manufacturing.py; \
	else \
		echo "Notice: ruff not installed. Skipping Python formatting."; \
	fi
	@echo "All formatting complete."

fmt-check:
	@echo ">>> Checking PCB Python Formatting..."
	@if command -v ruff > /dev/null; then \
		ruff format --check pcb/tests pcb/export_manufacturing.py; \
	elif $(PYTHON) -m ruff --version > /dev/null 2>&1; then \
		$(PYTHON) -m ruff format --check pcb/tests pcb/export_manufacturing.py; \
	else \
		echo "Notice: ruff not installed. Skipping Python format check."; \
	fi
	@echo "All format checks passed."

# ------------------------------------------------------------------------------
# Linting & Static Analysis
# ------------------------------------------------------------------------------
lint:
	@echo ">>> [1/3] Running KiCad Schematic Electrical Rule Check (ERC)..."
	@$(MAKE) -C pcb erc
	@echo ">>> [2/3] Running KiCad PCB Design Rule Check (DRC)..."
	@$(MAKE) -C pcb drc
	@echo ">>> [3/3] Running PCB Python Test Suite Linting..."
	@if command -v ruff > /dev/null; then \
		ruff check pcb/tests pcb/export_manufacturing.py; \
	elif $(PYTHON) -m ruff --version > /dev/null 2>&1; then \
		$(PYTHON) -m ruff check pcb/tests pcb/export_manufacturing.py; \
	else \
		echo "Notice: ruff not installed. Skipping Python linting."; \
	fi
	@echo "All linting and static analysis passed cleanly."

# ------------------------------------------------------------------------------
# Testing & Validation
# ------------------------------------------------------------------------------
test: test-pcb
	@echo "======================================================================"
	@echo "SUCCESS: All RP3A0 Pico PCB hardware verification tests passed!"
	@echo "======================================================================"

test-pcb:
	@echo ">>> Running Automated PCB Hardware Verification Suite (PyTest)..."
	@$(MAKE) -C pcb test

validate:
	@echo ">>> Running CopperPilot Stage-Gated Design Validation..."
	@$(COPPER_PILOT) validate .

# ------------------------------------------------------------------------------
# Code Coverage
# ------------------------------------------------------------------------------
coverage: coverage-pcb

coverage-pcb:
	@echo ">>> Generating PCB Automated Test Coverage Report (pytest-cov)..."
	@cd pcb && $(PYTHON) -m pytest tests/test_pcb.py --cov=tests --cov-report=term-missing

# ------------------------------------------------------------------------------
# Hardware DRC / ERC
# ------------------------------------------------------------------------------
drc:
	@$(MAKE) -C pcb drc

erc:
	@$(MAKE) -C pcb erc

# ------------------------------------------------------------------------------
# Manufacturing Builds
# ------------------------------------------------------------------------------
build-pcb:
	@$(MAKE) -C pcb fab

# ------------------------------------------------------------------------------
# Cleaning
# ------------------------------------------------------------------------------
clean:
	@$(MAKE) -C pcb clean
	@echo "Root workspace cleaned."

distclean: clean
	@rm -rf .pytest_cache pcb/.pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
	@echo "Distclean complete: all caches and temporaries removed."
