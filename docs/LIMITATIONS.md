# System Limitations & Diagnostic Architectural Findings

## 1. Monotonic Description Logic Subsumption Between Tier-1 and Tier-2 Rules

### The Architectural Issue
In the initial version of RiceKG, SWRL rules were stratified into:
- **Tier 1 (Canonical / Pathognomonic)**: High-cardinality antecedent sets ($4 \le |S| \le 7$ symptoms).
- **Tier 2 (Relaxed Composite)**: Low-cardinality antecedent sets ($2 \le |S| \le 3$ symptoms), where the Tier-2 antecedents formed a strict subset of the Tier-1 antecedents:
  $$\text{Ant}(R_{\text{tier2}}) \subset \text{Ant}(R_{\text{tier1}})$$

Under classical 2-valued first-order Horn-clause semantics, if both rules assert the identical predicate $\text{hasThreat}(?Rice, T)$, Tier 1 is logically redundant in terms of the diagnosis set:
$$\forall \text{Rice Sample } x, \quad \text{fires}(R_{\text{tier1}}, x) \implies \text{fires}(R_{\text{tier2}}, x)$$
Whenever Tier 1 fires, Tier 2 has already fired; whenever Tier 1 does not fire, Tier 2 might fire. Therefore, Tier 1 never changes the set of inferred threat individuals $\{\text{Grasshopper}, \dots\}$.

### The Empirical Resolution: Confidence-Graded Inference
To resolve this logical defect without discarding domain expert pathognomonic rules, RiceKG separates the consequents into distinct OWL object properties in a multiple inheritance hierarchy:
- Tier 1 asserts `hasConfirmedThreat`
- Tier 2 asserts `hasSuspectedThreat`
- Both inherit from `hasThreat` (`hasPest` / `hasDisease`)

When measured on the benchmark dataset (`evaluate.py`):
1. **Diagnosis Set Invariance**: Tier 1 still does not expand the set of diagnosed threats beyond Tier 2 alone. In terms of raw multi-label recall, Tier-2-only achieves identical coverage to Full (76 TP out of 80 targets).
2. **Diagnostic Calibration and Precision**:
   - **Tier-1 Precision@Confirmed**: **100.00%** (8 TP, 0 FP). When canonical pathognomonic criteria are met, the false discovery rate is exactly 0.00%.
   - **Tier-2 Precision@Suspected**: **97.14%** (68 TP, 2 FP). When partial observation criteria are met, recall is dramatically expanded (+68 diagnoses), but incurs 2 false positive discoveries (Case #59 Brown Planthopper co-diagnosed as Rice Bug; Case #60 False Smut co-diagnosed as Rice Blast).
   - **Brier Score**: Stratified confidence grading reduces multi-label probabilistic error from **0.007500** (flat binary) to **0.007429** (calibrated graded).

### Recommendation for Manuscript Framing
The manuscript must **not** claim that Tier 1 expands diagnostic recall. Rather, the multi-tier architecture should be framed as a **specificity vs. sensitivity trade-off mechanism**:
- Tier 1 serves as a high-specificity pathognomonic confirmation filter (100% precision, 0% FDR).
- Tier 2 serves as an actionable field screening filter under incomplete symptom scouting (high sensitivity, 97.14% precision).

---

## 2. Evaluation Set Circularity and Ceiling Effects

The standard benchmark file `dataText.csv` (80 test instances) was constructed using synthetic symptom profiles derived directly from the SWRL rule antecedent definitions. 

### Implications
1. **Ceiling Performance**: The system scores 99.25% multi-label accuracy and 92.50% exact-match accuracy because the test cases are synthetically aligned with the rule base.
2. **Generalization Gap**: Performance on real-world field observations (where farmers observe noisy, co-infected, or atypical symptom manifestations) cannot be rigorously estimated from `dataText.csv` alone.
3. **Remediation**: An independent, expert-annotated field dataset (`benchmark_field.csv`) must be evaluated to break this circularity (see P0-3).

