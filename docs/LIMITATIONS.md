# System Limitations & Diagnostic Architectural Findings

## 1. Low True-Positive Diagnostic Recall on Independent Field Cases (1/5 Cases, 20.8%)

On the independent, peer-reviewed literature benchmark (`data/benchmark_field.csv`, $n=32$), RiceKG
correctly diagnoses **1 of the 5 in-scope positive disease cases**:

- **Positive-case recall**: **20.83%** averaged across cross-validation folds (1/5 cases resolved on the full set).
- **Micro-averaged F1**: **29.00** [95% non-parametric bootstrap CI: 9.5, 51.6].
- **Aggregate exact match**: 87.50% — but see Section 2; this figure is dominated by negative controls.

Two comparisons make the result harder to dismiss. Every supervised baseline attains **0.00%**
positive-case recall on the same cases, having at most five positive examples to learn from. The naive
nearest-prototype matcher, which uses neither the ontology nor the DL reasoner, attains **38.33%**
positive recall — **higher than RiceKG**. The knowledge-based architecture does not currently
outperform a trivial symptom-count heuristic on independent cases.

### Failure causes, per case

An earlier revision of this document attributed all five failures to vocabulary gating. That diagnosis
was incorrect, and its cause is recorded here because it materially affected the reported numbers.
`benchmark_field.csv` originally encoded symptoms in a descriptive snake_case namespace
(`seed_yellowish_green_velvety_balls`) that shared **zero** terms with the ontology vocabulary
`model.ALL_SYMPTOMS` (`Rusty_Grain_Balls`), while `benchmark_augmented.csv` matched it on all 45 terms.
Consequently every one of the 32 field cases reached the reasoner as an empty assertion set, and the
benchmark built in P0-3 to break evaluation circularity had never exercised the rule base at all. The
identifiers are now normalized through `data/symptom_mapping.csv`, which resolves 9 of the 25
descriptors to ontology terms and leaves 16 deliberately unmapped; unmapped descriptors are retained
per case in the `unmapped_terms` column.

After normalization, `results/field_failure_analysis.md` assigns each positive case one cause:

| Case | True label | Cause |
|:--|:--|:--|
| FIELD_01 | `Rice_Blast` | `partial_vocabulary` |
| FIELD_02 | `Rice_Blast` | `partial_vocabulary` |
| FIELD_03 | `Bacterial_Leaf_Blight` | `partial_vocabulary` |
| FIELD_04 | `Rice_Root_Nematode` | `rule_recall_failure` |
| FIELD_05 | `False_Smut` | `resolved` |

The distinction is consequential. Three cases fail because diagnostic descriptors such as bacterial ooze
and water-soaked lesions have no ontology counterpart — these call for vocabulary extension (Section 3).
**FIELD_04 fails although all three of its symptoms map cleanly** (`Hook_Like_Root_Swelling`,
`Yellowing_Leaves`, `Stunted_Growth`): the Tier-2 nematode rule requires more antecedents than a field
report supplies. That is a rule-coverage defect, and no amount of vocabulary work will fix it.

---

## 2. Benchmark Composition Imbalance and Sample Power Constraints

### The 84.4% negative-control composition defect

- **Total cases**: $n = 32$.
- **Positive in-scope disease cases**: $n = 5$ (15.6%).
- **Negative control / out-of-scope cases**: $n = 27$ (84.4%).

Because 84.4% of the benchmark consists of out-of-scope pathogens (*Burkholderia glumae*,
*Sarocladium oryzae*, *Rice stripe necrosis virus* and others), the aggregate exact match is an artifact
of correct rejection. Reporting it without segregating positive-case recall would conceal diagnostic
performance entirely, which is why `results/baselines.md` now reports the two in separate columns and
`tests/test_p0_4_baselines.py` fails if the narrative stops quoting the measured positive recall.

The observed specificity on negative controls is also only partly earned: a case whose descriptors are
entirely unmapped cannot fire a rule regardless of its content, so rejection is guaranteed by
construction rather than by discrimination.

### Requirements for a properly powered field benchmark

1. **Minimum detectable effect**: at $\alpha = 0.05$ and $80\%$ power, the MDE for $n=32$ is
   $\pm 25.0$ percentage points. Smaller differences cannot be distinguished from chance, so
   non-significant comparisons in `results/baselines.md` indicate underpowering, not equivalence.
2. **Threat-class representation**: the 5 positive cases span 4 disease classes (2 Blast, 1 BLB,
   1 Nematode, 1 False Smut), leaving 6 of the 10 modelled threats — including every insect pest
   class — with no positive case at all.
3. **Power sizing**: distinguishing a 10-15 percentage-point margin ($\text{MDE} \le \pm 12\%$) at
   $\alpha = 0.05$ and $80\%$ power requires on the order of **15 to 20 verified positive cases per
   threat class**, sourced through the P0-3 peer-reviewed extraction gate with verbatim symptom spans
   and Crossref-verified citations.

---

## 3. Ontological Scope and Controlled Vocabulary Coverage Bottleneck

An explicit scientific finding of the Stage B vocabulary mapping protocol is the **Controlled Vocabulary Coverage Bottleneck**:
- **Information Loss Across Real-World Cases**: Of the 25 distinct symptom descriptors extracted from the independent literature cases, **16 (64.0%) have no counterpart** among the ontology's 45 symptom terms and are dropped at mapping time (`data/symptom_mapping.csv`). After normalization 24 of the 32 cases (75.0%) retain at least one representable symptom, so the loss is substantial but not total.
- **Critical Anatomical Omission (`Leaf_Sheath`)**:
  - The RiceKG ontology defines symptoms on `Leaf`, `Panicle`, `Stem`, and `Root`, but contains **no anatomical concept for `Leaf_Sheath`**.
  - As a direct consequence, major rice diseases such as Sheath Rot (*Sarocladium oryzae*) and Sheath Blight (*Rhizoctonia solani*) cannot be syntactically described. Lesions on the flag leaf sheath had to be mapped to general foliar `leaves_spots_infestation` or dropped.
- **Absence of Diagnostic Panicle/Glume Lesions**:
  - Key grain symptoms such as `Glume_Discoloration`, `Powdery_Sooty_Spore_Masses`, and `Chaffy_Empty_Spikelets` are missing.

---

## 4. Evaluation Set Circularity of `benchmark_augmented.csv`

The augmented benchmark `data/benchmark_augmented.csv` (80 test instances, formerly `dataText.csv`) was authored by the knowledge engineering team from the same SWRL rule antecedents that the reasoner executes:
1. **Ceiling Bias**: Multi-label accuracy of 99.25% and exact-match accuracy of 92.50% reflect deductive rule verification, not empirical diagnostic efficacy on real-world crops.
2. **Data Provenance Disclosure**: In accordance with scientific integrity standards, `data/README.md` classifies `benchmark_augmented.csv` as `provenance: rule_derived`. As stated in `data/README.md`, this set cannot be interpreted as empirical clinical or field diagnostic accuracy.
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
