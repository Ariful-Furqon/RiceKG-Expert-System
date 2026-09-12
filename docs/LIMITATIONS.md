# System Limitations & Diagnostic Architectural Findings

## 1. Description Logic Subsumption and Rejection of Probabilistic Calibration Claim

### The Architectural Problem
In the initial engineering of RiceKG, SWRL rules were stratified into two layers:
- **Tier 1 (Canonical / Pathognomonic)**: High-cardinality antecedent sets ($4 \le |S| \le 7$ symptoms).
- **Tier 2 (Relaxed Composite)**: Low-cardinality antecedent sets ($2 \le |S| \le 3$ symptoms), where the Tier-2 antecedents formed a strict subset of Tier 1:
  $$\text{Ant}(R_{\text{tier2}}) \subset \text{Ant}(R_{\text{tier1}})$$

Under classical first-order Horn-clause semantics, asserting the same predicate $\text{hasThreat}(?Rice, T)$ causes Tier 1 to be logically redundant:
$$\forall \text{Rice Sample } x, \quad \text{fires}(R_{\text{tier1}}, x) \implies \text{fires}(R_{\text{tier2}}, x)$$
Tier 1 never altered the inferred extension of diagnosed threats beyond Tier 2 alone.

### Out-of-Sample Calibration Analysis & Rejection of Calibration Claim
To resolve this, RiceKG introduced distinct subproperties (`hasConfirmedThreat` vs `hasSuspectedThreat` ⊑ `hasThreat`). When evaluating whether this stratification yields probabilistic calibration:

1. **In-Sample Train-on-Test Flaw**: Initial internal evaluations assigned $p = 1.000$ for confirmed and $p = 0.9714$ for suspected. However, $0.9714$ was the empirical precision calculated across the entire test set ($68 / 70$). Evaluating Brier score on the same data that yielded the parameters constituted a train-on-test circularity that reported a cosmetic 0.95% reduction ($0.007500 \to 0.007429$).
2. **Out-of-Sample Cross-Validation**: When evaluated under stratified 5-fold cross-validation where $\hat{p}(\text{confirmed})$ and $\hat{p}(\text{suspected})$ are estimated strictly on $k-1$ training folds and evaluated on held-out folds:
   - **Out-of-Sample Brier (Flat Binary)**: `0.007500`
   - **Out-of-Sample Brier (Stratified Graded)**: `0.007479`
   - **Brier Reduction**: `+0.000021` (`0.28%` reduction).
   - **Non-Parametric Bootstrap 95% Confidence Intervals** ($B = 1000$):
     - $\hat{p}(\text{Confirmed})$: point estimate `1.0000` [95% CI: `1.0000`, `1.0000`]
     - $\hat{p}(\text{Suspected})$: point estimate `0.9714` [95% CI: `0.9285`, `1.0000`]
3. **Formal Rejection of Calibration Claim**: Because the 95% bootstrap CI for $\hat{p}(\text{Suspected})$ includes `1.0000` and the out-of-sample Brier reduction is functionally indistinguishable from zero ($0.000021$), **we explicitly reject the claim that SWRL rule stratification provides probabilistic calibration**. The system is a deterministic deductive reasoner, not a calibrated probabilistic classifier.

### True Role of Multi-Tier Stratification: Epistemic Specificity vs. Screening Sensitivity
The valid scientific contribution of the multi-tier architecture is qualitative and epistemic, not probabilistic:
- **Tier 1 (Pathognomonic Specificity)**: Guarantees **100.00% precision with zero false discoveries** ($FP = 0$). When all canonical symptoms are observed, the diagnosis is definitively verified.
- **Tier 2 (Actionable Screening Sensitivity)**: Expands diagnostic recall from 10.0% to 95.0% under incomplete or early-stage field scouting, at the cost of rare false discoveries ($FP = 2$, precision $97.14\%$).

---

## 2. Evaluation Set Circularity and Independent Field Benchmark Reconstruction

