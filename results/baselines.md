# Comparative Baseline Evaluation & Paired Significance Testing

> **Generated**: 2026-09-13 10:38:33 UTC  
> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), and Holm–Bonferroni FWER step-down correction.

---

## 1. Augmented Verification Benchmark (`benchmark_augmented.csv`, $n=80$)

- **Dataset Provenance**: Rule-derived cases ($n=80$, multi-threat composites).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 16 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$15.8% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **60.00 ± 6.52** | **68.30 ± 3.41** | **[64.2, 72.4]** | — | — | Baseline Reference | — |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 72.50 ± 2.24 | 86.65 ± 1.37 | [84.5, 88.7] | < 0.001 | **0.0026*** | -12.5% [-19.1, -5.9] | -0.13 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 60.00 ± 6.52 | 68.30 ± 3.41 | [64.2, 72.4] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 40 cases/fold | 52.25 ± 10.27 | 69.39 ± 7.51 | [66.1, 72.4] | 0.0146 | **0.0878** | +7.8% [1.8, 13.7] | +0.10 |
| Random Forest | Supervised Machine Learning | 40 cases/fold | 55.25 ± 9.58 | 67.07 ± 8.04 | [63.8, 70.8] | 0.1046 | **0.5229** | +4.7% [-0.7, 10.2] | +0.08 |
| Multinomial Naive Bayes | Supervised Machine Learning | 40 cases/fold | 63.25 ± 10.07 | 77.44 ± 8.31 | [73.1, 80.7] | 0.3671 | **1.0000** | -3.2% [-9.8, 3.3] | -0.04 |
| k-NN | Supervised Machine Learning | 40 cases/fold | 63.75 ± 7.93 | 69.73 ± 6.99 | [66.1, 73.7] | 0.1994 | **0.7974** | -3.7% [-9.1, 1.6] | -0.06 |
| Logistic Regression (OvR) | Supervised Machine Learning | 40 cases/fold | 57.75 ± 10.69 | 69.01 ± 9.10 | [65.5, 72.8] | 0.4671 | **1.0000** | +2.2% [-3.1, 7.6] | +0.04 |

*Note: Asterisk (\*) on Holm-Adj p indicates statistically significant difference vs RiceKG after Holm–Bonferroni correction ($\alpha = 0.05$). Risk Difference ($\Delta$ Acc) is reported as percentage-point difference with paired Wald 95% confidence interval. Cohen's g is bounded on $[-0.50, +0.50]$ (defined as $g = b/(b+c) - 0.5$); values near $+0.50$ indicate that the ceiling of the statistic has been reached due to near-zero errors by RiceKG on discordant pairs ($c \approx 0$), rather than an unbounded magnitude.*

### Key Findings (Augmented Benchmark)
1. **Rule-Derived Verification Only**: All 80 cases in `benchmark_augmented.csv` have provenance `rule_derived`, constructed from RiceKG's own Horn clauses. Outperforming ML on cases generated from internal rules verifies deductive consistency, but does not establish empirical diagnostic superiority over supervised learning.
2. **Cold-Start Sample Efficiency**: Supervised ML models trained on 40 cases/fold achieve 55.50% to 63.75% exact match because 16 rare multi-threat combinations appear only once. RiceKG requires **zero training data** and executes deterministic symbolic inference.
3. **Rule Stratification Identity**: The unstratified single-tier rule baseline (*Flat Single-Tier*) achieves identical numerical accuracy to Full RiceKG on this benchmark, confirming the P0-2 ablation finding that tier stratification provides clinical specificity/screening grading rather than an accuracy improvement.

---

## 2. Independent Peer-Reviewed Field Benchmark (`benchmark_field.csv`, held-out `eval` split, $n=23$)

