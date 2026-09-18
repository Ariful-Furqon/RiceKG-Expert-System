# System Limitations & Diagnostic Architectural Findings

## 1. Ontology and Rule Remediation Did Not Improve Held-Out Diagnostic Recall

P0-5 Steps 2 and 3 extended the symptom vocabulary from 45 to 54 terms and revised five Tier-2
rules, each change justified from the phytopathology literature and documented in
[`docs/ONTOLOGY.md`](ONTOLOGY.md). The measured outcome is a large gain on the development
partition and **no gain on the held-out partition**.

| | Before Steps 2-3 | After Steps 2-3 |
|:--|:--:|:--:|
| **`eval` positive-case recall** | 38.33% | **35.00%** (now **31.67%**†) |
| **`eval` micro-F1** | 48.00 | **40.67** (now **41.00** [95% CI 33.3, 75.7]†) |
| **`eval` aggregate exact match** | 86.97% | **86.82%** (now **86.36%**†) |

† Current values after FIELD_24 was rejected in ontology v2.2.0 (`eval` 23 → 22 cases). 31.67% is a 5×2-fold average; it was 35.00% before FIELD_24 was rejected (ontology v2.2.0). The change comes only from the fold re-partition: no diagnosis changed, and pooled recall is 2/5 = 40.0%.
| `dev` positive-case recall | 19.17% | **63.33%** |
| `dev` micro-F1 | 24.86 | **75.14** |
| Positive cases resolved, both partitions | 3/12 | **6/12** |
| False positives on negative controls | 0 | **0** |

The `dev` gain is large and the held-out result is flat to slightly worse. A 63.33% versus 35.00%
gap between the partition that was visible during the work and the partition that was not is the
signature of overfitting to the development set, and it should be read that way even though every
individual change was argued from published agronomy rather than from a case.

Against the baselines on `eval`, RiceKG exceeds the ontology-free nearest-prototype matcher by
9.1 percentage points of exact match (Holm-adjusted $p = 0.0117$) and reaches 31.67% positive
recall against its 15.00%. The prototype matcher nonetheless retains a higher micro-F1
(57.05 against 41.00), so the two are not cleanly separated on that measure.

### An intermediate revision was withdrawn

The first attempt at `SWRL-R16` paired `Water_Soaked_Lesions` with `Bacterial_Ooze`. Both signs are
listed for bacterial blight in Ou (1985), but neither discriminates it: bacterial exudate is a
genus-level sign shared with *X. oryzicola*, *Burkholderia* and *Pantoea*, which is what the negative
controls contain. That revision produced **4 false positives on the 27 negative controls**. The same
error affected grassy stunt, where stunting with mottling is shared across rice viruses. Both rules
were re-specified around discriminating signs — tip-and-margin lesion onset for blight, excessive
tillering for grassy stunt — and the false positives returned to zero. The lesson is recorded here
because listing a sign for a disease is not the same as the sign distinguishing that disease.

### Remaining failure causes across all 12 positive cases

| Cause | Count | Cases |
|:--|:--:|:--|
| `resolved` | 6 | FIELD_04, FIELD_05, FIELD_33, FIELD_34, FIELD_35, FIELD_36 |
| `rule_recall_failure` | 4 | FIELD_02, FIELD_51, FIELD_52, FIELD_53 |
| `partial_vocabulary` | 2 | FIELD_01, FIELD_03 |

The four remaining rule failures are the two virus classes and one blast case. `Excessive_Tillering`
and `Orange_Leaf_Discoloration` were added because the literature identifies them as the
discriminating signs for grassy stunt and tungro, but **no descriptor in the benchmark records
either of them**, so the revised virus rules cannot fire on the present case set. That is a
limitation of what the source literature reports, not of the rules.

---

## 2. The Held-Out Partition Is Now Development-Informed

The field benchmark was partitioned into `dev` and `eval` so that rule and vocabulary work could be
validated without consuming the independent evidence. **That protection has been partly spent.**
The `eval` aggregate scores have now been observed across two rounds of rule revision within P0-5,
and although no individual `eval` case was inspected and no change was justified by one, the
knowledge that a revision moved the held-out number in a particular direction is itself information
that leaked into the process.

Consequently:

- `eval` figures in this repository are **development-informed**, not strictly held out.
- The manuscript must not describe the current 31.67% positive-case recall as an independent
  estimate of diagnostic efficacy. It is an optimistic bound.
- A genuinely independent figure requires a **fresh partition sourced after the rule base is
  frozen**, through the P0-3 case-report gate.

`results/baselines.md` carries this downgrade in its own header so the qualification travels with
the numbers.

### Composition, sourcing limits, and statistical power

- Retained benchmark: 38 cases — 12 in-scope positives, 26 out-of-scope negative controls.
  The `eval` partition holds 5 positives and 17 negative controls; `dev` holds 7 and 9.
