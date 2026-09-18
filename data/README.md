# RiceKG Benchmark Datasets & Provenance Documentation

This directory contains benchmark datasets used for evaluating the RiceKG expert system, accompanied by rigorous provenance tracking to avoid circular evaluation artifacts.

---

## 1. Deductive Verification Suite (`verification_suite.csv`)

### Overview
- **File**: `data/verification_suite.csv` (formerly `benchmark_synthetic.csv`, `benchmark_augmented.csv`, `dataText.csv`)
- **Sample Size ($n$)**: 73 test cases (narrowed from 80 following Part 5 scope narrowing)
- **Provenance**: `rule_derived`
- **Authorship**: Knowledge engineering team during SWRL rule base authoring.

### Composition & Stratification (T1–T6)

The 73 cases are partitioned into six diagnostic tiers:

| Tier | Case IDs | Description | Construction Method | Target Count |
|---|:---:|---|---|:---:|
| **T1: Canonical Single Threats** | 1–6 | Full pathognomonic profiles ($4 \le \|S\| \le 6$) | Exactly matches the antecedent clauses of Tier-1 SWRL rules `SWRL-R02`, `SWRL-R06` to `SWRL-R10`. | 6 (1 per in-scope threat) |
| **T2: Relaxed Single Threats** | 7–12 | Partial symptom profiles ($2 \le \|S\| \le 3$) | Exactly matches the minimal antecedent clauses of Tier-2 SWRL rules `SWRL-R12`, `SWRL-R16` to `SWRL-R20`. | 6 (1 per in-scope threat) |
| **T3: Co-infection Pairs** | 13–21 | Simultaneous multi-threat infections | Synthetic union of disjoint antecedent subsets from two distinct in-scope threats (e.g. Bacterial Leaf Blight + Rice Blast). | 9 |
| **T4: Noise & Distractor Cases** | 22–27 | Single threats with non-diagnostic noise | Threat antecedents perturbed with unspecific environmental symptoms (e.g. `Rainy_Season_Outbreak`, `Uniform_Field_Infection`). | 6 |
| **T5: Partial Symptom Variants** | 28–34 | Incomplete combinations | Partial subsets of canonical antecedents with varying symptom counts for in-scope threats. | 7 |
| **T6: Negative & Out-of-Scope Controls** | 35–73 | Non-diagnostic / Out-of-scope controls | 20 negative controls with insufficient evidence (`No_Diagnosis`) + 19 insect damage controls (`insect damage, out of scope`). | 39 |

### Case-by-Case Resolution for 26 Insect-Referencing Cases (Part 5 Scope Narrowing)

When the diagnostic scope was narrowed from 10 classes to 6 evidence-backed classes (retaining 5 phytopathogenic diseases and 1 parasitic nematode `Rice_Root_Nematode`), exactly 26 cases in the original 80-case suite referenced one of the four excluded insect pest classes (`Grasshopper`, `Rice_Stem_Borer`, `Rice_Bug`, `Brown_Planthopper`). Each was adjudicated individually without bulk resolution:

| Original Case | Original Diagnosis | Resolution | Symptoms Evaluated | Agronomic & Protocol Rationale |
|:---:|---|:---:|---|---|
| Case 01 | `Grasshopper` | Converted to Out-of-Scope Control | `Brown_Nymphs`, `Yellow_Nymphs`, `Eggs_On_Plant`, `Broad_Leaf_Damage`, `Severed_Panicles`, `Leaf_Chewing_Damage` | Purely insect defoliation signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 03 | `Rice_Stem_Borer` | Converted to Out-of-Scope Control | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Deadheart_Seedling`, `Easily_Pulled_Tillers`, `Whitehead_Empty_Panicles` | Culm boring signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 04 | `Rice_Bug` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Leaf_Margin_Sap_Sucking`, `Rotten_Panicles`, `Random_Feeding_Pattern`, `Empty_Grains` | Grain and foliar sap extraction signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 05 | `Brown_Planthopper` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Plant_Yellowing`, `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Blackened_Feeding_Punctures` | Direct hopperburn and sap extraction signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 11 | `Grasshopper` | Converted to Out-of-Scope Control | `Severed_Panicles`, `Leaf_Chewing_Damage` | Chewing defoliation signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 13 | `Rice_Stem_Borer` | Converted to Out-of-Scope Control | `Frass_In_Stem`, `Bore_Holes_In_Stem` | Minimal culm boring signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 14 | `Rice_Bug` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Empty_Grains` | Minimal grain damage signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 15 | `Brown_Planthopper` | Converted to Out-of-Scope Control | `Hopperburn_Drying`, `Circular_Hopperburn_Patches` | Minimal hopperburn signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 24 | `Rice_Blast and Rice_Stem_Borer` | **Removed** | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Panicle_Neck_Rot`, `Diamond_Shaped_Lesions` | Co-infection between retained disease and excluded insect; Blast is independently evaluated in pure disease co-infection cases. |
| Case 25 | `Grasshopper and Rice_Stem_Borer` | Converted to Out-of-Scope Control | `Severed_Panicles`, `Leaf_Chewing_Damage`, `Frass_In_Stem`, `Bore_Holes_In_Stem` | Purely insect-derived co-occurrence; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 28 | `Brown_Planthopper and False_Smut` | **Removed** | `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Rusty_Grain_Balls`, `Blackened_Grain_Balls` | Co-infection between retained disease and excluded insect; False Smut is independently evaluated in pure disease co-infection cases. |
| Case 29 | `Grasshopper and Rice_Bug` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Empty_Grains`, `Severed_Panicles`, `Leaf_Chewing_Damage` | Multi-pest insect feeding damage; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 32 | `False_Smut and Rice_Stem_Borer` | **Removed** | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Rusty_Grain_Balls`, `Blackened_Grain_Balls` | Co-infection between retained disease and excluded insect; False Smut is independently evaluated in pure disease co-infection cases. |
| Case 33 | `Grasshopper and Rice_Blast` | **Removed** | `Severed_Panicles`, `Leaf_Chewing_Damage`, `Panicle_Neck_Rot`, `Diamond_Shaped_Lesions` | Co-infection between retained disease and excluded insect; Blast is independently evaluated in pure disease co-infection cases. |
| Case 34 | `Brown_Planthopper and Rice_Tungro_Virus` | **Removed** | `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Green_Leafhopper_Present`, `Yellowing_Leaves` | Co-infection between retained disease and excluded insect; Tungro is independently evaluated in pure disease co-infection cases. |
| Case 35 | `Bacterial_Leaf_Blight and Rice_Stem_Borer` | **Removed** | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Yellowing_Leaf_Veins`, `Uniform_Field_Infection` | Co-infection between retained disease and excluded insect; BLB is independently evaluated in pure disease co-infection cases. |
| Case 38 | `Rice_Root_Nematode and Rice_Stem_Borer` | **Removed** | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Deadheart_Seedling`, `Stunted_Growth` | Co-infection between retained nematode and excluded insect; Nematode is independently evaluated in pure disease co-infection cases. |
| Case 39 | `Rice_Stem_Borer` | Converted to Out-of-Scope Control | `Frass_In_Stem`, `Bore_Holes_In_Stem`, `Rainy_Season_Outbreak`, `Plant_Yellowing` | Perturbed insect culm damage signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 40 | `Grasshopper` | Converted to Out-of-Scope Control | `Severed_Panicles`, `Leaf_Chewing_Damage`, `Deadheart_Seedling`, `Localized_Leaf_Yellowing` | Perturbed insect defoliation signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 42 | `Rice_Bug` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Empty_Grains`, `Rainy_Season_Outbreak`, `Rapid_Disease_Spread` | Perturbed grain sucking signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 43 | `Brown_Planthopper` | Converted to Out-of-Scope Control | `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Blackened_Feeding_Punctures`, `Rotten_Panicles` | Perturbed hopperburn signs; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 49 | `Rice_Stem_Borer` | Converted to Out-of-Scope Control | `Bore_Holes_In_Stem`, `Frass_In_Stem`, `Whitehead_Empty_Panicles`, `Rainy_Season_Outbreak` | Partial insect profile; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 54 | `Grasshopper` | Converted to Out-of-Scope Control | `Severed_Panicles`, `Leaf_Chewing_Damage`, `Broad_Leaf_Damage`, `Eggs_On_Plant` | Partial insect profile; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 55 | `Brown_Planthopper` | Converted to Out-of-Scope Control | `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Empty_Grains`, `Plant_Yellowing` | Partial insect profile; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 56 | `Rice_Bug` | Converted to Out-of-Scope Control | `Nymphs_Present`, `Adult_Insects_Present`, `Empty_Grains`, `Leaf_Margin_Sap_Sucking` | Partial insect profile; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |
| Case 59 | `Brown_Planthopper` | Converted to Out-of-Scope Control | `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Nymphs_Present`, `Adult_Insects_Present`, `Empty_Grains` | Partial insect profile; converted to an out-of-scope control expecting `"insect damage, out of scope"`. |

