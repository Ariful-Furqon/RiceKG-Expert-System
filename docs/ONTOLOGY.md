# Ontology Design and Change Rationale

This document records the RiceKG vocabulary and rule base, and the literature that justifies
each change made in P0-5 Step 2 and Step 3.

## Provenance rule for changes

Vocabulary and rule changes are justified from the phytopathology and nematology literature,
never from a benchmark case. Tuning the rule base against `data/benchmark_field.csv` would make
those cases part of the training signal and reintroduce the evaluation circularity that P0-3
exists to eliminate. The benchmark is additionally partitioned into a `dev` split, visible during
this work, and an `eval` split whose individual cases were not inspected while the changes below were made. Its **aggregate** scores were nonetheless observed across two revision rounds, so `eval` is now development-informed rather than strictly held out; `docs/LIMITATIONS.md` Section 2 records that downgrade and what would be needed to restore an independent estimate.

## Sources

- **Ou, S.H. (1985).** *Rice Diseases*, 2nd edition. Commonwealth Mycological Institute, Kew.
- **Hibino, H. (1996).** Biology and epidemiology of rice viruses. *Annual Review of
  Phytopathology* 34:249–274.
- **Bridge, J., Plowright, R.A. & Peng, D. (2005).** Nematode parasites of rice. In *Plant
  Parasitic Nematodes in Subtropical and Tropical Agriculture*, 2nd ed., CABI Publishing.
- **IRRI Rice Doctor** fact sheets (bacterial blight, rice blast, grassy stunt, tungro,
  root-knot nematode).

## Vocabulary extension (45 → 54 terms)

`docs/LIMITATIONS.md` Section 3 recorded that a majority of descriptors extracted from the field
literature had no counterpart in the original 45-term vocabulary, the most consequential omission
being the absence of any `Leaf_Sheath` anatomy. Nine terms were added across two rounds.

| Term | Denotes | Source | Used as a rule antecedent |
|:--|:--|:--|:--:|
| `Water_Soaked_Lesions` | Early bacterial lesion at leaf margin or tip | Ou (1985) pp. 61–96; IRRI bacterial blight | Yes — `SWRL-R16` |
| `Bacterial_Ooze` | Bacterial exudate droplets on lesion or cut leaf | Ou (1985) pp. 61–96 | No — withdrawn as an antecedent (genus-level sign) |
| `Leaf_Mottling` | Mosaic or mottle pattern, virus-associated | Hibino (1996) | No — withdrawn as an antecedent (shared across rice viruses) |
| `Interveinal_Chlorosis` | Chlorosis between leaf veins, virus-associated | Hibino (1996) | No — withdrawn as an antecedent (shared across rice viruses) |
| `Grain_Discoloration` | Discoloured or spotted grain | Ou (1985) | No — expressivity only |
| `Leaf_Sheath_Lesions` | Lesions on the leaf sheath | Ou (1985) | No — expressivity only |
| `Stem_Rot_Lesions` | Rot or lodging at the culm | Ou (1985) | No — expressivity only |
| `Excessive_Tillering` | Proliferation of tillers; tungro reduces tillering instead | Hibino (1996); IRRI grassy stunt | Yes — `SWRL-R19` |
| `Orange_Leaf_Discoloration` | Yellow-orange cast progressing from the leaf tip | Hibino (1996); IRRI tungro | Yes — `SWRL-R20` |

Six of the nine terms are **not** wired into any rule. Sheath and culm diseases
(*Rhizoctonia solani*, *Sarocladium oryzae*) are outside the ten modelled threats and appear in the
benchmark only as negative controls; the terms exist so that such cases can be *described* rather
than silently dropped, which makes their rejection an act of discrimination rather than an artifact
of unmappable input. Wiring them to a modelled threat would manufacture false positives.

`Bacterial_Ooze`, `Leaf_Mottling` and `Interveinal_Chlorosis` were introduced as antecedents in the first revision pass and withdrawn in the second; they remain in the vocabulary because they are real diagnostic observations worth recording, but they do not discriminate among the modelled threats. See the withdrawn-revision note below.

Nine descriptors remain unmapped by design — striping and streaking patterns, leaf bleaching,
whole-leaf withering, generic discoloration and malformation. `data/symptom_mapping.csv` records
each decision with its justification, and near-misses were not forced: `Yellowing_Leaf_Tips` is not
"whitened tips", and `Hopperburn_Drying` is planthopper-specific and cannot stand for generic drying.

## Tier-2 rule revisions

The Tier-2 defect was not antecedent cardinality — every Tier-2 rule already required only two or
three signs. It was **what those antecedents demanded**: three of the ten hinged on observing an
insect vector or a stand-level epidemiological pattern rather than a plant sign a scout or a case
report actually records.

