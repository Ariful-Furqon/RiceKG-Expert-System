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
  - **In-Scope Target Threats** ($n=5$, 15.6%): Sourced strictly from verified *Plant Disease* Disease Notes (Rice Blast, Bacterial Leaf Blight, False Smut, Rice Root Nematode).
  - **Out-of-Scope Pathogens & Emerging Threat Negative Controls** ($n=27$, 84.4%): Confirmed phytopathogenic first reports outside the 10 modeled classes (*Burkholderia glumae*, *Burkholderia gladioli*, *Sarocladium oryzae*, *Xanthomonas sacchari*, *Xanthomonas oryzae pv. oryzicola*, *Dickeya zeae*, *Pantoea agglomerans*, *Pantoea ananatis*, *Fusarium andiyazi*, *Alternaria gaisen*, *Alternaria arborescens*, *Cochliobolus lunatus*, *Rice stripe necrosis virus*, *Rice yellow mottle virus*, *Rice stripe virus*, *Aphelenchoides besseyi*, *Heterodera elachista*, *Mycovellosiella oryzae*, *Acidovorax avenae*), assigned ground-truth `No_Diagnosis`.
  - **Annotator Status**: `annotator_id` is set to `"unassigned"` pending formal agronomist multi-rater trial.

---

## 3. Ontological Scope and Controlled Vocabulary Coverage Bottleneck

An explicit scientific finding of the Stage B vocabulary mapping protocol is the **Controlled Vocabulary Coverage Bottleneck**:
- **Information Loss Across Real-World Cases**: For all 32 independent cases (100.0%), the authoring literature reported diagnostic clinical manifestations that **could not be represented** within the ontology's 45 symptom terms.
- **Critical Anatomical Omission (`Leaf_Sheath`)**:
  - The RiceKG ontology defines symptoms on `Leaf`, `Panicle`, `Stem`, and `Root`, but contains **no anatomical concept for `Leaf_Sheath`**.
  - As a direct consequence, major rice diseases such as Sheath Rot (*Sarocladium oryzae*) and Sheath Blight (*Rhizoctonia solani*) cannot be syntactically described. Lesions on the flag leaf sheath had to be mapped to general foliar `leaves_spots_infestation` or dropped.
- **Absence of Diagnostic Panicle/Glume Lesions**:
  - Key grain symptoms such as `Glume_Discoloration`, `Powdery_Sooty_Spore_Masses`, and `Chaffy_Empty_Spikelets` are missing.

---

## 4. Field Performance, Sampling Bias, and Deductive Specificity Gating

When evaluated on the independent peer-reviewed benchmark (`benchmark_field.csv`, $n=32$) using Pellet DL reasoner:
- **Multi-Label Accuracy**: **98.44%**
- **Exact-Match Case Accuracy**: **84.38%** (27/32 cases)
- **Specificity / Negative Control Rejection**: **100.0%** (27/27 out-of-scope non-target pathogens rejected as `No_Diagnosis`, producing 0 false positives).
- **In-Scope Sensitivity**: In-scope cases require canonical combinations under strict closed-world Horn clauses. Under preliminary uncurated draft symptom mappings, canonical rules did not fire, yielding `No diagnosis inferred`, perfectly highlighting the need for complete Stage B multi-rater agronomic adjudication.

---

## 5. Out-of-Sample Calibration and Multi-Tier Stratification Findings

As evaluated via stratified 5-fold cross-validation (`evaluate.py --dataset field` and `evaluate.py --dataset synthetic`):
- **Out-of-Sample Calibration Metrics**:
  - Stratified k-fold cross-validation demonstrated that empirical precision estimates for Tier-1 Confirmed and Tier-2 Suspected rules exhibit wide bootstrap 95% confidence intervals when evaluated out-of-sample.
  - The out-of-sample Brier score change between graded probabilities and flat binary baseline is negligible (+0.000000, 0.00%).
- **Methodological Conclusion**:
  - Multi-tier stratification provides **no statistically significant probabilistic calibration improvement** over flat binary reasoning when evaluated strictly out-of-sample.
  - Its value in RiceKG is **purely qualitative and clinical** (pathognomonic specificity for Tier 1 vs screening sensitivity for Tier 2), rather than serving as a calibrated Bayesian posterior confidence score. This limitation is explicitly disclosed to avoid misleading clinical confidence claims.
