PYTHON ?= python3
VENV ?= .venv
VENV_BIN ?= $(VENV)/bin

# Include standard Homebrew / JVM paths in execution PATH
export PATH := /opt/homebrew/opt/openjdk/bin:/usr/local/opt/openjdk/bin:$(PATH)

.PHONY: help install test ablate baselines failure-analysis competency check-docs results-index reproduce anon-bundle clean

help:
	@echo "RiceKG Expert System - Makefile commands"
	@echo "  make install       - Create .venv and install pinned dependencies from requirements-lock.txt"
	@echo "  make test          - Run test suite with pytest"
	@echo "  make ablate        - Run reasoner ablation experiments"
	@echo "  make baselines     - Run comparative ML and rule baselines"
	@echo "  make failure-analysis - Regenerate per-case field failure diagnosis"
	@echo "  make competency    - Regenerate the ontology competency-question report"
	@echo "  make check-docs    - Verify README/docs figures match results/"
	@echo "  make results-index - Regenerate docs/RESULTS_INDEX.md from results/*.json"
	@echo "  make reproduce     - Regenerate every result artifact end to end"
	@echo "  make anon-bundle   - Produce an anonymised review copy in anon_bundle/"
	@echo "  make clean         - Remove virtual environment and cached artifacts"

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

competency:
	$(VENV_BIN)/python3 analysis/competency_questions.py

check-docs:
	$(VENV_BIN)/python3 analysis/check_readme_consistency.py

degradation:
	$(VENV_BIN)/python3 analysis/degradation_curve.py

results-index:
	$(VENV_BIN)/python3 analysis/build_results_index.py

reproduce: ablate baselines failure-analysis competency degradation results-index check-docs
	@echo "All result artifacts regenerated and documentation figures verified."

# ---------------------------------------------------------------------------
# Anonymous review bundle
# ---------------------------------------------------------------------------
# Produces anon_bundle/ricekg-review/ — a copy of the repository with all
# author-identifying strings replaced. Does NOT modify the working tree.
# Upload the bundle to anonymous.4open.science or Zenodo for blind review.
# See docs/ANONYMISATION.md for the full checklist.

ANON_DIR := anon_bundle/ricekg-review

anon-bundle:
	@$(PYTHON) analysis/build_anon_bundle.py --out $(ANON_DIR)

clean:
	rm -rf $(VENV) build/ dist/ *.egg-info .pytest_cache/ __pycache__ */__pycache__