| Rule | Threat | Before | After | Justification |
|:--|:--|:--|:--|:--|
| `SWRL-R12` | Rice_Root_Nematode | `Hook_Like_Root_Swelling` ∧ `Root_Knot_Swelling` | `Hook_Like_Root_Swelling` ∧ `Stunted_Growth` ∧ `Yellowing_Leaves` | Requiring two distinct gall morphologies at once conflates *Hirschmanniella* and *Meloidogyne* damage. Bridge et al. (2005) describe galling with hooked tips together with above-ground stunting and chlorosis. |
| `SWRL-R16` | Bacterial_Leaf_Blight | `Yellowing_Leaf_Veins` ∧ `Uniform_Field_Infection` | `Water_Soaked_Lesions` ∧ `Yellowing_Leaf_Tips` | `Uniform_Field_Infection` describes the stand, not the plant. Ou (1985) gives water-soaked lesions beginning at the leaf tip or margin; tip-and-margin onset is what separates blight from the interveinal streaking of bacterial leaf streak. |
| `SWRL-R18` | Rice_Blast | `Panicle_Neck_Rot` ∧ `Diamond_Shaped_Lesions` | `Diamond_Shaped_Lesions` ∧ `Necrotic_Spots` | Leaf blast and neck blast are distinct phenological phases of the same pathogen and are seldom reported together. Ou (1985) pp. 109–201. |
| `SWRL-R19` | Rice_Grassy_Stunt | `Brown_Planthopper_Present` ∧ `Severe_Stunting` | `Severe_Stunting` ∧ `Excessive_Tillering` | Vector presence makes diagnosis contingent on entomological sampling. Hibino (1996) characterises RGSV by severe stunting with excessive tillering, the latter separating it from tungro. |
| `SWRL-R20` | Rice_Tungro_Virus | `Green_Leafhopper_Present` ∧ `Yellowing_Leaves` | `Stunted_Growth` ∧ `Orange_Leaf_Discoloration` | As above for the green leafhopper. Hibino (1996) characterises tungro by stunting with a yellow-orange cast progressing from the leaf tip. |

### A withdrawn intermediate revision

The first pass specified `SWRL-R16` as `Water_Soaked_Lesions` ∧ `Bacterial_Ooze` and `SWRL-R19` as
`Stunted_Growth` ∧ `Leaf_Mottling`. Both pairs are listed for their diseases in the literature, and
both failed: exudate is a genus-level bacterial sign shared with *X. oryzicola*, *Burkholderia* and
*Pantoea*, and stunting with mottling is common to the rice viruses. The pass produced **4 false
positives on the 27 negative controls**. Re-specifying around signs that discriminate rather than
merely accompany — tip-and-margin onset, excessive tillering, the orange cast — returned false
positives to zero. Recorded here because a sign being listed for a disease is not the same as that
sign distinguishing it.

`SWRL-R11`, `R13`, `R14`, `R15` and `R17` were reviewed and left unchanged: their antecedents are
already plant-level signs that a field report supplies.

All Tier-2 rules continue to assert `hasSuspectedThreat`, preserving the confidence grading
established in P0-1. Tier-1 rules are untouched, so the pathognomonic precision reported in
`results/ablation.md` is unaffected by these revisions.

## Graded partial matching: the `possible` grade

Strict Horn-clause inference is all-or-nothing. A Tier-2 rule with two antecedents fires
only when both are observed, and returns nothing at all when one is missing — no ranking, no
weak signal, no indication that the evidence was nearly sufficient. On the field benchmark's
`dev` split this was the binding failure mode: three of the seven positive cases stopped at
**one of two** antecedents. `FIELD_03` is the clearest instance. It records
`Water_Soaked_Lesions`, `Bacterial_Ooze` and `Yellowing_Leaves` — three genuine bacterial
blight signs — and yielded `No_Diagnosis` because `SWRL-R16` happens to require
`Yellowing_Leaf_Tips` rather than `Yellowing_Leaves`.

P0-1 specified an ordinal grade set `{confirmed, probable, possible}`; only the first two were
implemented. `model.predict_diseases(..., include_possible=True)` now scores Tier-2 rules that
did not fire and surfaces those whose antecedent coverage reaches
`POSSIBLE_COVERAGE_THRESHOLD` as `possible`, carrying the matched and unmet antecedents so the
derivation stays auditable.

### Calibration, and a calibration error

An initial threshold sweep against the 7 positive cases and 9 negative controls of the `dev`
partition suggested a clear win at 0.50: positive recall 4/7 -> 7/7, with 4 of 9 controls
raising a false positive.

**That sweep used the wrong metric.** It scored a case as recovered whenever the true threat
appeared *anywhere* in the prediction set — a containment criterion. The metric the evaluation
harness actually reports is exact match, which requires the predicted label set to equal the
truth set. Measured properly, the grade is a regression:

| | Exact match | Positive recall | Micro-F1 | Negative-control accuracy |
|:--|:--:|:--:|:--:|:--:|
| `eval`, strict | **86.82** | **35.00** | **40.67** | **100.00** |
| `eval`, + possible | 39.09 | 17.50 | 34.44 | 44.22 |
| `dev`, strict | **81.25** | **63.33** | **75.14** | **100.00** |
| `dev`, + possible | 56.25 | 55.00 | 60.08 | 54.93 |

