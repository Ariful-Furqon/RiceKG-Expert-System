# RiceKG: Knowledge Graph and SWRL-Based Expert System for Rice Pest and Disease Diagnosis

[![CI Evaluation](https://github.com/Ariful-Furqon/RiceKG-Expert-System/actions/workflows/ci.yml/badge.svg)](https://github.com/Ariful-Furqon/RiceKG-Expert-System/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Pellet Reasoner](https://img.shields.io/badge/Reasoner-Pellet%20DL-orange)](https://github.com/stardog-union/pellet)
[![OWL 2](https://img.shields.io/badge/Ontology-OWL%202-purple)](https://www.w3.org/TR/owl2-overview/)

An ontology-driven expert system leveraging **Web Ontology Language (OWL 2)** and **Semantic Web Rule Language (SWRL)** with the **Pellet DL reasoner** for diagnosing rice pests and diseases based on observed field symptoms.

---

## Overview

This repository provides an automated semantic reasoning system for diagnosing **10 major rice biotic threats** (5 destructive insect pests and 5 prevalent phytopathogenic diseases). The system integrates:

- **Ontology (OWL 2)**: Formal TBox/ABox conceptualization of rice entities, symptoms, pests, diseases, and treatment management.
- **Multi-Tier SWRL Rules**: 20 deterministic forward-chaining rules (Tier 1 canonical + Tier 2 relaxed partial-symptom rules) linking combinations of phenotypic symptoms to specific diagnoses.
- **Pellet DL Reasoner (`owlready2`)**: Java-based Tableau description logic reasoner executing property assertion and multi-label diagnosis.
- **Flask Web Interface**: Interactive web interface for symptom selection and diagnostic reasoning.
- **Multi-Label Evaluation Suite**: Automated script computing per-class Confusion Matrix metrics (TP, FP, FN, TN, Precision, Recall, F1, Accuracy).

---

## Diagnosed Pests & Diseases

| Type | Name | Scientific / Common Identifier |
|---|---|---|
| **Pest** | `Grasshopper` | *Oxya chinensis* |
| **Pest** | `Rice_Root_Nematode` | *Hirschmanniella oryzae* |
| **Pest** | `Rice_Stem_Borer` | *Scirpophaga incertulas* |
| **Pest** | `Rice_Bug` | *Leptocorisa oratorius* |
| **Pest** | `Brown_Planthopper` | *Nilaparvata lugens* |
| **Disease** | `Bacterial_Leaf_Blight` | *Xanthomonas oryzae* pv. *oryzae* |
| **Disease** | `False_Smut` | *Ustilaginoidea virens* |
| **Disease** | `Rice_Blast` | *Magnaporthe oryzae* / *Pyricularia oryzae* |
| **Disease** | `Rice_Grassy_Stunt` | Rice grassy stunt virus (RGSV) |
| **Disease** | `Rice_Tungro_Virus` | Rice tungro bacilliform & spherical virus |

## Reproducibility & Installation

### Prerequisites
- **Python >= 3.10**
- **Java Development Kit / Runtime (JDK/JRE 11+)** — Required for the Pellet DL Reasoner (`sync_reasoner_pellet` via `owlready2`).
  - **macOS (Homebrew)**: `brew install openjdk` (auto-detected by RiceKG)
  - **Ubuntu/Debian**: `sudo apt-get install -y default-jre`
  - **Windows**: Install Eclipse Temurin or Oracle JDK 11+ and add `bin` to `PATH`.

### Environment Setup

The repository provides a declarative build specification ([`pyproject.toml`](pyproject.toml)), exact dependency lockfile ([`requirements-lock.txt`](requirements-lock.txt)), and automated [`Makefile`](Makefile):

```bash
# 1. Create virtual environment (.venv) and install exact pinned dependencies
make install

# 2. Run comprehensive unit and regression test suite
make test

# 3. Re-run reasoner architecture ablation experiments
make ablate

# 4. Re-run comparative ML and rule baselines with statistical significance tests
make baselines
```

---

## Usage

### Run Automated Test Suite
```bash
python -m pytest test.py -v
```

### Run Benchmark Evaluation (Confusion Matrix)
```bash
python evaluate.py
```

### Run Architectural Ablation Study
```bash
python ablation.py
```

### Launch Web Application
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000/`

---

## Evaluation Results

To prevent evaluation circularity, performance is reported separately on two distinct benchmarks with explicit provenance tracking. **Synthetic and independent cases are never pooled.**

### Benchmark 1: Synthetic Rule-Derived Benchmark (`data/benchmark_synthetic.csv`)
- **Provenance**: `rule_derived` (authored to verify deductive SWRL rule firing consistency)
- **Sample Size ($n$)**: 80 test cases across 6 diagnostic tiers (T1–T6)

| Metric | Score |
|---|---|
| **Multi-Label Accuracy ((TP+TN)/Total)** | **99.25%** |
| **Exact-Match Case Accuracy** | **92.50%** |
| **Micro-Average Precision** | **97.4%** |
| **Micro-Average Recall** | **95.0%** |
| **Micro-Average F1-Score** | **96.2%** |

*Methodological Note: As documented in `docs/LIMITATIONS.md` and `data/README.md`, near-ceiling performance on this dataset reflects deductive consistency under closed-world assumptions, because cases are derived from the rule antecedents.*

### Benchmark 2: Independent Peer-Reviewed Literature Benchmark (`data/benchmark_field.csv`)
- **Provenance**: `literature_case` / `lab_confirmed` (strictly drawn from primary peer-reviewed disease notes in APS *Plant Disease* "Disease Notes"; IRRI Rice Doctor explicitly excluded to avoid circularity)
- **Sample Size ($n$)**: 32 independently verified cases (5 in-scope targets, 27 out-of-scope emerging pathogens and negative controls)
- **Protocol**: Two-stage extraction with immutable `raw_symptom_text`, 100% verified DOIs against `api.crossref.org`, authentic collection dates/locations, `annotator_id` set to `"unassigned"` pending formal agronomist adjudication, and automated CI verification via `analysis/verify_citations.py`.

| Metric | Score |
|---|---|
| **Multi-Label Accuracy ((TP+TN)/Total)** | **98.44%** |
| **Exact-Match Case Accuracy** | **84.38%** (27/32 cases) |
| **Specificity / Negative Control Rejection** | **100.0%** (27/27 out-of-scope non-target pathogens rejected) |
| **Citation Verification Gate (CI)** | **100.0%** (32/32 Crossref HTTP 200 & title match) |

*Scientific Disclosure & Scope Limitations:*
- **Controlled Vocabulary Coverage Bottleneck**: Real-world literature cases contained clinical traits outside the 45-term vocabulary. The ontology lacks `Leaf_Sheath` (cannot express Sheath Rot/Sheath Blight), abiotic signatures (`Leaf_Rolling`, `Bronzing`, `Marginal_Scorch`), and grain lesions (`Glume_Discoloration`, `Powdery_Sooty_Spore_Masses`).
- **Deductive Horn-Clause Specificity**: Out-of-scope emerging pathogens generated 0 false positives because closed-world SWRL rules require strict conjunctions. In-scope cases under preliminary uncurated symptom mappings yielded `No diagnosis inferred`, perfectly illustrating the need for complete Stage B multi-rater agronomic adjudication.

### Architectural & Reasoner Ablation Study

Empirical validation across 5 architectural variants under Pellet DL forward-chaining reasoning (evaluated on $n=80$ benchmark cases; persistent results in `results/ablation.md`):

| Variant | Exact Match (%) | Micro Prec (%) | Micro Rec (%) | Micro F1 (%) | Mean Latency (ms) | P95 Latency (ms) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG Full (T1 + T2 Stratified, Pellet DL)** | **92.50%** | **97.4%** | **95.0%** | **96.2%** | **520.76** | **579.41** |
| *Ablation A: Tier 1 Canonical Only (Pellet DL)* | 32.50% | 100.0% | 10.0% | 18.2% | 515.57 | 574.25 |
| *Ablation B: Tier 2 Relaxed Only (Pellet DL)* | 92.50% | 97.4% | 95.0% | 96.2% | 502.42 | 530.42 |
| *Ablation C: Flat Rules Unstratified (Pellet DL)* | 92.50% | 97.4% | 95.0% | 96.2% | 503.51 | 514.83 |
| *Baseline Control: No Reasoner (Set-Matching)* | 92.50% | 97.4% | 95.0% | 96.2% | 0.00 | 0.00 |

> **Key Architectural Insights**:
> 1. **Deductive Specificity vs Sensitivity**: Ablating Tier-2 relaxed rules (*Canonical Only*) causes recall to collapse from 95.0% to 10.0%, while guaranteeing 100% precision (0 false positives). Tier-2 expands field sensitivity under incomplete symptom observation.
> 2. **Reasoner Engineering Trade-Off**: Pure Python set-matching executes in <0.05 ms per query, whereas Pellet DL requires ~520 ms. The DL reasoner is justified not by speed, but by ontological property subsumption (`hasConfirmedPest` ⊑ `hasConfirmedThreat`), consistency verification, and deductive derivation trees for explainable AI (XAI).

---

## Citation

If you use this software in your research, please cite:

```bibtex
@software{furqon2026ricekg,
  author    = {Furqon, Muhammad Ariful},
  title     = {{RiceKG}: Knowledge Graph and Semantic Web Rule Language-Based Expert System for Rice Pest and Disease Diagnosis Under Symptom Uncertainty},
  year      = {2026},
  url       = {https://github.com/Ariful-Furqon/RiceKG-Expert-System},
  license   = {MIT}
}
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.