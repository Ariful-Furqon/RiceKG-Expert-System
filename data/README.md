# RiceKG Benchmark Datasets & Provenance Documentation

This directory contains benchmark datasets used for evaluating the RiceKG expert system, accompanied by rigorous provenance tracking to avoid circular evaluation artifacts.

---

## 1. Deductive Verification Suite (`verification_suite.csv`)

### Overview
- **File**: `data/verification_suite.csv` (formerly `benchmark_synthetic.csv`, `benchmark_augmented.csv`, `dataText.csv`)
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
> As disclosed in `docs/LIMITATIONS.md`, **`verification_suite.csv` is rule-derived**. Evaluating an expert system on cases generated from earlier Horn-clause rules exhibited ceiling consistency (60.00% exact match and 95.12% multi-label accuracy following P0-5 rule revisions; formerly 92.50%). It verifies rule firing consistency and deductive completeness, but **cannot be interpreted as empirical clinical or field diagnostic accuracy**.

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

### Symptom Identifier Normalization (`symptom_mapping.csv`)

The `symptom_*` columns of this file were originally populated with descriptive snake_case slugs
authored during Stage B extraction (for example `seed_yellowish_green_velvety_balls`). Those slugs form
a namespace disjoint from the ontology vocabulary `model.ALL_SYMPTOMS`, which uses identifiers such as
`Rusty_Grain_Balls`: **none of the 25 recorded descriptors matched any of the then 45 ontology terms**, while
`verification_suite.csv` matched on all 45. As a result every case in this benchmark reached the
reasoner as an empty assertion set, and the benchmark could not exercise the rule base at all.

[`symptom_mapping.csv`](symptom_mapping.csv) records the resolution of each descriptor with a
justification:

- **16 descriptors mapped** to an ontology term. Nine were direct semantic identities
  (`roots_hook_shaped_galls` → `Hook_Like_Root_Swelling`, `seed_empty_unfilled` → `Empty_Grains`);
  seven more became mappable when the P0-5 Step 2 vocabulary extension added terms for water-soaked
  lesions, bacterial ooze, mottling, interveinal chlorosis, grain discoloration, leaf sheath lesions
  and culm rot (see `docs/ONTOLOGY.md`).
- **9 descriptors remain unmapped** because the ontology still models no corresponding concept —
  striping and streaking patterns, leaf bleaching, whitened leaf tips, whole-leaf withering, generic
  discoloration, generic drying, root discoloration and plant malformation. Near-misses were
  deliberately *not* forced: `Yellowing_Leaf_Tips` is not "whitened tips", and `Hopperburn_Drying` is
  planthopper-specific and cannot stand for generic drying.

Unmapped descriptors are preserved per case in the `unmapped_terms` column (placed after `diagnosis` so
the evaluation loader does not read them as symptoms), keeping the vocabulary gap auditable. The
verbatim `raw_symptom_text` column is unchanged, so source provenance is unaffected by this
normalization.

---

## 3. Usage in Evaluation Pipeline

The evaluation script (`evaluate.py`) supports separate dataset evaluation via `--dataset`:

```bash
# Evaluate deductive verification suite
python evaluate.py --dataset verification

# Evaluate independent field/literature benchmark
python evaluate.py --dataset field

# Specify custom CSV file
python evaluate.py --csv-path data/custom_eval.csv
```

Verification-suite and independent field metrics are **never pooled into a single composite accuracy score**: the first measures deductive consistency, the second measures diagnostic accuracy.