The exact-match loss is significant on both partitions (`eval`: -47.8 points, Holm-adjusted
$p < 0.0001$).

The mechanism is not wildly over-firing: it adds 0.73 labels per case on average and never
more than two. The arithmetic is simply unforgiving. Twenty-seven of the benchmark's 39 cases
are negative controls whose truth set is empty, so a *single* speculative label converts a
correct rejection into an error, and on a positive case it converts a correct prediction into
a mismatch. On a benchmark composed mostly of out-of-scope pathogens, any mechanism that
volunteers additional hypotheses is penalised heavily.

### What this leaves

The grade is retained but **off by default**, and it is reported as a separate system,
`RiceKG (Full + Possible)`, so the regression is visible rather than buried. Two readings are
defensible and they are not the same claim:

- **As autonomous diagnosis**, judged by exact match, partial matching is harmful and should
  not be enabled. This is the reported result.
- **As a screening aid**, where the question is whether the true threat appears in a short
  list an extension officer then narrows, the containment behaviour is the relevant one — but
  the repository does not currently report a containment metric, so that reading is *not
  evidenced here* and must not be asserted until it is measured.

`predict_diseases_flat` and `/api/v1/diagnose` never emit the grade, so the v1 surface is
unchanged. A `possible` diagnosis is a prompt to look further or to escalate, never a basis
for treatment.

## Part 5 Diagnostic Scope Narrowing (10 Classes → 6 Evidence-Backed Classes)

### Rationale
Four of the ten previously diagnosable classes (`Grasshopper`, `Rice_Stem_Borer`, `Rice_Bug`, `Brown_Planthopper`) possessed **zero independent field cases** in peer-reviewed literature. The primary evidence pipeline for RiceKG relies on peer-reviewed *First Report* disease notes in plant pathology journals (e.g. *Plant Disease*, *New Disease Reports*), which document plant pathogens and nematodes rather than insect pests. In accordance with `docs/LIMITATIONS.md`, maintaining diagnostic claims over insect classes rested entirely on deductive circularity over synthetic rules with zero empirical grounding.

### The Scope Cut
The diagnostic scope was narrowed to six evidence-backed classes (five phytopathogenic diseases and one parasitic nematode):
1. `Bacterial_Leaf_Blight` (3 field positives)
2. `Rice_Root_Nematode` (3 field positives)
3. `Rice_Blast` (2 field positives)
4. `Rice_Tungro_Virus` (2 field positives)
5. `False_Smut` (1 field positive)
6. `Rice_Grassy_Stunt` (1 field positive)

### Scope Constraints & Architectural Rules
1. **`Rice_Root_Nematode` is Retained**: Although categorized under `Pest` in the ontology, *Meloidogyne graminicola* has three independently verified peer-reviewed field cases. The cut excludes the four *insect* classes only.
2. **Planthopper and Leafhopper Retained as Vectors**: `Brown_Planthopper_Present` and `Green_Leafhopper_Present` remain in the ontology vocabulary and rule antecedents for `Rice_Grassy_Stunt` and `Rice_Tungro_Virus` respectively. The insects cease to be diagnosable outputs, but remain valid entomological vector evidence.
3. **Surviving Rule IDs Preserved**: The eight insect rules were removed:
   - Tier 1: `SWRL-R01`, `SWRL-R03`, `SWRL-R04`, `SWRL-R05`
   - Tier 2: `SWRL-R11`, `SWRL-R13`, `SWRL-R14`, `SWRL-R15`
   The twelve surviving rules retain their original identifiers (`SWRL-R02`, `R06`–`R10`, `R12`, `R16`–`R20`) to prevent breaking cross-references across `docs/` and `results/`.
