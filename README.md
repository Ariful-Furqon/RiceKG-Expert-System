# RiceKG: Knowledge Graph and Semantic Web Rule Language-Based Expert System for Rice Pest and Disease Diagnosis

An ontology-driven expert system leveraging Web Ontology Language (OWL 2) and Semantic Web Rule Language (SWRL) with Pellet reasoner for diagnosing rice pests and diseases based on observed field symptoms.

---

## 🌾 Overview

This repository provides an automated semantic reasoning system for diagnosing 10 major rice pests and diseases. The system integrates:
- **Ontology (OWL 2)**: Formal conceptualization of rice entities, symptoms, pests, diseases, and treatment management.
- **SWRL Rules**: Deterministic forward-chaining rules linking combinations of phenotypic symptoms to specific diagnoses.
- **Automated Pellet Reasoner (`owlready2`)**: Semantic inference engine executing property assertion and multi-label diagnosis.
- **Flask Web Interface**: User-friendly web interface for interactive symptom selection and diagnosis.
- **Multi-Label Evaluation Suite**: Automated script computing Confusion Matrix metrics (TP, FP, FN, TN, Precision, Recall, F1, Accuracy).

---

## 🔬 Diagnosed Pests & Diseases

| Type | Name | Scientific / Common Identifier |
|---|---|---|
| **Pest** | `Grasshopper` | *Oxya chinensis* / Grasshopper |
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

## 📁 Repository Structure

```
RiceKG-Expert-System/
├── app.py                  # Flask web application & diagnosis endpoints
├── model.py                # Ontology schema, SWRL rule definitions, and Pellet inference
├── evaluate.py             # Evaluation script for full confusion matrix calculation
├── test.py                 # Unit test script with sample cases
├── dataText.csv            # Test dataset (20 field test cases with symptoms & targets)
├── rice_ontology.owl       # Generated OWL 2 RDF/XML ontology file
├── static/                 # CSS, stylesheets, and assets
├── templates/              # HTML templates (Bootstrap + Jinja2)
│   ├── index.html          # Main symptom selection form
│   ├── result.html         # Diagnostic result display
│   ├── layout.html         # Base template
│   └── about.html          # Project information
├── requirements.txt        # Python package dependencies
└── README.md               # Documentation
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Java Runtime Environment (JRE/JDK 11+) for Pellet Reasoner

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/RiceKG-Expert-System.git
cd RiceKG-Expert-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or install core dependencies directly)*:
```bash
pip install flask owlready2
```

---

## 🧪 Usage

### Run Unit Tests
```bash
python test.py
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

## 📊 Evaluation Results

Benchmark evaluation on 20 multi-label field test instances:

| Metric | Score |
|---|---|
| **Multi-Label Accuracy ((TP+TN)/Total)** | **99.50%** |
| **Exact-Match Case Accuracy** | **95.00%** |
| **Micro-Average Precision** | **100.0%** |
| **Micro-Average Recall** | **95.7%** |
| **Micro-Average F1-Score** | **97.8%** |

---

## 📄 Citation & License

This project is licensed under the MIT License.