### The Circularity Defect of `benchmark_synthetic.csv`
The initial benchmark file `data/benchmark_synthetic.csv` (80 test instances, formerly `dataText.csv`) was authored by the knowledge engineering team from the same SWRL rule antecedents that the reasoner executes:
1. **Ceiling Bias**: Multi-label accuracy of 99.25% and exact-match accuracy of 92.50% reflect deductive rule verification, not empirical diagnostic efficacy on real-world crops.
2. **Data Provenance Disclosure**: In accordance with scientific integrity standards, `data/README.md` classifies `benchmark_synthetic.csv` as `provenance: rule_derived`.

### Remediation: Rebuilding `benchmark_field.csv` from Peer-Reviewed Disease Notes
To eliminate circularity, `data/benchmark_field.csv` was completely reconstructed ($n=32$) from primary peer-reviewed phytopathology case literature:
- **Primary Sources**: APS *Plant Disease* ("Disease Notes" section), BSPP *New Disease Reports*, and peer-reviewed journals (*Crop Protection*, *Insects*, *Plant and Soil*, *Field Crops Research*).
- **Exclusion of IRRI Rice Doctor**: Because the ontology's 45 controlled vocabulary terms were historically derived from IRRI Rice Doctor diagnostic profiles, sourcing independent test cases from IRRI would perpetuate vocabulary and definition circularity. Sourcing was strictly restricted to primary phytopathology literature with laboratory-confirmed pathogen identification (PCR, sequencing, pathogenicity tests, microscopic spore morphology).
- **Mandatory Two-Stage Protocol**:
  - **Stage A (Data Extraction & Provenance Audit)**: Each case records the `raw_symptom_text` copied **verbatim** from the original publication, alongside the authentic `location`, `observation_date`, `ground_truth_method` (`lab_confirmed` / `literature_case`), `citation`, and verified `doi`. No symptom columns were filled during this stage. No dates, locations, or DOIs were fabricated.
  - **Stage B (Controlled Vocabulary Mapping)**: `raw_symptom_text` was mapped into the 45-term controlled vocabulary independently without inspecting SWRL rule definitions or `model.py` code. The verbatim `raw_symptom_text` remains in the CSV as an immutable audit trail.
- **Benchmark Sample Composition** ($n=32$):
  - **In-Scope Threat Classes** ($n=19$, 59.4%): Distributed across all 10 ontology threat classes (Rice Blast, Bacterial Leaf Blight, False Smut, Rice Root Nematode, Rice Stem Borer, Brown Planthopper, Rice Bug, Grasshopper, Rice Grassy Stunt, Rice Tungro Virus).
  - **Out-of-Scope Pathogens** ($n=7$, 21.9%): Confirmed phytopathogenic infections outside the 10 modeled classes (*Burkholderia glumae*, *Burkholderia gladioli*, *Sarocladium oryzae*, *Rice hoja blanca virus*, *Tilletia horrida*, *Pantoea ananatis*, *Fusarium andiyazi*), assigned ground-truth `No_Diagnosis`.
  - **Abiotic & Nutrient Stress Mimics** ($n=6$, 18.8%): Abiotic conditions that visually mimic infectious foliar diseases (Zinc deficiency, Iron toxicity, Nitrogen deficiency, Drought stress, Salinity stress), assigned ground-truth `No_Diagnosis`.

---

## 3. Ontological Scope and Controlled Vocabulary Coverage Bottleneck

An explicit scientific finding of the Stage B vocabulary mapping protocol is the **Controlled Vocabulary Coverage Bottleneck**:
- **100% Information Loss Across Real-World Cases**: For all 32 independent cases (100.0%), the authoring literature reported diagnostic clinical manifestations that **could not be represented** within the ontology's 45 symptom terms.
- **Critical Anatomical Omission (`Leaf_Sheath`)**:
  - The RiceKG ontology defines symptoms on `Leaf`, `Panicle`, `Stem`, and `Root`, but contains **no anatomical concept for `Leaf_Sheath`**.
  - As a direct consequence, major rice diseases such as Sheath Rot (*Sarocladium oryzae*) and Sheath Blight (*Rhizoctonia solani*) cannot be syntactically described. In case `FIELD_22` (*Sarocladium oryzae*), lesions on the flag leaf sheath had to be mapped to general foliar `Necrotic_Spots` or dropped entirely.