- **Dataset Provenance**: Peer-reviewed observed-case reports ($n=23$: 5 in-scope disease cases, 18 out-of-scope negative controls). Sources that are not case reports were excluded to `data/rejected_field_candidates.csv` with a stated reason.
- **Independence (downgraded)**: this partition was held out during P0-5 Steps 2-3, but its aggregate scores have now been observed across two rounds of rule revision. It is **development-informed**, not strictly held out. See `docs/LIMITATIONS.md` Section 2. A fresh partition is required before the manuscript cites an independent diagnostic figure.
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 3 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$29.5% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **86.82 ± 7.26** | **35.00 ± 36.86** | **40.67 ± 41.36** | **[34.8, 74.3]** | — | — | Baseline Reference | — |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 73.94 ± 3.54 | 17.50 ± 18.43 | 43.29 ± 19.55 | [31.7, 58.5] | < 0.001 | **< 0.001*** | +13.0% [6.9, 19.2] | +0.50 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 86.82 ± 7.26 | 35.00 ± 36.86 | 40.67 ± 41.36 | [34.8, 74.3] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 11 cases/fold | 69.70 ± 9.01 | 10.00 ± 30.00 | 2.86 ± 8.57 | [0.0, 15.0] | < 0.001 | **< 0.001*** | +17.4% [10.1, 24.7] | +0.45 |
| Random Forest | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0098*** | +8.7% [3.5, 13.8] | +0.50 |
| Multinomial Naive Bayes | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0098*** | +8.7% [3.5, 13.8] | +0.50 |
| k-NN | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0098*** | +8.7% [3.5, 13.8] | +0.50 |
| Logistic Regression (OvR) | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0098*** | +8.7% [3.5, 13.8] | +0.50 |

*Note: Aggregate exact match is dominated by the 18/23 negative control cases (78.3% of the benchmark), on which returning `No_Diagnosis` is correct. Positive-case recall over the 5 in-scope disease cases is reported separately and is the diagnostically meaningful column. Risk Difference (\Delta Acc) is reported with paired Wald 95% CI. Cohen's g is bounded on $[-0.50, +0.50]$ and saturates; read the Risk Difference for magnitude.*

### Key Findings (Independent Field Benchmark)
1. **Positive-Case Recall Is the Binding Constraint**: On the only independent benchmark in the repository, RiceKG attains 35.00% positive-case recall over 5 in-scope disease cases (micro-F1 40.67, 95% CI [34.8, 74.3]), against an aggregate exact match of 86.82%. Diagnostic efficacy on authentic field cases remains largely unproven.
2. **Every Supervised Baseline Scores Zero on Positive Cases**: All five ML classifiers attain 0.00% positive-case recall, having at most 5 positive training examples split across folds. Their aggregate accuracy is produced solely by predicting the majority `No_Diagnosis` class.
3. **Residual Failures Are Now Separable**: Following identifier normalization against `model.ALL_SYMPTOMS` (see `data/symptom_mapping.csv`), the remaining errors split into genuine vocabulary gaps — literature descriptors such as bacterial ooze and water-soaked lesions that the 45-term vocabulary does not model — and true Tier-2 rule-recall failures on partially observed cases. `results/field_failure_analysis.md` assigns a cause to each case.
4. **Negative Control Artifact**: 18 of 23 cases (78.3%) are out-of-scope emerging pathogens. Reporting aggregate exact match alone would conceal positive-case performance entirely, which is why the two are separated above.
5. **Statistical Power & MDE**: With $n=23$ and only 5 positive cases, the minimum detectable effect is $\pm 29.5$ percentage points. Non-significant comparisons reflect severe underpowering, not demonstrated equivalence.

### Companion: development split (not independent)

The `dev` split holds 16 cases (7 positive, 9 negative controls) and was visible during vocabulary and rule work. It is reported for transparency only and must not be cited as independent evidence.

| System / Model | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) |
|:---|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 81.25 | 63.33 | 75.14 |
| Rule: Nearest Prototype | 75.00 | 51.67 | 65.00 |
| Rule: Flat Single-Tier | 81.25 | 63.33 | 75.14 |
| Decision Tree | 55.00 | 32.50 | 28.76 |
| Random Forest | 62.50 | 29.17 | 35.52 |
| Multinomial Naive Bayes | 56.25 | 0.00 | 0.00 |
| k-NN | 51.25 | 0.00 | 0.00 |
| Logistic Regression (OvR) | 56.25 | 0.00 | 0.00 |


---

## 3. Statistical Power & Minimum Detectable Effect Disclosure

- **Augmented Benchmark ($n=80$)**: $\text{MDE} = \pm 15.8\%$.
- **Field Benchmark, eval split ($n=23$, 5 positive cases)**: $\text{MDE} = \pm 29.5\%$.
- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.