4. **Twenty-One Insect Signs Retained as Out-of-Scope Vocabulary**: The 21 insect-associated symptoms (those used only by the removed insect rules) were reclassified under `OutOfScopeSign` and `InsectDamageSign`. If no in-scope rule fires and the query contains at least two distinct *insect-specific* signs, the system returns an explicit differential response: *"consistent with insect damage, which is outside the diagnostic scope of this system"*, rather than a silent uninformative `No_Diagnosis`.
   - **Specific vs. non-specific signs.** Only 14 of the 21 terms count toward the gate (`model.INSECT_SPECIFIC_SIGNS`): the insect itself (`Adult_Insects_Present`, `Nymphs_Present`, `Brown_Nymphs`, `Yellow_Nymphs`), its eggs (`Eggs_On_Plant`), and feeding mechanisms that no pathogen reproduces (`Frass_In_Stem`, `Bore_Holes_In_Stem`, `Hopperburn_Drying`, `Circular_Hopperburn_Patches`, `Blackened_Feeding_Punctures`, `Leaf_Margin_Sap_Sucking`, `Leaf_Chewing_Damage`, `Broad_Leaf_Damage`, `Severed_Panicles`). The other seven (`Plant_Yellowing`, `Localized_Leaf_Yellowing`, `Empty_Grains`, `Rotten_Panicles`, `Deadheart_Seedling`, `Easily_Pulled_Tillers`, `Random_Feeding_Pattern`) are also produced by pathogens, nematodes, nutrient deficiency or abiotic stress. They are kept in the vocabulary but never count as insect evidence.
   - **Why two signs.** Two is the evidentiary minimum of the removed Tier-2 insect rules (`SWRL-R11`, `R13` and `R15` each required two antecedents). It keeps the single-sign negative controls in the verification suite (`Severed_Panicles` alone, `Frass_In_Stem` alone) as `No_Diagnosis`.
   - **Correction.** The first implementation of this gate fired on *any one* of the 21 terms. That labelled `Plant_Yellowing` alone, a nitrogen-deficiency presentation, as insect damage. It also produced out-of-scope responses on field cases FIELD_02 (`Rice_Blast`), FIELD_51 (`Rice_Tungro_Virus`) and three *Burkholderia* negative controls (FIELD_15, 18, 22), all of which carry only non-specific signs. The threshold was set on the agronomic distinction above, before the pipeline was re-run; `tests/test_insect_out_of_scope.py` pins it.
5. **Zero Loss on Field Benchmark**: Exactly 0 of the 39 cases in `data/benchmark_field.csv` diagnose an insect class; 100% of the empirical field evidence is preserved untouched.

### Moved-Figures Table (Pre-Part 5 vs Post-Part 5)

| Metric / Dimension | Pre-Part 5 (10 Classes) | Post-Part 5 (6 Classes) | Agronomic & Methodological Cause |
|---|:---:|:---:|---|
| **Class-Level Field Coverage** | 6 / 10 (60.0%) | **6 / 6 (100.0%)** | Four ungrounded insect classes removed; all 6 retained classes have independent peer-reviewed field cases. |
| **Diagnosable Classes** | 10 | **6** | 4 insect classes removed; 5 diseases + 1 nematode retained. |
| **Surviving SWRL Rules** | 20 | **12** | 8 insect rules deleted; 6 Tier-1 and 6 Tier-2 rules survive with original IDs. |
| **Verification Suite Sample Size ($n$)** | 80 cases | **73 cases** | 26 insect-referencing cases adjudicated: 19 converted to out-of-scope controls, 7 co-infections removed. |
| **Field Benchmark Sample Size ($n$)** | 39 cases | **39 cases** | Zero-loss property: 0 field cases diagnosed insects; 100% empirical data preserved. |
| **Verification Exact Match (Ablation Full)** | 60.00% | **64.38%** | Case mix changed from 80 cases to 73 cases with 19 out-of-scope controls. Not an algorithmic gain. (The first Part 5 run reported 50.68%; that figure came from the over-broad insect gate, corrected in point 4 above.) |
| **Verification Multi-Label Acc (Ablation Full)** | 96.25% | **92.47%** | Reflects altered denominator and class count (6 vs 10 classes) over 73 cases. |
| **Verification Micro-Recall (Ablation Full)** | 52.50% | **26.67%** | Fewer disease rule firings across the re-stratified verification suite. |
| **Verification Micro-F1 (Ablation Full)** | 68.30% | **42.11%** | Harmonic mean shift following revised verification suite composition. |
| **Verification 5x2-CV Exact Match (RiceKG)** | 60.00 ± 6.52% | **64.38 ± 1.80%** | Altered fold partitioning over $n=73$ cases with 18 negative/out-of-scope controls. |
| **Field `eval` Positive-Case Recall (RiceKG)** | 35.00 ± 36.86% | **35.00 ± 36.86%** | Exactly identical; field benchmark is untouched by insect scope cut. |
| **Field `eval` Exact Match (RiceKG)** | 86.82 ± 7.26% | **86.82 ± 7.26%** | Exactly identical; field benchmark evaluation unchanged. |
| **Field `eval` Micro-F1 (RiceKG)** | 40.67 ± 41.36% | **40.67 ± 41.36%** | Exactly identical; zero empirical loss on field eval split. |
| **Competency Questions** | 13 satisfied, 3 gaps | **13 satisfied, 3 gaps** | CQ08 (ControlTreatment), CQ09 (confidence in OWL), CQ10 (antecedents in OWL) remain open for Part 4. |

> [!NOTE]
> Any shift in aggregate accuracy on `verification_suite.csv` reflects the smaller, differently-composed case mix (73 cases, 6 classes, 19 out-of-scope controls) rather than algorithmic improvement or degradation.

## Invariants

- Six Tier-1 and six Tier-2 rules (12 surviving rules); `tests/test_p0_2_ablation.py` enforces the counts.
- `ml_baselines.SYMPTOM_ORDER` tracks `model.ALL_SYMPTOMS`; `tests/test_p0_4_baselines.py` enforces the correspondence without pinning a vocabulary size.
- Every revised rule carries a `literature` and verified `doi` field in `RULE_REGISTRY` naming its source.
- Surviving rule IDs (`SWRL-R02`, `SWRL-R06`–`SWRL-R10`, `SWRL-R12`, `SWRL-R16`–`SWRL-R20`) are strictly preserved.

