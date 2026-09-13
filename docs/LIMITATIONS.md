# System Limitations & Diagnostic Architectural Findings

## 1. Zero True-Positive Diagnostic Recall on Independent Field Cases (0/5 Cases, 0.0% Recall)

On the independent, peer-reviewed literature benchmark (`data/benchmark_field.csv`, $n=32$), RiceKG achieves **0 out of 5 true positives** on confirmed positive disease cases:
- **Positive-Case Diagnostic Recall**: **0.0%** ($0/5$ cases correctly diagnosed).
- **Micro-Averaged F1-Score**: **0.00** [95% non-parametric bootstrap CI: `0.0`, `0.0`].
- **Micro-Precision / Micro-Recall**: **0.0% / 0.0%** across all positive instances.

### Diagnostic Failure Diagnosis: Closed-Vocabulary Gating
As comprehensively analyzed per-case in [`results/field_failure_analysis.md`](../results/field_failure_analysis.md), the 0/5 failure across all positive field cases is attributable to **vocabulary gating**, not deductive rule failure:
- In all 5 positive cases (`FIELD_01` and `FIELD_02` Rice Blast, `FIELD_03` Bacterial Leaf Blight, `FIELD_04` Rice Root Nematode, `FIELD_05` False Smut), the clinical symptoms extracted verbatim from APS *Plant Disease* Disease Notes could not be mapped into RiceKG's closed 45-term controlled vocabulary (`model.ALL_SYMPTOMS`).
- Because no input symptoms mapped to ontology terms, the 45-dimensional binary feature vector was all-zeros for every case. The DL reasoner received an empty symptom assertion set, preventing both Tier-1 canonical and Tier-2 relaxed Horn clauses from activating.
- Consequently, the reasoner deterministically output `No_Diagnosis` (all-zeros).
- **Critical Distinction**: The system's rules are not logically unsound, but they are inaccessible in real-world clinical contexts without an intervening flexible semantic translation or open-vocabulary mapping layer. Diagnostic efficacy on independent field cases is **currently unproven**.

---

## 2. Benchmark Composition Imbalance and Sample Power Constraints

### The 84.4% Negative Control Composition Defect
A major design limitation of the P0-3 independent benchmark (`data/benchmark_field.csv`) is its extreme class imbalance:
- **Total Cases**: $n = 32$.
- **Positive In-Scope Disease Cases**: $n = 5$ (15.6%).
- **Negative Control / Out-of-Scope Pathogen Cases**: $n = 27$ (84.4%).

Because 84.4% of the benchmark consists of negative controls (confirmed emerging pathogens outside the 10 modeled classes, such as *Burkholderia glumae*, *Sarocladium oryzae*, and *Rice stripe necrosis virus*), the reported **84.38% aggregate exact match is an artifact of negative-control rejection**. Defaulting to `No_Diagnosis` correctly matches 27/27 negative controls while simultaneously failing on 5/5 positive disease cases. Reporting aggregate exact match without segregating positive-case recall conceals complete diagnostic failure on actual disease targets.

### Requirements for a Properly Powered Field Benchmark
The current field sample ($n=32$) is severely underpowered:
1. **Minimum Detectable Effect (MDE)**: At $\alpha = 0.05$ and $80\%$ statistical power ($1 - \beta = 0.80$), the MDE for $n=32$ is $\pm 25.0$ percentage points. Differences smaller than 25% cannot be distinguished from chance.
2. **Threat-Class Representation**: With only 5 positive cases distributed across 4 disease classes (2 Blast, 1 BLB, 1 Nematode, 1 False Smut) and 0 cases for the remaining 6 threat classes (including all 5 insect pest classes), the benchmark barely evaluates diagnostic multi-class discrimination.
3. **Power Sizing for Reliable Field Validation**:
   - To reliably evaluate multi-threat diagnostic sensitivity and distinguish a 10–15 percentage-point performance margin ($\text{MDE} \le \pm 12\%$) at $\alpha = 0.05$ and $80\%$ power, a field benchmark requires at least **15 to 20 verified positive cases per threat class**.
   - Across all 10 threat classes, this requires **150 to 200 positive field cases**, evaluated against a balanced set of negative controls.
4. **Data Sourcing Constraint**: Expanding this benchmark requires labor-intensive extraction from peer-reviewed literature through the Stage A/B extraction protocol (verbatim symptom text, Crossref DOIs, laboratory confirmation). Sourcing authentic positive cases across under-reported pest classes remains an open domain curation challenge; per AIP hard constraints, cases cannot and will not be fabricated.

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

## 4. Evaluation Set Circularity of `benchmark_synthetic.csv`

The synthetic benchmark `data/benchmark_synthetic.csv` (80 test instances, formerly `dataText.csv`) was authored by the knowledge engineering team from the same SWRL rule antecedents that the reasoner executes:
1. **Ceiling Bias**: Multi-label accuracy of 99.25% and exact-match accuracy of 92.50% reflect deductive rule verification, not empirical diagnostic efficacy on real-world crops.
2. **Data Provenance Disclosure**: In accordance with scientific integrity standards, `data/README.md` classifies `benchmark_synthetic.csv` as `provenance: rule_derived`. As stated in `data/README.md`, this set cannot be interpreted as empirical clinical or field diagnostic accuracy.
3. **Comparative Baseline Context**: Outperforming supervised ML on `rule_derived` cases reflects cold-start inductive difficulty for ML rather than clinical superiority of RiceKG.

---

## 5. Description Logic Subsumption and Rejection of Probabilistic Calibration Claim

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
