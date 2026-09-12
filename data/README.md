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

## 2. Independent Field & Literature Benchmark (`benchmark_field.csv`)

### Overview
- **File**: `data/benchmark_field.csv`
- **Schema**:
  `case_id,symptom_1,symptom_2,symptom_3,symptom_4,symptom_5,symptom_6,diagnosis,source,location,observation_date,annotator_id,ground_truth_method,citation`
- **Provenance**: `expert_authored` / `literature_case` / `field_observed`
- **Purpose**: Independent evaluation on cases authored or published outside the RiceKG rule-authoring process to break circularity.

### Ground Truth Verification Methods
- `literature_case`: Sourced from peer-reviewed phytopathology literature or the IRRI Rice Doctor diagnostic compendium with full bibliographic citations.
- `lab_confirmed`: Diagnosed via laboratory isolation, PCR, or microscopic pathogen verification.
- `expert_visual`: Visual diagnosis by certified agronomist/phytopathologist with inter-rater agreement logged.

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

