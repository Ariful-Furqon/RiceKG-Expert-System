PYTHON ?= python3
VENV ?= .venv
VENV_BIN ?= $(VENV)/bin

# Include standard Homebrew / JVM paths in execution PATH
export PATH := /opt/homebrew/opt/openjdk/bin:/usr/local/opt/openjdk/bin:$(PATH)

.PHONY: help install test ablate baselines clean

help:
	@echo "RiceKG Expert System - Makefile commands"
	@echo "  make install    - Create .venv and install pinned dependencies from requirements-lock.txt"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make ablate     - Run reasoner ablation experiments"
	@echo "  make baselines  - Run comparative ML and rule baselines"
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

clean:
	rm -rf $(VENV) build/ dist/ *.egg-info .pytest_cache/ __pycache__ */__pycache__
