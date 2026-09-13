# Per-Case Failure Diagnosis: Positive Field Benchmark Cases

> **Evaluation Target**: `data/benchmark_field.csv` ($n=32$ total cases: 5 positive disease cases, 27 negative control / out-of-scope cases).  
> **Observed Finding**: RiceKG produces 0 true positives out of 5 positive cases (micro-F1: 0.00, 95% CI: [0.0, 0.0], Exact Match on positive subset: 0.0%).  
> **Diagnostic Distinction**:
> - **Vocabulary gating**: The case's symptoms never map into RiceKG's closed 45-term vocabulary (`model.ALL_SYMPTOMS`). As a result, the 45-dimensional binary feature vector is all-zeros, the reasoner receives an empty input individual, and no rules can fire. The required remedy is vocabulary expansion / ontology mapping.
> - **Rule failure**: The symptoms successfully map into the vocabulary, but no Tier-1 or Tier-2 Horn clause fires (or a rule for an incorrect threat fires). The required remedy is rule revision or relaxation.

---

## Summary Matrix

| Case ID | Raw Symptom Text | Terms Successfully Mapped | Terms Dropped / Unmapped | Rules Fired | Predicted Label | True Label | Assigned Failure Cause |
|---|---|---|---|---|---|---|---|
| **FIELD_01** | "A leaf spot symptom initially appeared as grey-green and/or water soaked with a darker green border and then expanded rapidly to several centimeters in length and became light tan in color with a distinct necrotic border." | *None* (`[]`) | `leaves_spots_infestation`, `leaves_water_soaked_stripes`, `leaves_discoloration` | *None* | `No_Diagnosis` | `Rice_Blast` | **Vocabulary gating** |
| **FIELD_02** | "Symptoms observed in commercial fields during September and October consisted mainly of darkened lesions at the panicle neck node and flag leaf collar. Many of the panicles with neck rot were partially filled or blank." | *None* (`[]`) | `leaves_spots_infestation`, `stem_rot_or_break`, `seed_empty_unfilled` | *None* | `No_Diagnosis` | `Rice_Blast` | **Vocabulary gating** |
| **FIELD_03** | "Typical symptoms were characterized by yellow to grayish, water-soaked lesions that start from the leaf tip and progress along the central vein or leaf margin. At an advanced stage of the disease, the leaves were completely desiccated sometimes with droplets of yellow exudate at the leaf margin." | *None* (`[]`) | `leaves_water_soaked_stripes`, `leaves_drying_up_yellowish_brown`, `leaves_yellowing`, `leaves_bacterial_ooze_droplet` | *None* | `No_Diagnosis` | `Bacterial_Leaf_Blight` | **Vocabulary gating** |
| **FIELD_04** | "Galls and hooked tips were found in the roots of rice seedlings and plants." | *None* (`[]`) | `roots_hook_shaped_galls`, `leaves_yellowing`, `plant_stunted_short` | *None* | `No_Diagnosis` | `Rice_Root_Nematode` | **Vocabulary gating** |
| **FIELD_05** | "A few spikelets in a panicle transform into globose, yellowish green, velvety spore balls that are 2 to 5 cm in diameter and covered by a thin orange membrane. The membrane bursts open and releases powdery dark green spores." | *None* (`[]`) | `seed_yellowish_green_velvety_balls`, `seed_dark_green_spores_powder` | *None* | `No_Diagnosis` | `False_Smut` | **Vocabulary gating** |

---

## Detailed Per-Case Analysis

