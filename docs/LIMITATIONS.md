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

## 2. Evaluation Set Circularity and Field Benchmark Independence

### The Circularity Defect of `benchmark_synthetic.csv`
The benchmark file `data/benchmark_synthetic.csv` (80 test instances, formerly `dataText.csv`) was authored by the knowledge engineering team from the same SWRL rule antecedents that the reasoner executes:
1. **Ceiling Bias**: Multi-label accuracy of 99.25% and exact-match accuracy of 92.50% reflect deductive rule verification, not empirical diagnostic efficacy on real-world crops.
2. **Data Provenance Disclosure**: In accordance with scientific integrity standards, `data/README.md` classifies `benchmark_synthetic.csv` as `provenance: rule_derived`.

### Remediation: Independent Literature & Field Benchmark (`benchmark_field.csv`)
To break evaluation circularity:
1. **Independent Benchmark (`data/benchmark_field.csv`)**: Contains authentic, peer-reviewed case reports and IRRI Rice Doctor compendium entries ($n=15$) spanning all 10 threat classes, with complete bibliographic citations, geographical coordinates, observation dates, and ground truth verification methods (`literature_case`).
2. **Inter-Annotator Agreement Protocol**: `analysis/agreement.py` provides Cohen's and Fleiss' $\kappa$ with bootstrap CIs for prospective multi-rater extension scouting.
3. **Separation of Metrics**: The synthetic benchmark and independent field benchmark are evaluated separately via `evaluate.py --dataset [synthetic|field]` and are **never pooled into an aggregate score**.
