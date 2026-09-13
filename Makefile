PYTHON ?= python3
VENV ?= .venv
VENV_BIN ?= $(VENV)/bin

# Include standard Homebrew / JVM paths in execution PATH
export PATH := /opt/homebrew/opt/openjdk/bin:/usr/local/opt/openjdk/bin:$(PATH)

.PHONY: help install test ablate baselines failure-analysis check-docs reproduce clean

help:
	@echo "RiceKG Expert System - Makefile commands"
	@echo "  make install    - Create .venv and install pinned dependencies from requirements-lock.txt"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make ablate     - Run reasoner ablation experiments"
	@echo "  make baselines  - Run comparative ML and rule baselines"
	@echo "  make failure-analysis - Regenerate per-case field failure diagnosis"
	@echo "  make check-docs - Verify README/docs figures match results/"
	@echo "  make reproduce  - Regenerate every result artifact end to end"
	@echo "  make clean      - Remove virtual environment and cached artifacts"

install:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements-lock.txt

test:
	$(VENV_BIN)/pytest -v tests/

ablate:
	$(VENV_BIN)/python3 ablation.py

baselines:
	$(VENV_BIN)/python3 baselines/run_baselines.py

failure-analysis:
	$(VENV_BIN)/python3 analysis/field_failure_analysis.py --split all

check-docs:
	$(VENV_BIN)/python3 analysis/check_readme_consistency.py

reproduce: ablate baselines failure-analysis check-docs
	@echo "All result artifacts regenerated and documentation figures verified."

clean:
	rm -rf $(VENV) build/ dist/ *.egg-info .pytest_cache/ __pycache__ */__pycache__
