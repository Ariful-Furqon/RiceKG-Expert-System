# RiceKG: Knowledge Graph and SWRL-Based Expert System for Rice Pest and Disease Diagnosis

[![CI Evaluation](https://github.com/Ariful-Furqon/RiceKG-Expert-System/actions/workflows/ci.yml/badge.svg)](https://github.com/Ariful-Furqon/RiceKG-Expert-System/actions/workflows/ci.yml)
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

Benchmark evaluation on **80 stratified multi-label test instances** across 6 evaluation tiers designed to stress-test the system under field symptom uncertainty:

| Tier | Description | Cases |
|---|---|---|
| T1 | Canonical full-symptom profiles | 10 |
| T2 | Relaxed partial-symptom profiles | 10 |
| T3 | Multi-threat co-infections (including masking scenarios) | 18 |
| T4 | Noisy field observations with environmental distractors | 22 |
| T5 | Symptom under-reporting / sub-threshold observations | 8 |
| T6 | Non-pathognomonic environmental & negative controls | 12 |

### Aggregate Metrics

| Metric | Score |
|---|---|
| **Multi-Label Accuracy ((TP+TN)/Total)** | **99.25%** |
| **Exact-Match Case Accuracy** | **92.50%** |
| **Micro-Average Precision** | **97.4%** |
| **Micro-Average Recall** | **95.0%** |
| **Micro-Average F1-Score** | **96.2%** |

### Per-Class Confusion Matrix

| Diagnosis (Class) | TP | FP | FN | TN | Precision (%) | Recall (%) | F1 (%) |
|---|---|---|---|---|---|---|---|
| Grasshopper | 7 | 0 | 0 | 73 | 100.0% | 100.0% | 100.0% |
| Rice_Root_Nematode | 6 | 0 | 1 | 73 | 100.0% | 85.7% | 92.3% |
| Rice_Stem_Borer | 9 | 0 | 0 | 71 | 100.0% | 100.0% | 100.0% |
| Rice_Bug | 5 | 1 | 0 | 74 | 83.3% | 100.0% | 90.9% |
| Brown_Planthopper | 7 | 0 | 0 | 73 | 100.0% | 100.0% | 100.0% |
| Bacterial_Leaf_Blight | 9 | 0 | 0 | 71 | 100.0% | 100.0% | 100.0% |
| False_Smut | 9 | 0 | 0 | 71 | 100.0% | 100.0% | 100.0% |
| Rice_Blast | 10 | 1 | 1 | 68 | 90.9% | 90.9% | 90.9% |
| Rice_Grassy_Stunt | 7 | 0 | 1 | 72 | 100.0% | 87.5% | 93.3% |
| Rice_Tungro_Virus | 7 | 0 | 1 | 72 | 100.0% | 87.5% | 93.3% |
| **TOTAL (Micro Avg)** | **76** | **2** | **4** | **718** | **97.4%** | **95.0%** | **96.2%** |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.