- P0-5 sourced 21 candidate cases and **rejected 14**: every DOI resolved against Crossref, but the
  sources were reviews, control-efficacy trials, population-genetics studies and a caged infestation
  experiment whose symptom text is textbook description rather than observation. Two supplied a
  "case" each on opposite sides of the split boundary. Rejections are preserved with reasons in
  `data/rejected_field_candidates.csv`, and `tests/test_p0_5_field.py` enforces the gate.
- **`Grasshopper`, `Rice_Bug`, `Rice_Stem_Borer` and `Brown_Planthopper` have no positive field case.**
  Insect pests are not published as first-report disease notes the way emerging pathogens are, so the
  venue supplying case-grade evidence for diseases has no equivalent for pests. No claim about
  diagnostic performance on insect pests is supported by field evidence.
- Held-out MDE is $\pm 30.2$ percentage points ($\alpha = 0.05$, $80\%$ power); on `dev` it is
  $\pm 35.4$. Differences below those thresholds cannot be distinguished from chance, so every
  non-significant comparison here is underpowered rather than demonstrably equivalent.
- Distinguishing a 10-15 point margin would require roughly **15 to 20 verified positive cases per
  threat class**. The present benchmark is an order of magnitude short.

### Per-Class Field Coverage Analysis (6/6 In-Scope Coverage)

The table below summarizes independent empirical validation coverage (`dev` and `eval` splits; the development-exposed `holdout` split is reported separately) across the 6 in-scope biotic threat classes modeled in RiceKG following the Part 5 scope narrowing:

| Threat Class | Category | Independent Field Cases ($n$) | Partition Split | Field Case IDs | Empirical Validation Status |
|:---|:---|:---:|:---:|:---|:---:|
| **Bacterial Leaf Blight** | Pathogen (Bacterium) | 3 | 1 eval, 2 dev | FIELD_03, FIELD_35, FIELD_36 | Evaluated ($n=3$) |
| **False Smut** | Pathogen (Fungus) | 1 | 0 eval, 1 dev | FIELD_05 | Evaluated ($n=1$) |
| **Rice Blast** | Pathogen (Fungus) | 2 | 0 eval, 2 dev | FIELD_01, FIELD_02 | Evaluated ($n=2$) |
| **Rice Grassy Stunt** | Pathogen (Virus) | 1 | 1 eval, 0 dev | FIELD_53 | Evaluated ($n=1$) |
| **Rice Root-Knot Nematode** | Plant-parasitic nematode | 3 | 1 eval, 2 dev | FIELD_04, FIELD_33, FIELD_34 | Evaluated ($n=3$) |
| **Rice Tungro Virus** | Pathogen (Virus) | 2 | 2 eval, 0 dev | FIELD_51, FIELD_52 | Evaluated ($n=2$) |
| *Out-of-Scope Negative Controls* | Pathogen Mimics | 26 | 17 eval, 9 dev | FIELD_06–FIELD_32 except FIELD_24 | Evaluated (Specificity) |
| *Excluded Insect Classes (Reference Only)* | Insect Pests | 0 | — | Excluded from scope | Outside Diagnostic Scope |

**Key Coverage Takeaways**:
1. **100% In-Scope Empirical Coverage (6/6 Classes)**: With the diagnostic scope narrowed to exclude insect pests, **every single in-scope threat class (6/6, 100%) possesses independent empirical field backing** in `data/benchmark_field.csv`.
2. **Resolution of the Structural Sourcing Bottleneck**: Four insect pest classes (`Grasshopper`, `Rice_Stem_Borer`, `Rice_Bug`, `Brown_Planthopper`) were excluded from the automated diagnostic scope because phytopathology first-report disease notes report pathogens, leaving insect pests with zero empirical field reports. Rather than asserting diagnostic competence unsupported by literature evidence, the system reclassifies their 19 damage signs as out-of-scope vocabulary (`InsectDamageSign`), providing an informative differential response (*"consistent with insect damage, which is outside the diagnostic scope of this system"*). The response requires at least two distinct insect-specific signs (`model.INSECT_SPECIFIC_SIGNS`); signs shared with pathogens or abiotic stress never trigger it. It has been exercised only on rule-derived controls, so its field reliability is unmeasured.
3. **Vector Sightings Retained**: Vector presence terms (`Brown_Planthopper_Present` and `Green_Leafhopper_Present`) remain in the ontology as supporting observational antecedents for the viral diseases they transmit (`Rice_Grassy_Stunt` and `Rice_Tungro_Virus`).

---

## 3. Residual Vocabulary Coverage Limits

The P0-5 Step 2 extension closed the most serious gaps, but coverage remains partial.

