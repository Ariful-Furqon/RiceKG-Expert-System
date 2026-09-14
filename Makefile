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

results-index:
	$(VENV_BIN)/python3 analysis/build_results_index.py

reproduce: ablate baselines failure-analysis competency results-index check-docs
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
	@echo "Building anonymised review bundle in $(ANON_DIR)/ ..."
	@rm -rf anon_bundle
	@mkdir -p $(ANON_DIR)
	@rsync -a --exclude='.git' --exclude='anon_bundle' \
	       --exclude='__pycache__' --exclude='*.pyc' \
	       --exclude='.venv' --exclude='*.egg-info' \
	       --filter=':- .gitignore' \
	       . $(ANON_DIR)/
	# Substitute identifying strings in text files
	@find $(ANON_DIR) -type f \( -name "*.md" -o -name "*.py" -o -name "*.cff" \
	       -o -name "*.yml" -o -name "*.yaml" -o -name "*.txt" -o -name "*.csv" \
	       -o -name "*.json" -o -name "*.rst" -o -name "*.html" \) | \
	  xargs sed -i \
	    -e 's/Furqon, Ariful/ANONYMISED/g' \
	    -e 's/Muhammad Ariful/ANONYMISED/g' \
	    -e 's/Ariful Furqon/ANONYMISED/g' \
	    -e 's/ariful\.furqon@unej\.ac\.id/ricekg-review@anonymous.invalid/g' \
	    -e 's/Ariful-Furqon\/RiceKG-Expert-System/ANONYMISED\/ANONYMISED/g' \
	    -e 's/github\.com\/Ariful-Furqon/github.com\/ANONYMISED/g' \
	    -e 's/Universitas Jember (UNEJ)/[Institution name withheld for review]/g' \
	    -e 's/Universitas Jember/[Institution name withheld for review]/g' \
	    -e 's/UNEJ/[Institution withheld]/g' \
	    -e 's/Lembaga Penelitian dan Pengabdian kepada Masyarakat (LP2M)/[Ethics body withheld]/g' \
	    -e 's/family-names: Furqon/family-names: ANONYMISED/g' \
	    -e 's/given-names: Ariful/given-names: ANONYMISED/g' \
	    -e 's/given-names: Muhammad Ariful/given-names: ANONYMISED/g' \
	    -e 's|affiliation: "Department of Informatics.*"|affiliation: "ANONYMISED"|g'
	# Squash git history to a single anonymous commit
	@cd $(ANON_DIR) && git init -q && git add -A && \
	  GIT_AUTHOR_NAME="Anonymous" \
	  GIT_AUTHOR_EMAIL="review@anonymous.invalid" \
	  GIT_COMMITTER_NAME="Anonymous" \
	  GIT_COMMITTER_EMAIL="review@anonymous.invalid" \
	  git commit -q -m "Initial submission"
	@echo ""
	@echo "Bundle created: $(ANON_DIR)/"
	@echo "Upload to anonymous.4open.science or a restricted Zenodo deposit."
	@echo "See docs/ANONYMISATION.md for the release procedure after acceptance."

clean:
	rm -rf $(VENV) build/ dist/ *.egg-info .pytest_cache/ __pycache__ */__pycache__