- **Absence of Abiotic Stress Phenotypes**:
  - The vocabulary contains zero terms for characteristic abiotic stress responses: `Leaf_Rolling` (drought), `Bronzing` / `Brown_Spots_Interveinal` (zinc deficiency, iron toxicity), or `Marginal_Leaf_Scorch` (salinity).
  - Consequently, abiotic mimics can only be entered as non-diagnostic general symptoms (e.g., `Yellowing_Leaves`, `Stunted_Growth`) or complete non-entries.
- **Absence of Diagnostic Panicle/Grain Lesions**:
  - Key grain symptoms such as `Glume_Discoloration`, `Powdery_Sooty_Spore_Masses` (kernel smut), and `Chaffy_Empty_Spikelets` are missing.
  - In case `FIELD_24` (*Tilletia horrida* / Kernel Smut), **zero symptoms (0/45) could be mapped** into the vocabulary, because the symptom description ("black spore mass bursting from glumes") has no ontological counterpart.

---

## 4. Field Performance, Sampling Bias, and Deductive Specificity Gating

When evaluated on the independent peer-reviewed benchmark (`benchmark_field.csv`, $n=32$) using Pellet DL reasoner:
- **Multi-Label Accuracy**: **99.38%**
- **Exact-Match Case Accuracy**: **93.75%** (30/32 cases)
- **Micro-Average Precision**: **100.0%** (17 TP, 0 FP)
- **Micro-Average Recall**: **89.5%** (17 TP, 2 FN)
- **Micro-Average F1-Score**: **94.4%**

### Error Analysis (False Negatives)
Two in-scope cases were missed by the reasoner (`FN = 2`):
1. **Case `FIELD_03` (Rice Blast on wild rice)**: Sourced from *Plant Disease* (DOI: 10.1094/PDIS-04-14-0338-PDN). Verbatim symptoms included eye-shaped necrotic lesions rapidly spreading across plots. The mapped symptoms (`Diamond_Shaped_Lesions`, `Necrotic_Spots`, `Rapid_Disease_Spread`) lacked `Panicle_Neck_Rot` or `Gray_Spore_Mass`, which are mandatory in both Tier 1 and Tier 2 SWRL rules. The reasoner inferred `No_Diagnosis`.
2. **Case `FIELD_19` (Rice Tungro Virus)**: Sourced from *New Disease Reports* (DOI: 10.5197/j.2044-0588.2016.034.004). Foliar symptoms described yellow-orange leaf discoloration and severe stunting. Mapped symptoms (`Orange_Yellow_Leaves`, `Stunted_Growth`) failed to satisfy Tier-2 Tungro rules, which require either `Mottled_Grain` or `Rusty_Spots` alongside leaf chlorosis.

### Honest Declaration of Sampling Bias
> [!WARNING]
> While RiceKG achieved 100.0% precision (0 false positives on out-of-scope pathogens and abiotic mimics), **this near-ceiling specificity must be acknowledged as an artifact of sampling bias and rigid Horn-clause conjunctions**.
>
> In a closed-world DL reasoner, rules fire only when strict conjunctions of 2 to 7 specific concepts are satisfied. Because out-of-scope pathogens (*B. glumae*, *P. ananatis*, *T. horrida*) and abiotic disorders (nitrogen deficiency, drought) do not express the exact conjunctions required for the 10 target threats, the system safely defaults to `No_Diagnosis`.
>
> However, in open-field agricultural scouting, unmodeled co-morbidities, secondary opportunistic saprophytes, and atypical symptom complexes frequently present ambiguous or overlapping features. Claiming that RiceKG has "100% field precision" would be scientifically misleading. We report these figures with full disclosure of the sample size ($n=32$), the curated nature of the literature case series, and the rigid conjunct requirements of SWRL rules.
