# RiceKG Benchmark Datasets & Provenance Documentation

This directory contains benchmark datasets used for evaluating the RiceKG expert system, accompanied by rigorous provenance tracking to avoid circular evaluation artifacts.

---

## 1. Synthetic Rule-Derived Benchmark (`benchmark_synthetic.csv`)

### Overview
- **File**: `data/benchmark_synthetic.csv` (formerly `dataText.csv`)
- **Sample Size ($n$)**: 80 test cases
- **Provenance**: `rule_derived`
- **Authorship**: Knowledge engineering team during SWRL rule base authoring.

### Composition & Stratification (T1–T6)

The 80 cases are partitioned into six diagnostic tiers:

| Tier | Case IDs | Description | Construction Method | Target Count |
|---|:---:|---|---|:---:|
| **T1: Canonical Single Threats** | 1–10 | Full pathognomonic profiles ($4 \le \|S\| \le 6$) | Exactly matches the antecedent clauses of Tier-1 SWRL rules `SWRL-R01` to `SWRL-R10`. | 10 (1 per threat) |
| **T2: Relaxed Single Threats** | 11–20 | Partial symptom profiles ($2 \le \|S\| \le 3$) | Exactly matches the minimal antecedent clauses of Tier-2 SWRL rules `SWRL-R11` to `SWRL-R20`. | 10 (1 per threat) |
| **T3: Co-infection Pairs** | 21–38 | Simultaneous multi-threat infections | Synthetic union of disjoint antecedent subsets from two distinct threats (e.g. Bacterial Leaf Blight + Rice Blast). | 18 |
| **T4: Noise & Distractor Cases** | 39–48 | Single threats with non-diagnostic noise | Threat antecedents perturbed with unspecific environmental symptoms (e.g. `Rainy_Season_Outbreak`, `Plant_Yellowing`). | 10 |
| **T5: Partial Symptom Variants** | 49–60 | Incomplete combinations | Partial subsets of canonical antecedents with varying symptom counts. | 12 |
| **T6: Negative Controls** | 61–80 | Non-diagnostic / Insufficient evidence | Isolated symptoms (e.g. single symptom `Severed_Panicles` or general background traits) where no rule should fire (`No_Diagnosis`). | 20 |

### Methodological Disclosure & Circularity
> [!IMPORTANT]
> As disclosed in `docs/LIMITATIONS.md`, **`benchmark_synthetic.csv` is rule-derived**. Evaluating an expert system on cases generated from its own Horn-clause rules guarantees near-ceiling performance (99.25% multi-label accuracy, 92.50% exact-match accuracy) by construction. It verifies rule firing consistency and deductive completeness, but **cannot be interpreted as empirical clinical or field diagnostic accuracy**.

---

## 2. Independent Peer-Reviewed Field Benchmark (`benchmark_field.csv`)

### Overview
- **File**: `data/benchmark_field.csv`
- **Sample Size ($n$)**: 32 independently verified cases
- **Schema**:
  `case_id,raw_symptom_text,symptom_1,symptom_2,symptom_3,symptom_4,symptom_5,symptom_6,diagnosis,source,location,observation_date,annotator_id,ground_truth_method,citation,doi`
- **Provenance**: `literature_case` / `lab_confirmed` (primary peer-reviewed disease notes)
- **Primary Sources**: APS *Plant Disease* ("Disease Notes"), BSPP *New Disease Reports*, *Crop Protection*, *Insects*, *Plant and Soil*, *Field Crops Research*.
- **Circularity Avoidance**: IRRI Rice Doctor was explicitly excluded because the ontology's 45 symptoms were historically derived from IRRI diagnostic compendia. Sourcing from independent peer-reviewed literature ensures orthogonal evaluation.

### Mandatory Two-Stage Construction Protocol & Verification Gates
1. **Stage A (Provenance & Verbatim Extraction)**:
   - For every case, the authentic publication was retrieved and `raw_symptom_text` was extracted **verbatim** from the published abstract/text.
   - `location` and `observation_date` appear directly in the paper; when observation date is unstated, `observation_date` is left empty (`""`).
   - `ground_truth_method`: set to `lab_confirmed` strictly where isolation, PCR, sequencing, or Koch's postulates are reported (or `expert_visual` for macroscopic/microscopic spore structures).
   - Real publication titles are strictly preserved in `citation` without alteration.
   - Every DOI is audited and verified against the official Crossref API (`api.crossref.org/works/{doi}`).
2. **Stage B (Vocabulary Mapping & Annotator Status)**:
   - `annotator_id` is set to `"unassigned"` pending formal human agronomist multi-rater trial.
   - Symptoms mapped in this stage are uncurated/preliminary draft mappings pending full agronomic adjudication.
   - `raw_symptom_text` is preserved in the CSV as a permanent verbatim audit trail.

### Dataset Composition ($n=32$ Peer-Reviewed Disease Notes)
All 32 cases are drawn strictly from primary peer-reviewed disease notes (APS *Plant Disease* "Disease Notes"):
- **Target In-Scope Threats** ($n=5$, 15.6%):
  - Rice Blast (*Magnaporthe oryzae* / *Pyricularia grisea*, $n=2$: Western Australia, California)
  - Bacterial Leaf Blight (*Xanthomonas oryzae pv. oryzae*, $n=1$: Madagascar)
  - Rice Root Nematode (*Meloidogyne graminicola*, $n=1$: Sichuan, China)
  - False Smut (*Ustilaginoidea virens*, $n=1$: Louisiana)
- **Out-of-Scope Pathogens & Emerging Threat Negative Controls** ($n=27$, 84.4%):
  - Emerging bacterial panicle blights and foot rots (*Xanthomonas sacchari*, *Burkholderia glumae*, *Burkholderia gladioli*, *Dickeya zeae*, *Pantoea agglomerans*, *Pantoea ananatis*)
  - Bacterial leaf streak (*Xanthomonas oryzae pv. oryzicola*)
  - Emerging fungal blights and rots (*Sarocladium oryzae*, *Alternaria gaisen*, *Alternaria arborescens*, *Cochliobolus lunatus*, *Fusarium andiyazi*, *Mycovellosiella oryzae*)
  - Emerging viral threats (*Rice stripe necrosis virus*, *Rice yellow mottle virus*, *Rice stripe virus*)
  - Emerging nematode threats (*Aphelenchoides besseyi*, *Heterodera elachista*)
  - Evaluated as true negative controls (`diagnosis: No_Diagnosis`).

---

## 3. Usage in Evaluation Pipeline

The evaluation script (`evaluate.py`) supports separate dataset evaluation via `--dataset`:

```bash
# Evaluate synthetic verification benchmark
python evaluate.py --dataset synthetic

# Evaluate independent field/literature benchmark
python evaluate.py --dataset field

# Specify custom CSV file
python evaluate.py --csv-path data/custom_eval.csv
```

Synthetic and independent metrics are **never pooled into a single composite accuracy score**.

