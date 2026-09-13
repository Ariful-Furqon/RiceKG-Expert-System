# Comparative Baseline Evaluation & Paired Significance Testing

> **Generated**: 2026-09-13 03:52:00 UTC  
> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), and Holm–Bonferroni FWER step-down correction.

---

## 1. Synthetic Verification Benchmark (`benchmark_synthetic.csv`, $n=80$)

- **Dataset Provenance**: Rule-derived cases ($n=80$, multi-threat composites).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 16 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$15.8% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Effect Size ($\Delta$ Acc / Cohen's $g$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **92.50 ± 2.24** | **96.19 ± 1.15** | **[94.8, 97.4]** | — | — | Baseline Reference |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 72.50 ± 2.24 | 86.65 ± 1.37 | [84.5, 88.7] | < 0.001 | **< 0.001*** | +20.0% (g=+0.44) |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 92.50 ± 2.24 | 96.19 ± 1.15 | [94.8, 97.4] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| Decision Tree | Supervised Machine Learning | 40 cases/fold | 55.50 ± 6.40 | 72.04 ± 5.46 | [69.0, 75.2] | < 0.001 | **< 0.001*** | +37.0% (g=+0.44) |
| Random Forest | Supervised Machine Learning | 40 cases/fold | 55.50 ± 9.80 | 67.56 ± 8.64 | [64.2, 71.3] | < 0.001 | **< 0.001*** | +37.0% (g=+0.47) |
| Multinomial Naive Bayes | Supervised Machine Learning | 40 cases/fold | 63.75 ± 9.17 | 78.24 ± 6.89 | [74.2, 81.5] | < 0.001 | **< 0.001*** | +28.8% (g=+0.44) |
| k-NN | Supervised Machine Learning | 40 cases/fold | 63.75 ± 7.93 | 69.73 ± 6.99 | [66.1, 73.7] | < 0.001 | **< 0.001*** | +28.8% (g=+0.44) |
| Logistic Regression (OvR) | Supervised Machine Learning | 40 cases/fold | 57.75 ± 10.69 | 69.01 ± 9.10 | [65.5, 72.8] | < 0.001 | **< 0.001*** | +34.8% (g=+0.48) |

*Note: Asterisk (\*) indicates statistically significant difference vs RiceKG after Holm-Bonferroni correction ($\alpha = 0.05$). Positive $\Delta$ Acc indicates RiceKG outperforms the baseline.*

### Key Findings (Synthetic Benchmark)
1. **Cold-Start Asymmetry**: Supervised ML models trained on 40 cases/fold achieve 55.50% to 63.75% exact match because 16 rare multi-threat combinations appear only once. RiceKG requires **zero training data** and achieves 92.50% exact match ($p < 0.001$ across all ML baselines).
2. **Rule Stratification Identity**: The unstratified single-tier rule baseline (*Flat Single-Tier*) achieves identical numerical accuracy to Full RiceKG on this benchmark, corroborating the P0-2 ablation finding that tier stratification provides clinical specificity/screening grading rather than an empirical accuracy bump.

---

## 2. Independent Peer-Reviewed Field Benchmark (`benchmark_field.csv`, $n=32$)

- **Dataset Provenance**: Authentic literature case series from APS *Plant Disease* Disease Notes ($n=32$).
- **Cross-Validation Split Strategy**: `KFold(n_splits=2) [Fallback: 3 rare combinations have n=1]`.
- **Minimum Detectable Effect (MDE)**: $\pm$25.0% accuracy ($\alpha=0.05, 1-\beta=0.80$).

| System / Model | Paradigm | Training Budget | Exact Match (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Effect Size ($\Delta$ Acc / Cohen's $g$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | Knowledge-Based / Semantic Web | **0 cases (cold start)** | **84.38 ± 5.04** | **0.00 ± 0.00** | **[0.0, 0.0]** | — | — | Baseline Reference |
| Rule: Nearest Prototype | Knowledge-Based / Semantic Web | 0 cases (cold start) | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| Rule: Flat Single-Tier | Knowledge-Based / Semantic Web | 0 cases (cold start) | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| Decision Tree | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| Random Forest | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| Multinomial Naive Bayes | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |
| k-NN | Supervised Machine Learning | 16 cases/fold | 66.88 ± 33.78 | 0.00 ± 0.00 | [0.0, 0.0] | < 0.001 | **< 0.001*** | +17.5% (g=+0.50) |
| Logistic Regression (OvR) | Supervised Machine Learning | 16 cases/fold | 84.38 ± 5.04 | 0.00 ± 0.00 | [0.0, 0.0] | 1.0000 | **1.0000** | +0.0% (g=+0.00) |

### Key Findings (Independent Field Benchmark)
1. **Controlled Vocabulary Bottleneck**: As documented in `docs/LIMITATIONS.md`, authentic literature cases describe traits outside the closed 45-symptom vocabulary. When symptoms fail to map, both RiceKG and the ML classifiers default to `No_Diagnosis` (all zeros).
2. **Negative Control Specificity**: All systems achieve 84.38% exact match on the field benchmark because 27 of the 32 cases are true negative controls (out-of-scope emerging pathogens correctly rejected).
3. **Statistical Equivalence vs Power**: With $n=32$, the minimum detectable effect is $\pm 25.0$ percentage points. The lack of statistically significant difference between RiceKG and ML baselines ($p=1.000$) reflects vocabulary gating rather than proof of true parity.

---

## 3. Statistical Power & Minimum Detectable Effect Disclosure

- **Synthetic Benchmark ($n=80$)**: $\text{MDE} = \pm 15.8\%$. Differences smaller than ~16 percentage points cannot be detected at $80\%$ power.
- **Field Benchmark ($n=32$)**: $\text{MDE} = \pm 25.0\%$. Differences smaller than ~25 percentage points cannot be detected at $80\%$ power.
- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.