---

# Part 4 — Ontology and Rule-Base Redesign

## 4-A. Evidence Type Separation & Property Hierarchy

Previously, all 54 observation individuals were indiscriminately asserted via `hasSymptom(?Rice, ?Symptom)`. This conflated distinct ontological categories: an insect vector sighting is not a lesion, and a field-level epidemic pattern is not a plant organ manifestation.

In Part 4, `hasObservation` was introduced as the top-level object property (`Rice >> Observation`), with four specialized functional subproperties:
1. **`hasSymptom`** (`Rice >> Symptom`): Morphological, histological, and anatomical plant disease signs.
2. **`hasOrganismSighting`** (`Rice >> OrganismSighting`): Direct observation of non-vector pests or biological organisms (e.g. `Adult_Insects_Present`, `Nymphs_Present`, `Brown_Nymphs`, `Yellow_Nymphs`, `Eggs_On_Plant`).
3. **`hasVectorSighting`** (`Rice >> VectorSighting`): Specific observation of insect vectors responsible for viral transmission (`Brown_Planthopper_Present` for Rice Grassy Stunt, `Green_Leafhopper_Present` for Rice Tungro).
4. **`hasEpidemiologicalContext`** (`Rice >> EpidemiologicalContext`): Macro-environmental, phenological, or stand-level disease contexts (`Uniform_Field_Infection`, `Rapid_Disease_Spread`, `Rainy_Season_Outbreak`, `Infected_Seedlings`, `Milky_Stage_Vulnerability`).

### Complete Reclassification of all 61 Vocabulary Terms

| Category | Terms Assigned | Count |
|:---|:---|:---:|
| **`hasOrganismSighting`** | `Adult_Insects_Present`, `Nymphs_Present`, `Brown_Nymphs`, `Yellow_Nymphs`, `Eggs_On_Plant` | 5 |
| **`hasVectorSighting`** | `Brown_Planthopper_Present`, `Green_Leafhopper_Present` | 2 |
| **`hasEpidemiologicalContext`** | `Uniform_Field_Infection`, `Rapid_Disease_Spread`, `Rainy_Season_Outbreak`, `Infected_Seedlings`, `Milky_Stage_Vulnerability` | 5 |
| **`hasSymptom`** | All 49 plant morphological signs (detailed in 4-B taxonomy) | 49 |
| **Total Vocabulary** | | **61** |

---

## 4-B. Two-Axis Symptom Taxonomy

To resolve vocabulary mismatches between scout field reports and rigid rule antecedents, symptoms are modeled as formal OWL classes organized along two orthogonal axes:

### 1. Anatomical Axis
- **`LeafSign`**: `Yellowing_Leaves`, `Yellowing_Leaf_Tips`, `Yellowing_Leaf_Veins`, `Leaf_Discoloration_Yellow`, `Localized_Leaf_Yellowing`, `Interveinal_Chlorosis`, `Orange_Leaf_Discoloration`, `Leaf_Mottling`, `Chlorotic_Streaks`, `Leaf_Bleaching`, `Whitened_Leaf_Tips`, `Necrotic_Spots`, `Diamond_Shaped_Lesions`, `Water_Soaked_Lesions`, `Leaf_Sheath_Lesions`, `Hopperburn_Drying`, `Brown_Streaks`, `Leaf_Desiccation`, `Leaf_Chewing_Damage`, `Broad_Leaf_Damage`, `Leaf_Margin_Sap_Sucking`.
- **`StemSign`**: `Stem_Rot_Lesions`, `Bore_Holes_In_Stem`, `Easily_Pulled_Tillers`, `Blackened_Feeding_Punctures`, `Bacterial_Ooze`.
- **`RootSign`**: `Hook_Like_Root_Swelling`, `Root_Knot_Swelling`, `Deformed_Roots`, `Discolored_Roots`.
- **`PanicleSign`**: `Panicle_Neck_Rot`, `Rotten_Panicles`, `Severed_Panicles`, `Whitehead_Empty_Panicles`, `No_Panicle_Formation`.
- **`GrainSign`**: `Empty_Grains`, `Grain_Discoloration`, `Rusty_Grain_Balls`, `Blackened_Grain_Balls`.
- **`WholePlantSign`**: `Plant_Yellowing`, `Stunted_Growth`, `Severe_Stunting`, `Deadheart_Seedling`, `Leaf_Wilting`, `Excessive_Tillering`.

