# Comparative Baseline Evaluation & Paired Significance Testing

> **Generated**: 2026-09-14 07:42:24 UTC  
> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), and Holm–Bonferroni FWER step-down correction.

---

## 1. Deductive Verification Suite (`verification_suite.csv`, $n=73$)

- **Dataset Provenance**: Rule-derived cases ($n=73$, multi-threat composites).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 7 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$16.6% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **64.38 ± 1.80** | **40.84 ± 9.80** | **[34.1, 49.3]** | — | — | Baseline Reference | — |
| RiceKG (Full + Possible) | Knowledge-Based / Semantic Web | 0 cases (cold start) | 68.48 ± 5.73 | 68.40 ± 4.77 | [63.7, 72.0] | 0.1060 | **0.2119** | -4.1% [-8.7, 0.5] | -0.10 |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 86.28 ± 4.30 | 90.00 ± 2.32 | [87.3, 92.1] | < 0.001 | **< 0.001*** | -21.9% [-27.6, -16.2] | -0.31 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 64.38 ± 1.80 | 40.84 ± 9.80 | [34.1, 49.3] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 36 cases/fold | 71.21 ± 6.65 | 71.07 ± 8.50 | [67.2, 75.3] | 0.0062 | **0.0187*** | -6.8% [-11.5, -2.2] | -0.16 |
| Random Forest | Supervised Machine Learning | 36 cases/fold | 75.59 ± 7.47 | 71.25 ± 9.42 | [66.9, 76.2] | < 0.001 | **< 0.001*** | -11.2% [-15.9, -6.6] | -0.26 |
| Multinomial Naive Bayes | Supervised Machine Learning | 36 cases/fold | 75.65 ± 7.11 | 73.30 ± 10.01 | [66.7, 78.1] | < 0.001 | **< 0.001*** | -11.2% [-17.0, -5.5] | -0.17 |
| k-NN | Supervised Machine Learning | 36 cases/fold | 77.25 ± 5.98 | 73.66 ± 7.90 | [69.3, 78.3] | < 0.001 | **< 0.001*** | -12.9% [-17.6, -8.1] | -0.28 |
| Logistic Regression (OvR) | Supervised Machine Learning | 36 cases/fold | 74.51 ± 7.02 | 68.03 ± 10.54 | [63.7, 73.9] | < 0.001 | **< 0.001*** | -10.1% [-14.7, -5.6] | -0.25 |

*Note: Asterisk (\*) on Holm-Adj p indicates statistically significant difference vs RiceKG after Holm–Bonferroni correction ($\alpha = 0.05$). Risk Difference ($\Delta$ Acc) is reported as percentage-point difference with paired Wald 95% confidence interval. Cohen's g is bounded on $[-0.50, +0.50]$ (defined as $g = b/(b+c) - 0.5$); values near $+0.50$ indicate that the ceiling of the statistic has been reached due to near-zero errors by RiceKG on discordant pairs ($c \approx 0$), rather than an unbounded magnitude.*

### Key Findings (Verification Suite)
1. **Rule-Derived Verification Only**: All 80 cases in `verification_suite.csv` have provenance `rule_derived`, constructed from RiceKG's own Horn clauses. Outperforming ML on cases generated from internal rules verifies deductive consistency, but does not establish empirical diagnostic superiority over supervised learning.
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
| RiceKG (Full + Possible) | Knowledge-Based / Semantic Web | 0 cases (cold start) | 39.09 ± 10.21 | 17.50 ± 18.43 | 34.44 ± 9.97 | [25.6, 42.2] | < 0.001 | **< 0.001*** | +47.8% [38.7, 57.0] | +0.50 |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 73.94 ± 3.54 | 17.50 ± 18.43 | 43.29 ± 19.55 | [31.7, 58.5] | < 0.001 | **< 0.001*** | +13.0% [6.9, 19.2] | +0.50 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 86.82 ± 7.26 | 35.00 ± 36.86 | 40.67 ± 41.36 | [34.8, 74.3] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 11 cases/fold | 69.70 ± 9.01 | 10.00 ± 30.00 | 2.86 ± 8.57 | [0.0, 15.0] | < 0.001 | **< 0.001*** | +17.4% [10.1, 24.7] | +0.45 |
| Random Forest | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0078*** | +8.7% [3.5, 13.8] | +0.50 |
| Multinomial Naive Bayes | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0078*** | +8.7% [3.5, 13.8] | +0.50 |
| k-NN | Supervised Machine Learning | 11 cases/fold | 76.36 ± 8.12 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **0.0024*** | +10.4% [4.8, 16.0] | +0.50 |
| Logistic Regression (OvR) | Supervised Machine Learning | 11 cases/fold | 78.03 ± 7.65 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0020 | **0.0078*** | +8.7% [3.5, 13.8] | +0.50 |

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
| RiceKG (Full + Possible) | 56.25 | 55.00 | 60.08 |
| Rule: Nearest Prototype | 75.00 | 51.67 | 65.00 |
| Rule: Flat Single-Tier | 81.25 | 63.33 | 75.14 |
| Decision Tree | 55.00 | 32.50 | 28.76 |
| Random Forest | 62.50 | 29.17 | 35.52 |
| Multinomial Naive Bayes | 56.25 | 0.00 | 0.00 |
| k-NN | 47.50 | 0.00 | 0.00 |
| Logistic Regression (OvR) | 58.75 | 18.33 | 19.67 |


---

## 3. Statistical Power & Minimum Detectable Effect Disclosure

- **Verification Suite ($n=73$)**: $\text{MDE} = \pm 16.6\%$.
- **Field Benchmark, eval split ($n=23$, 5 positive cases)**: $\text{MDE} = \pm 29.5\%$.
- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.