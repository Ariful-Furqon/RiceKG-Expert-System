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

## Invariants

- Ten Tier-1 and ten Tier-2 rules; `tests/test_p0_2_ablation.py` enforces the counts.
- `ml_baselines.SYMPTOM_ORDER` tracks `model.ALL_SYMPTOMS`; `tests/test_p0_4_baselines.py`
  enforces the correspondence without pinning a vocabulary size.
- Every revised rule carries a `literature` field in `RULE_REGISTRY` naming its source.
