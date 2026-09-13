# Comparative Baseline Evaluation & Paired Significance Testing

> **Generated**: 2026-09-13 05:08:32 UTC  
> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), and Holm–Bonferroni FWER step-down correction.

---

## 1. Augmented Verification Benchmark (`benchmark_augmented.csv`, $n=80$)

- **Dataset Provenance**: Rule-derived cases ($n=80$, multi-threat composites).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 16 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$15.8% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **92.50 ± 2.24** | **96.19 ± 1.15** | **[94.8, 97.4]** | — | — | Baseline Reference | — |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 72.50 ± 2.24 | 86.65 ± 1.37 | [84.5, 88.7] | < 0.001 | **< 0.001*** | +20.0% [15.8, 24.2] | +0.44 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 92.50 ± 2.24 | 96.19 ± 1.15 | [94.8, 97.4] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 40 cases/fold | 55.50 ± 6.40 | 72.04 ± 5.46 | [69.0, 75.2] | < 0.001 | **< 0.001*** | +37.0% [31.8, 42.2] | +0.44 |
| Random Forest | Supervised Machine Learning | 40 cases/fold | 55.50 ± 9.80 | 67.56 ± 8.64 | [64.2, 71.3] | < 0.001 | **< 0.001*** | +37.0% [32.1, 41.9] | +0.47 |
| Multinomial Naive Bayes | Supervised Machine Learning | 40 cases/fold | 63.75 ± 9.17 | 78.24 ± 6.89 | [74.2, 81.5] | < 0.001 | **< 0.001*** | +28.8% [23.9, 33.6] | +0.44 |
| k-NN | Supervised Machine Learning | 40 cases/fold | 63.75 ± 7.93 | 69.73 ± 6.99 | [66.1, 73.7] | < 0.001 | **< 0.001*** | +28.8% [23.9, 33.6] | +0.44 |
| Logistic Regression (OvR) | Supervised Machine Learning | 40 cases/fold | 57.75 ± 10.69 | 69.01 ± 9.10 | [65.5, 72.8] | < 0.001 | **< 0.001*** | +34.8% [29.9, 39.6] | +0.48 |

*Note: Asterisk (\*) on Holm-Adj p indicates statistically significant difference vs RiceKG after Holm–Bonferroni correction ($\alpha = 0.05$). Risk Difference ($\Delta$ Acc) is reported as percentage-point difference with paired Wald 95% confidence interval. Cohen's g is bounded on $[-0.50, +0.50]$ (defined as $g = b/(b+c) - 0.5$); values near $+0.50$ indicate that the ceiling of the statistic has been reached due to near-zero errors by RiceKG on discordant pairs ($c \approx 0$), rather than an unbounded magnitude.*

### Key Findings (Augmented Benchmark)
1. **Rule-Derived Verification Only**: All 80 cases in `benchmark_augmented.csv` have provenance `rule_derived`, constructed from RiceKG's own Horn clauses. Outperforming ML on cases generated from internal rules verifies deductive consistency, but does not establish empirical diagnostic superiority over supervised learning.
2. **Cold-Start Sample Efficiency**: Supervised ML models trained on 40 cases/fold achieve 55.50% to 63.75% exact match because 16 rare multi-threat combinations appear only once. RiceKG requires **zero training data** and executes deterministic symbolic inference.
3. **Rule Stratification Identity**: The unstratified single-tier rule baseline (*Flat Single-Tier*) achieves identical numerical accuracy to Full RiceKG on this benchmark, confirming the P0-2 ablation finding that tier stratification provides clinical specificity/screening grading rather than an accuracy improvement.

---

## 2. Independent Peer-Reviewed Field Benchmark (`benchmark_field.csv`, $n=32$)

- **Dataset Provenance**: Authentic literature case series from APS *Plant Disease* Disease Notes ($n=32$).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 3 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$25.0% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **87.50 ± 5.59** | **20.83 ± 22.13** | **29.00 ± 30.04** | **[9.5, 51.6]** | — | — | Baseline Reference | — |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 84.38 ± 3.12 | 38.33 ± 15.00 | 41.71 ± 15.05 | [25.6, 61.3] | 0.3018 | **0.6035** | +3.1% [-1.6, 7.8] | +0.17 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 87.50 ± 5.59 | 20.83 ± 22.13 | 29.00 ± 30.04 | [9.5, 51.6] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 16 cases/fold | 83.12 ± 4.88 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0156 | **0.1094** | +4.4% [1.2, 7.5] | +0.50 |
| Random Forest | Supervised Machine Learning | 16 cases/fold | 83.12 ± 4.88 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0156 | **0.1094** | +4.4% [1.2, 7.5] | +0.50 |
| Multinomial Naive Bayes | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0625 | **0.2500** | +3.1% [0.4, 5.8] | +0.50 |
| k-NN | Supervised Machine Learning | 16 cases/fold | 83.12 ± 4.88 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0156 | **0.1094** | +4.4% [1.2, 7.5] | +0.50 |
| Logistic Regression (OvR) | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | 0.0625 | **0.2500** | +3.1% [0.4, 5.8] | +0.50 |

*Note: Aggregate exact match is dominated by the 27/32 negative control cases (84.4% of the benchmark), on which returning `No_Diagnosis` is correct. Positive-case recall over the 5 in-scope disease cases is reported separately and is the diagnostically meaningful column. Risk Difference (\Delta Acc) is reported with paired Wald 95% CI. Cohen's g is bounded on $[-0.50, +0.50]$ and saturates; read the Risk Difference for magnitude.*

### Key Findings (Independent Field Benchmark)
1. **Positive-Case Recall Is the Binding Constraint**: On the only independent benchmark in the repository, RiceKG attains 20.83% positive-case recall over 5 in-scope disease cases (micro-F1 29.00, 95% CI [9.5, 51.6]), against an aggregate exact match of 87.50%. Diagnostic efficacy on authentic field cases remains largely unproven.
2. **Every Supervised Baseline Scores Zero on Positive Cases**: All five ML classifiers attain 0.00% positive-case recall, having at most 5 positive training examples split across folds. Their aggregate accuracy is produced solely by predicting the majority `No_Diagnosis` class.
3. **Residual Failures Are Now Separable**: Following identifier normalization against `model.ALL_SYMPTOMS` (see `data/symptom_mapping.csv`), the remaining errors split into genuine vocabulary gaps — literature descriptors such as bacterial ooze and water-soaked lesions that the 45-term vocabulary does not model — and true Tier-2 rule-recall failures on partially observed cases. `results/field_failure_analysis.md` assigns a cause to each case.
4. **Negative Control Artifact**: 27 of 32 cases (84.4%) are out-of-scope emerging pathogens. Reporting aggregate exact match alone would conceal positive-case performance entirely, which is why the two are separated above.
5. **Statistical Power & MDE**: With $n=32$ and only 5 positive cases, the minimum detectable effect is $\pm 25.0$ percentage points. Non-significant comparisons reflect severe underpowering, not demonstrated equivalence.

---

## 3. Statistical Power & Minimum Detectable Effect Disclosure

- **Augmented Benchmark ($n=80$)**: $\text{MDE} = \pm 15.8\%$. Differences smaller than ~16 percentage points cannot be detected at $80\%$ power.
- **Field Benchmark ($n=32$)**: $\text{MDE} = \pm 25.0\%$. Differences smaller than ~25 percentage points cannot be detected at $80\%$ power.
- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.