### FIELD_01 (`Rice_Blast`)
- **Citation**: You et al. (2012). *First Report of Rice Blast (Magnaporthe oryzae) on Rice (Oryza sativa) in Western Australia.* Plant Disease, 96(8): 1228. DOI: [10.1094/pdis-05-12-0420-pdn](https://doi.org/10.1094/pdis-05-12-0420-pdn).
- **Target Disease**: Rice Blast (*Magnaporthe oryzae*).
- **Input Symptoms in Benchmark CSV**: `leaves_spots_infestation`, `leaves_water_soaked_stripes`, `leaves_discoloration`.
- **Ontology Alignment**: None of the three recorded terms exist in `model.ALL_SYMPTOMS`. The canonical RiceKG blast rules (`SWRL-R08` and `SWRL-R18`) require `Panicle_Neck_Rot` and `Diamond_Shaped_Lesions`. Although the raw text describes spindle lesions ("expanded rapidly... light tan in color with a distinct necrotic border"), the terms were recorded in free-text draft strings.
- **Reasoner State**: Zero ontology properties asserted on the plant individual. No SWRL rules activated.
- **Predicted**: `No_Diagnosis` (0 TP, 1 FN).
- **Failure Cause**: **Vocabulary gating**.

### FIELD_02 (`Rice_Blast`)
- **Citation**: Greer et al. (1997). *First Report of Rice Blast Caused by Pyricularia grisea in California.* Plant Disease, 81(9): 1094. DOI: [10.1094/pdis.1997.81.9.1094a](https://doi.org/10.1094/pdis.1997.81.9.1094a).
- **Target Disease**: Rice Blast (*Magnaporthe oryzae* / *Pyricularia grisea*).
- **Input Symptoms in Benchmark CSV**: `leaves_spots_infestation`, `stem_rot_or_break`, `seed_empty_unfilled`.
- **Ontology Alignment**: RiceKG defines `Panicle_Neck_Rot` and `Empty_Grains` in `model.ALL_SYMPTOMS`, but the CSV recorded `stem_rot_or_break` and `seed_empty_unfilled`. Zero terms mapped to the closed vocabulary.
- **Reasoner State**: Zero ontology properties asserted. No SWRL rules activated.
- **Predicted**: `No_Diagnosis` (0 TP, 1 FN).
- **Failure Cause**: **Vocabulary gating**.

### FIELD_03 (`Bacterial_Leaf_Blight`)
- **Citation**: Raveloson et al. (2023). *First Report of Bacterial Leaf Blight Disease of Rice Caused by Xanthomonas oryzae pv. oryzae in Madagascar.* Plant Disease, 107(8): 2510. DOI: [10.1094/pdis-03-23-0411-pdn](https://doi.org/10.1094/pdis-03-23-0411-pdn).
- **Target Disease**: Bacterial Leaf Blight (*Xanthomonas oryzae* pv. *oryzae*).
- **Input Symptoms in Benchmark CSV**: `leaves_water_soaked_stripes`, `leaves_drying_up_yellowish_brown`, `leaves_yellowing`, `leaves_bacterial_ooze_droplet`.
- **Ontology Alignment**: Canonical BLB rules (`SWRL-R06` and `SWRL-R16`) require `Yellowing_Leaf_Veins`, `Uniform_Field_Infection`, `Yellowing_Leaf_Tips`, and `Rapid_Disease_Spread`. None of the four CSV symptoms match `model.ALL_SYMPTOMS`.
- **Reasoner State**: Zero ontology properties asserted. No SWRL rules activated.
- **Predicted**: `No_Diagnosis` (0 TP, 1 FN).
- **Failure Cause**: **Vocabulary gating**.

### FIELD_04 (`Rice_Root_Nematode`)
- **Citation**: Xie et al. (2019). *First Report of Root-Knot Nematode, Meloidogyne graminicola, on Rice in Sichuan Province, Southwest China.* Plant Disease, 103(8): 2142. DOI: [10.1094/pdis-03-19-0502-pdn](https://doi.org/10.1094/pdis-03-19-0502-pdn).
- **Target Pest**: Rice Root Nematode (*Meloidogyne graminicola* / *Hirschmanniella* spp.).
- **Input Symptoms in Benchmark CSV**: `roots_hook_shaped_galls`, `leaves_yellowing`, `plant_stunted_short`.
- **Ontology Alignment**: RiceKG defines `Hook_Like_Root_Swelling`, `Root_Knot_Swelling`, `Yellowing_Leaves`, and `Stunted_Growth`. However, the recorded terms `roots_hook_shaped_galls` and `plant_stunted_short` do not match the ontology identifiers verbatim.
- **Reasoner State**: Zero ontology properties asserted. No SWRL rules activated.
- **Predicted**: `No_Diagnosis` (0 TP, 1 FN).
- **Failure Cause**: **Vocabulary gating**.

### FIELD_05 (`False_Smut`)
- **Citation**: Rush et al. (2000). *Outbreak of False Smut of Rice in Louisiana.* Plant Disease, 84(1): 100. DOI: [10.1094/pdis.2000.84.1.100d](https://doi.org/10.1094/pdis.2000.84.1.100d).
- **Target Disease**: False Smut (*Ustilaginoidea virens*).
- **Input Symptoms in Benchmark CSV**: `seed_yellowish_green_velvety_balls`, `seed_dark_green_spores_powder`.
- **Ontology Alignment**: RiceKG False Smut rules (`SWRL-R07` and `SWRL-R17`) require `Rusty_Grain_Balls` and `Blackened_Grain_Balls`. Neither recorded CSV symptom matches `model.ALL_SYMPTOMS`.
- **Reasoner State**: Zero ontology properties asserted. No SWRL rules activated.
- **Predicted**: `No_Diagnosis` (0 TP, 1 FN).
- **Failure Cause**: **Vocabulary gating**.

---

## Architectural Implication
In 5 out of 5 positive field cases, failure is strictly attributable to **Vocabulary gating**, not rule failure. When real-world literature cases are imported, any divergence in nomenclature prevents symptoms from mapping into the closed 45-term vocabulary. The reasoner operates on an empty input graph, deterministically returning `No_Diagnosis`.

Consequently, the high aggregate exact match reported on the field benchmark (27/32, 84.38%) is entirely an artifact of correctly returning `No_Diagnosis` on the 27 negative control cases. On genuine positive disease cases, the true-positive rate of the unmapped pipeline is **0/5 (0.0%)**.
