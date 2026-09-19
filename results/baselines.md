# Comparative Baseline Evaluation & Paired Significance Testing

> **Generated**: 2026-09-19 01:40:53 UTC  
> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), and Holm–Bonferroni FWER step-down correction.

---

## 1. Verification suite (`verification_suite.csv`, $n=73$): not a comparison

The suite's cases and labels were authored from an earlier rule base, before the P0-5 revisions and the vocabulary extension; most of its positive cases cannot fire the current Tier-2 rules because the signs those rules require did not yet exist. A score on it measures agreement with that earlier rule base, and a nearest-prototype matcher built from the (barely changed) Tier-1 antecedents is favoured by construction. The suite is therefore used only as regression input: `results/ablation.md` checks that Pellet and set matching give identical output on it. Per-system figures remain in `results/baselines.json` under `verification_suite` for reproducibility and are not reported here.

---

## 2. Field benchmark, `eval` split (`benchmark_field.csv`, $n=22$), 5x2-fold protocol

The headline field figures are the single-run graded counts in `results/graded_evaluation.md`; RiceKG is not trained, so cross-validation only adds fold-partition noise to its figures. This section keeps the 5x2 protocol because the supervised baselines need training folds.

- **Dataset Provenance**: Peer-reviewed observed-case reports ($n=22$: 5 in-scope disease cases, 17 out-of-scope negative controls). Sources that are not case reports were excluded to `data/rejected_field_candidates.csv` with a stated reason.
- **Independence (downgraded)**: this partition was held out during P0-5 Steps 2-3, but its aggregate scores have now been observed across two rounds of rule revision. It is **development-informed**, not strictly held out. See `docs/LIMITATIONS.md` Section 2. A fresh partition is required before the manuscript cites an independent diagnostic figure.
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 3 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$30.2% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\Delta$ Acc [95% CI] | Cohen's $g$* |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **95.45 ± 4.55** | **85.00 ± 15.28** | **91.14 ± 9.08** | **[77.4, 97.6]** | — | — | Baseline Reference | — |
| RiceKG (Full + Possible) | Knowledge-Based / Semantic Web | 0 cases (cold start) | 81.82 ± 10.76 | 85.00 ± 15.28 | 70.23 ± 19.90 | [59.4, 81.7] | < 0.001 | **< 0.001*** | +13.6% [7.2, 20.0] | +0.50 |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 86.36 ± 7.33 | 40.83 ± 28.49 | 74.83 ± 10.23 | [63.4, 81.3] | 0.0020 | **0.0039*** | +9.1% [3.7, 14.5] | +0.50 |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 95.45 ± 4.55 | 85.00 ± 15.28 | 91.14 ± 9.08 | [77.4, 97.6] | 1.0000 | **1.0000** | +0.0% [0.0, 0.0] | +0.00 |
| Decision Tree | Supervised Machine Learning | 11 cases/fold | 74.55 ± 15.10 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +20.9% [13.3, 28.5] | +0.50 |
| Random Forest | Supervised Machine Learning | 11 cases/fold | 77.27 ± 9.32 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +18.2% [11.0, 25.4] | +0.50 |
| Multinomial Naive Bayes | Supervised Machine Learning | 11 cases/fold | 77.27 ± 9.32 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +18.2% [11.0, 25.4] | +0.50 |
| k-NN | Supervised Machine Learning | 11 cases/fold | 77.27 ± 9.32 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +18.2% [11.0, 25.4] | +0.50 |
| Logistic Regression (OvR) | Supervised Machine Learning | 11 cases/fold | 77.27 ± 9.32 | 0.00 ± 0.00 (0/5) | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +18.2% [11.0, 25.4] | +0.50 |

*Note: Aggregate exact match is dominated by the 17/22 negative control cases (77.3% of the benchmark), on which returning `No_Diagnosis` is correct. Positive-case recall over the 5 in-scope disease cases is reported separately and is the diagnostically meaningful column. Risk Difference (\Delta Acc) is reported with paired Wald 95% CI. Cohen's g is bounded on $[-0.50, +0.50]$ and saturates; read the Risk Difference for magnitude.*

### Key Findings (field `eval` split)
1. **Positive-case recall is the diagnostically meaningful figure**: RiceKG attains 85.00% positive-case recall over 5 in-scope disease cases (micro-F1 91.14, 95% CI [77.4, 97.6]), against an aggregate exact match of 95.45%. With 5 positive cases, diagnostic efficacy on field cases is not established.
2. **Every supervised baseline scores zero on positive cases**: all five ML classifiers attain 0.00% positive-case recall, having at most 5 positive training examples split across folds. Their aggregate accuracy comes from predicting the majority `No_Diagnosis` class.
3. **Per-case causes**: `results/field_failure_analysis.md` assigns a cause to every remaining failure.
4. **Negative Control Artifact**: 17 of 22 cases (77.3%) are out-of-scope emerging pathogens. Reporting aggregate exact match alone would conceal positive-case performance entirely, which is why the two are separated above.
5. **Statistical Power & MDE**: With $n=22$ and only 5 positive cases, the minimum detectable effect is $\pm 30.2$ percentage points. Non-significant comparisons reflect severe underpowering, not demonstrated equivalence.

### Companion: development split (not independent)

The `dev` split holds 16 cases (7 positive, 9 negative controls) and was visible during vocabulary and rule work. It is reported for transparency only and must not be cited as independent evidence.

| System / Model | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) |
|:---|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 87.50 | 75.00 | 84.14 |
| RiceKG (Full + Possible) | 75.00 | 75.00 | 70.94 |
| Rule: Nearest Prototype | 81.25 | 55.00 | 66.48 |
| Rule: Flat Single-Tier | 87.50 | 75.00 | 84.14 |
| Decision Tree | 56.25 | 31.67 | 33.05 |
| Random Forest | 55.00 | 5.83 | 8.00 |
| Multinomial Naive Bayes | 58.75 | 6.67 | 10.00 |
| k-NN | 51.25 | 0.00 | 0.00 |
| Logistic Regression (OvR) | 58.75 | 5.83 | 9.00 |


---

## 3. Statistical Power & Minimum Detectable Effect Disclosure

- **Field Benchmark, eval split ($n=22$, 5 positive cases)**: $\text{MDE} = \pm 30.2\%$.
- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.