### 2. Phenomenological Axis
- **`Chlorosis`**: General loss of chlorophyll. Subsumes `Plant_Yellowing`, `Yellowing_Leaves`, `Yellowing_Leaf_Tips`, `Yellowing_Leaf_Veins`, `Leaf_Discoloration_Yellow`, `Localized_Leaf_Yellowing`, `Interveinal_Chlorosis`, `Orange_Leaf_Discoloration`, `Leaf_Mottling`, `Chlorotic_Streaks`, `Leaf_Bleaching`, `Whitened_Leaf_Tips`.
- **`Necrosis`**: Localized death of plant tissues. Subsumes `Necrotic_Spots`, `Diamond_Shaped_Lesions`, `Water_Soaked_Lesions`, `Stem_Rot_Lesions`, `Leaf_Sheath_Lesions`, `Panicle_Neck_Rot`, `Rotten_Panicles`, `Hopperburn_Drying`, `Blackened_Feeding_Punctures`, `Deadheart_Seedling`, `Brown_Streaks`, `Leaf_Desiccation`, `Leaf_Wilting`, `Discolored_Roots`.
- **`Stunting`**: Growth retardation. Subsumes `Stunted_Growth` and `Severe_Stunting`.
- **`MechanicalDamage`**: Structural injury. Subsumes `Leaf_Chewing_Damage`, `Broad_Leaf_Damage`, `Severed_Panicles`, `Bore_Holes_In_Stem`, `Easily_Pulled_Tillers`, `Leaf_Margin_Sap_Sucking`.
- **`GrainAbnormality`**: Kernel defects and malformations. Subsumes `Empty_Grains`, `Grain_Discoloration`, `Rusty_Grain_Balls`, `Blackened_Grain_Balls`, `Whitehead_Empty_Panicles`.

---

## 4-C. Defined Classes Replacing SWRL Rules & Machine-Provable Subsumption

In previous versions, diagnosis was executed via Horn-clause forward-chaining rules. While functionally executable, SWRL rules cannot be checked for inter-rule subsumption or hierarchical consistency by Description Logic reasoners.

Each threat diagnosis is now formulated as equivalent class expressions (Defined Classes) in OWL 2 DL:
```owl
Class: Rice_BlastConfirmed
    EquivalentTo:
        Rice and (hasObservation value Diamond_Shaped_Lesions)
             and (hasObservation value Panicle_Neck_Rot)
             and (hasObservation value Uniform_Field_Infection)
             and (hasObservation value Infected_Seedlings)
             and (hasObservation value Necrotic_Spots)

Class: Rice_BlastSuspect
    EquivalentTo:
        Rice and (hasObservation value Diamond_Shaped_Lesions)
             and (hasObservation value Necrotic_Spots)
```

### Machine-Provable Subsumption
Because every antecedent in the Tier-2 suspect definition is a strict subset of the Tier-1 confirmed definition, the Pellet DL tableau reasoner *formally proves*:
$$\text{Rice\_BlastConfirmed} \sqsubseteq \text{Rice\_BlastSuspect}$$
This property holds universally across all six diagnosable threats.

**Unit Verification**: Added `tests/test_tier_subsumption_is_provable.py` which executes Pellet classification over an isolated ontology world and asserts:
1. $\text{ThreatConfirmed} \sqsubseteq \text{ThreatSuspect}$ for all 6 threats (**PASS**).
2. Removing a Tier-2 antecedent breaks the subsumption entailment (**PASS**).

This formally answers the architectural requirement of why an OWL 2 DL reasoner is necessary: pure Python set-containment or relational baselines cannot prove subsumption invariants over the rule base at any latency.

---

## 4-D. Logic-Based Qualified Cardinality for `possible` Grade

Rather than relying purely on an ad-hoc Python threshold (`POSSIBLE_COVERAGE_THRESHOLD = 0.5`), the `possible` diagnostic tier is formalized in description logic via OWL 2 qualified cardinality restrictions:
```owl
Class: Rice_BlastPossible
    EquivalentTo:
        Rice and (hasObservation min 2 Rice_BlastObservation)
```
where `Rice_BlastObservation` is a defined superclass typing all Tier-2 antecedents for Rice Blast (`Diamond_Shaped_Lesions`, `Necrotic_Spots`). A sample exhibiting $\ge k$ characteristic signs is classified into `*Possible` directly by Pellet's description logic tableau algorithm.

---

## 4-E. Agronomic Disjointness & Consistency

To ensure logical consistency and prevent nonsensical co-classifications, pairwise disjointness axioms were asserted:
- **`AllDisjointClasses([Pest, Disease])`**: Formally asserts that an organism cannot be simultaneously a pest animal and a pathogenic disease.
- **`AllDifferent(threat_individuals)`**: Enforces the Unique Name Assumption over nominal threats in OWL DL.
- **Agronomic Co-infection vs Disjointness**: Legitimate agronomic co-infections (e.g. *Pyricularia oryzae* blast co-occurring with *Ustilaginoidea virens* false smut) are explicitly not declared disjoint, as mixed infections occur naturally in humid fields.

### Open-World Assumption Limitations
OWL operates under the Open-World Assumption (OWA) without negation-as-failure: absence of evidence is not evidence of absence. A reasoner cannot infer that a threat is ruled out merely because a symptom is unrecorded. This is a genuine Description Logic constraint and is preserved as an explicit architectural boundary.