- Of the 25 distinct symptom descriptors extracted from the field literature, **16 now map** to an
  ontology term and **9 remain unmapped** (`data/symptom_mapping.csv`). Before the extension the
  split was 9 mapped and 16 unmapped.
- The missing `Leaf_Sheath` anatomy has been added as `Leaf_Sheath_Lesions`, together with
  `Stem_Rot_Lesions` and `Grain_Discoloration`. These three are **expressivity only**: sheath and
  culm diseases (*Rhizoctonia solani*, *Sarocladium oryzae*) lie outside the ten modelled threats and
  appear in the benchmark solely as negative controls. The terms let such cases be described rather
  than silently dropped, which makes their rejection an act of discrimination instead of an artifact
  of unmappable input. Wiring them to a modelled threat would manufacture false positives.
- The nine still-unmapped descriptors are striping and streaking patterns, leaf bleaching, whitened
  leaf tips, whole-leaf withering, generic leaf discoloration, generic drying, root discoloration and
  plant malformation. Near-misses were deliberately not forced: `Yellowing_Leaf_Tips` is not
  "whitened tips", and `Hopperburn_Drying` is planthopper-specific and cannot stand for generic drying.
- Two terms added for their discriminating value — `Excessive_Tillering` for grassy stunt and
  `Orange_Leaf_Discoloration` for tungro — have **no corresponding descriptor anywhere in the
  benchmark**, so the virus rules that depend on them cannot fire on the present case set.

---

## 4. Evaluation Set Circularity of `verification_suite.csv`

`data/verification_suite.csv` (80 instances, formerly `benchmark_augmented.csv` / `dataText.csv`) was authored from the same
SWRL rule antecedents that the reasoner executes, and carries provenance `rule_derived`.

The P0-5 rule revisions demonstrated this circularity directly rather than by argument. Revising
five Tier-2 rules on literature grounds — without touching the benchmark — moved exact-match
accuracy on this set from **92.50% to 60.00%** and multi-label accuracy from **99.25% to 95.12%**.
A benchmark whose score collapses when the rules change is measuring agreement with those rules,
not diagnostic ability. The former near-ceiling figures were never independent evidence, and the
present lower figures are not evidence of degraded diagnosis either; both are measurements of
consistency with whichever rule base generated the cases.

The set retains one legitimate use: verifying that rule firing remains deductively consistent.
It cannot be interpreted as empirical clinical or field diagnostic accuracy, and outperforming
supervised ML on it reflects cold-start inductive difficulty for the learners rather than clinical
superiority of RiceKG.

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

---

## 6. Cold-Start Learning Curve and Coarse Granularity of the Field Evaluation Set

The cold-start learning curve experiment ([`results/learning_curve.md`](../results/learning_curve.md)) quantifies the sample efficiency of RiceKG's zero-shot symbolic knowledge base relative to five supervised machine learning models across scaling training budgets (Pool A: $N \in [5, 80]$ rule-derived cases; Pool B: $N \in [2, 16]$ real field cases).

This analysis reveals an inherent structural limitation of the independent field evaluation set:

1. **Staircase Quantisation Step ($\Delta = 0.20$)**:
   The held-out `eval` partition of [`data/benchmark_field.csv`](../data/benchmark_field.csv) contains strictly $n = 5$ in-scope positive disease cases (and 17 out-of-scope negative controls). As a result, positive-case recall on any single evaluation run or draw is inherently discrete and can only take values in the quantised set:
   $$\text{Recall}_{\text{pos}} \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$$
   with a coarse step size of $\Delta = 0.20$ (20.0 percentage points per case). Every single misclassification or correct prediction shifts the measured recall by a full 20.0 percentage points, creating a discrete staircase rather than a continuous curve.
2. **Statistical Power and Wide Confidence Intervals**:
   While aggregating across $R = 200$ stratified bootstrap draws smooths the expected mean recall, the 95% confidence intervals at small budgets remain wide. Furthermore, as established in Section 2, the minimum detectable effect size on this partition is $\pm 30.2\%$ ($\alpha = 0.05$, $80\%$ power). Consequently, apparent small margins between supervised ML models and the zero-shot symbolic knowledge base (e.g., 40.0% vs. 35.00%) lie entirely within the noise margin of random variation.
3. **Methodological Mitigation**:
   To prevent misleading interpretations:
   - All learning-curve evaluations report per-budget non-parametric 95% bootstrap confidence intervals rather than bare point means;
   - A secondary smooth learning curve is reported over the larger verification suite ($n = 80$) to reveal asymptotic inductive behavior, explicitly disclosed as rule-derived rather than empirical field performance;
   - Crossover budgets ($N^*$) are strictly defined to require that the 95% bootstrap CI of the paired difference excludes zero, and no extrapolation beyond empirical pool boundaries is permitted.

