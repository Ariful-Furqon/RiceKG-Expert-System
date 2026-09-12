# RiceKG: Knowledge Graph and SWRL-Based Expert System for Rice Pest and Disease Diagnosis

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
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

---

## Repository Structure

```
RiceKG-Expert-System/
├── app.py                  # Flask web application & diagnosis endpoints
├── model.py                # OWL 2 ontology schema, SWRL rule definitions, and Pellet inference
├── evaluate.py             # Multi-label evaluation with per-class confusion matrix
├── test.py                 # Automated pytest test suite (18 test cases)
├── dataText.csv            # Benchmark dataset (20 field test cases with symptoms & targets)
├── rice_ontology.owl       # Generated OWL 2 RDF/XML ontology file
├── requirements.txt        # Python package dependencies
├── Procfile                # WSGI deployment configuration
├── CITATION.cff            # Citation metadata for academic referencing
├── LICENSE                 # MIT License
├── static/
│   ├── site.css            # Application stylesheet
│   └── data.json           # Biotic threats knowledge catalog (IPM prescriptions)
├── templates/
│   ├── layout.html         # Base template with navigation
│   ├── index.html          # Interactive symptom selection form
│   ├── result.html         # Diagnostic report with IPM recommendations
│   ├── threats.html        # Biotic threats knowledge base catalog
│   └── about.html          # System architecture information
└── README.md               # Documentation
```

---

## Installation & Setup

### Prerequisites
- **Python 3.9+**
- **Java Runtime Environment (JRE/JDK 11+)** — Required for the Pellet DL Reasoner

> **Note**: The Pellet reasoner is bundled with `owlready2` but requires a Java runtime to execute. Ensure `java` is available on your system PATH.

### 1. Clone the Repository
```bash
git clone https://github.com/Ariful-Furqon/RiceKG-Expert-System.git
cd RiceKG-Expert-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
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

### Launch Web Application
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000/`

---

## Evaluation Results

Benchmark evaluation on 20 multi-label field test instances:

| Metric | Score |
|---|---|
| **Multi-Label Accuracy ((TP+TN)/Total)** | **99.50%** |
| **Exact-Match Case Accuracy** | **95.00%** |
| **Micro-Average Precision** | **100.0%** |
| **Micro-Average Recall** | **95.7%** |
| **Micro-Average F1-Score** | **97.8%** |

---

## Citation

If you use this software in your research, please cite:

```bibtex
@software{furqon2026ricekg,
  author    = {Furqon, Ariful},
  title     = {{RiceKG}: Knowledge Graph and Semantic Web Rule Language-Based Expert System for Rice Pest and Disease Diagnosis},
  year      = {2026},
  url       = {https://github.com/Ariful-Furqon/RiceKG-Expert-System},
  license   = {MIT}
}
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.