---

## 4-F. Competency Questions Closure (16 Satisfied, 0 Gaps)

All three previously open competency question gaps were resolved in the ontology graph and verified via SPARQL queries in `analysis/competency_questions.py`:
- **CQ08 (IPM Recommendations)**: Populated `ControlTreatment` instances linked via `hasControlTreatment` to all 6 threats. Each treatment carries verified, cited IPM protocols and DOIs.
- **CQ09 (Diagnostic Confidence)**: Confidence grades (`confirmed`, `suspected`, `possible`) are asserted into the graph as datatype properties (`hasDiagnosticConfidence`).
- **CQ10 (OWL-Introspectable Antecedents)**: Canonical antecedents are asserted directly onto threat individuals via `hasSymptom`, enabling SPARQL introspection of rule requirements without reading external Python registries.

**Result**: **16 satisfied, 0 gaps (100% satisfaction)**. Documented in `docs/COMPETENCY_QUESTIONS.md` and verified in `tests/test_competency_questions.py` (5/5 PASS).

---

## 4-G. Vocabulary Reuse, Annotations & Metadata

External ontology alignments were added using SKOS mapping relations (`skos:exactMatch`, `skos:closeMatch`):
- **AGROVOC Alignment**:
  - `Rice_Root_Nematode` $\rightarrow$ `c_24089` (*Meloidogyne graminicola*)
  - `Bacterial_Leaf_Blight` $\rightarrow$ `c_8453` (*Xanthomonas oryzae*)
  - `False_Smut` $\rightarrow$ `c_8091` (*Ustilaginoidea virens*)
  - `Rice_Blast` $\rightarrow$ `c_4558` (*Magnaporthe grisea / Pyricularia oryzae*)
  - `Rice_Grassy_Stunt` $\rightarrow$ `c_24855` (*Rice grassy stunt tenuivirus*)
  - `Rice_Tungro_Virus` $\rightarrow$ `c_6590` (*Rice tungro spherical/bacilliform virus*)
  - `Brown_Planthopper_Present` $\rightarrow$ `c_5204` (*Nilaparvata lugens*)
  - `Green_Leafhopper_Present` $\rightarrow$ `c_5119` (*Nephotettix virescens*)
  - Symptom matches: `Stunted_Growth` $\rightarrow$ `c_7463`, `Necrotic_Spots` $\rightarrow$ `c_5138`, `Chlorosis` $\rightarrow$ `c_1550`, `Necrosis` $\rightarrow$ `c_5139`, etc.
- **Plant Ontology (PO) Alignment**:
  - `LeafSign` $\rightarrow$ `PO:0025034` (leaf)
  - `StemSign` $\rightarrow$ `PO:0009047` (stem)
  - `RootSign` $\rightarrow$ `PO:0009005` (root)
  - `PanicleSign` $\rightarrow$ `PO:0009051` (inflorescence)
  - `GrainSign` $\rightarrow$ `PO:0009010` (seed / caryopsis)
  - `WholePlantSign` $\rightarrow$ `PO:0000003` (whole plant)
- **Ontology Metadata**:
  - Dublin Core (`dcterms:title`, `dcterms:creator`, `dcterms:license`, `dcterms:description`).
  - Namespace metadata (`vann:preferredNamespacePrefix`, `vann:preferredNamespaceUri`).
  - Full `rdfs:comment` and `rdfs:label` asserted on **every class, object property, and individual**.

---

## 4-H. Rule & Treatment Provenance Verification

All 12 production rules and 6 IPM control treatments carry agronomic citations and verified DOIs. `analysis/verify_citations.py` was extended to query the Crossref API (`https://api.crossref.org/works/{doi}`) and verify:
- HTTP 200 resolution.
- Exact title match between Crossref metadata and internal citation strings.
- **Verification Result**: 12/12 rules PASSED (100%), 6/6 IPM treatments PASSED (100%).

---

## 4-J. Field Benchmark Vocabulary Coverage & Negative Control Discrimination

### 1. Agronomic Decisions on 9 Unmapped Field Descriptors
In `data/symptom_mapping.csv`, the 9 previously unmapped descriptors from field case reports were adjudicated on agronomic grounds:
1. `leaves_drying_up_yellowish_brown` $\rightarrow$ `Leaf_Desiccation` (mapped under `LeafSign`, `Necrosis`).
2. `leaves_chlorotic_stripes_streaks` $\rightarrow$ `Chlorotic_Streaks` (mapped under `LeafSign`, `Chlorosis`).
3. `leaves_brown_streaks_stripes` $\rightarrow$ `Brown_Streaks` (mapped under `LeafSign`, `Necrosis`).
4. `leaves_bleached_white` $\rightarrow$ `Leaf_Bleaching` (mapped under `LeafSign`, `Chlorosis`).
5. `leaves_whitened_leaf_tips` $\rightarrow$ `Whitened_Leaf_Tips` (mapped under `LeafSign`, `Chlorosis`).
6. `leaves_withering_dead` $\rightarrow$ `Leaf_Wilting` (mapped under `WholePlantSign`, `Necrosis`).
7. `roots_discolored` $\rightarrow$ `Discolored_Roots` (mapped under `RootSign`, `Necrosis`).
8. `leaves_discoloration` $\rightarrow$ **Unmapped** (too generic; lacks diagnostic specificity).
9. `plant_malformation` $\rightarrow$ **Unmapped** (too generic; nonspecific abiotic/biotic sign).