**Summary**: 19 cases converted to out-of-scope controls with target `"insect damage, out of scope"`; 7 co-infections removed. Total verification suite size: 80 - 7 = 73 cases.

### Methodological Disclosure & Circularity
> [!IMPORTANT]
> As disclosed in `docs/LIMITATIONS.md`, **`verification_suite.csv` is rule-derived**. Evaluating an expert system on cases generated from earlier Horn-clause rules exhibited ceiling consistency. It verifies rule firing consistency and deductive completeness, but **cannot be interpreted as empirical clinical or field diagnostic accuracy**.

---

## 2. Independent Peer-Reviewed Field Benchmark (`benchmark_field.csv`)

### Zero-Loss Property Under Scope Narrowing
> [!NOTE]
> **Zero Empirical Loss**: Exactly **0 of the 38 cases** in the `dev` and `eval` splits of `data/benchmark_field.csv` diagnose an insect class. The peer-reviewed *First Report* disease-note literature naturally reports plant pathogens and parasitic nematodes, not insect pests. Consequently, the entire independent field benchmark survived the Part 5 scope narrowing completely untouched with **100% data retention (39/39 cases)**.

### Overview
- **File**: `data/benchmark_field.csv`
- **Sample Size ($n$)**: 39 independently verified cases
- **Schema**:
  `case_id,raw_symptom_text,symptom_1,symptom_2,symptom_3,symptom_4,symptom_5,symptom_6,diagnosis,source,location,observation_date,annotator_id,ground_truth_method,citation,doi,case_type,split`
- **Provenance**: `literature_case` / `lab_confirmed` (primary peer-reviewed disease notes)
- **Primary Sources**: APS *Plant Disease* ("Disease Notes"), BSPP *New Disease Reports*, *Crop Protection*, *Insects*, *Plant and Soil*, *Field Crops Research*.
- **Circularity Avoidance**: IRRI Rice Doctor was explicitly excluded because the ontology's symptoms were historically derived from IRRI diagnostic compendia. Sourcing from independent peer-reviewed literature ensures orthogonal evaluation.

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

The evaluation script (`ricekg/evaluate.py`) supports separate dataset evaluation via `--dataset`:

```bash
# Evaluate deductive verification suite
python -m ricekg.evaluate --dataset verification

# Evaluate independent field/literature benchmark
python -m ricekg.evaluate --dataset field

# Specify custom CSV file
python -m ricekg.evaluate --csv-path data/custom_eval.csv
```

Verification-suite and independent field metrics are **never pooled into a single composite accuracy score**: the first measures deductive consistency, the second measures diagnostic accuracy.