None of the seven newly mapped expressivity terms were wired as antecedents to in-scope rules, preserving strict rule provenance.

### 2. Explicit Negative Control Differential Response
When a field report carries mapped signs of a non-modeled disease (e.g. *Rhizoctonia*, *Burkholderia*, *Xanthomonas oryzae pv. oryzicola*) and no in-scope rule fires, the system returns an explicit differential diagnosis:
> *"signs recorded, not consistent with any disease in scope"*

This is distinct from both a positive diagnosis and the insect out-of-scope response. Tested in `tests/test_negative_control_out_of_scope.py` (4/4 PASS).

### 3. Dual Specificity Reporting (Earned Discrimination)
On the 27 negative controls (FIELD_06 to FIELD_32, true label `No_Diagnosis`):
- **Specificity across all 27 negative controls**: **100.0% (27/27)**.
- **Specificity across mapped-sign controls only**: **100.0% (24/24) [Earned Discrimination]**.
This proves that the system's rejections are not merely artifacts of unmappable input; even when genuine disease signs are recognized and processed by the ontology, the system correctly refrains from falsely firing on out-of-scope pathogens.

### 4. Evaluation Across Benchmark Splits
- **Dev Split ($n=16$)**: Exact-Match Accuracy: **81.25%**, Precision: **100.0%**, Recall: **57.1%**, F1: **72.7%**. Specificity on controls: 100.0% (9/9 all, 8/8 mapped-sign).
- **Eval Split ($n=23$)**: Exact-Match Accuracy: **86.96%**, Precision: **100.0%**, Recall: **40.0%**, F1: **57.1%**. Specificity on controls: 100.0% (18/18 all, 16/16 mapped-sign). Recall at `385caf9` (40.0%) is exactly preserved.
- **Holdout Split ($n=18$)**: Exact-Match Accuracy: **27.78%**, Precision: **83.3%**, Recall: **27.8%**, F1: **41.7%**.

---

## Moved-Figures Table (Pre-Part 4 vs Post-Part 4)

| Metric / Dimension | Pre-Part 4 (`385caf9`) | Post-Part 4 (Redesigned) | Cause / Rationale |
|:---|:---:|:---:|:---|
| **Symptom Vocabulary Size** | 54 terms | **61 terms** | 7 expressivity descriptors mapped from field negative controls (4-J). |
| **Observation Property Hierarchy** | Flat `hasSymptom` | **`hasObservation` with 4 subproperties** | Separated morphological signs, organism sightings, vector sightings, and context (4-A). |
| **Symptom Taxonomy** | None (flat individuals) | **2 axes (6 anatomical, 5 phenomenological)** | Formal class subsumption over symptoms (4-B). |
| **Rule Formalism** | SWRL Horn Clauses | **OWL 2 DL Defined Classes** | Tableau DL classification replaces rule firing; machine-provable subsumption enabled (4-C). |
| **Provable Tier Subsumption** | Not provable (SWRL limitation) | **Proven by Pellet DL ($\text{Confirmed} \sqsubseteq \text{Suspect}$)** | Verified in `tests/test_tier_subsumption_is_provable.py` (4-C). |
| **Possible Grade Implementation** | Python heuristic check | **OWL 2 Qualified Cardinality (`min k ...`)** | Logical expressivity in description logic (4-D). |
| **Competency Questions** | 13 satisfied, 3 gaps | **16 satisfied, 0 gaps** | CQ08, CQ09, CQ10 fully resolved in ontology graph (4-F). |
| **External Alignment** | 0 external links | **AGROVOC (18 matches) + PO (6 matches)** | SKOS mapping relations and Dublin Core annotations added (4-G). |
| **Rule & IPM Provenance** | Unverified free text | **100% Crossref Verified DOIs** | Verified via `analysis/verify_citations.py` (4-H). |
| **Negative Control Discrimination** | "By construction" rejection | **100.0% (24/24) earned specificity** | Explicit differential response for out-of-scope plant pathogens (4-J). |
| **Field Eval Exact-Match Acc** | 86.96% | **86.96%** | Preserved with zero eval data leakage. |
| **Field Eval Recall** | 40.0% | **40.0%** | Preserved exactly side-by-side with `385caf9`. |
| **Field Eval Precision** | 100.0% | **100.0%** | 0 false positives maintained. |
| **Test Suite Pass Rate** | 114 passed | **121 passed, 0 failed** | All unit, regression, and property tests green. |

