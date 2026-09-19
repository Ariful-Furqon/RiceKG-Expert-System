# Probabilistic Reasoning Layer Evaluation (noisy-OR, PART 8)

> **Generated**: 2026-09-19T00:44:50.647195+00:00  
> **Headline Metric Preservation**: Strict RiceKG positive recall remains the headline metric.  
> **Target Venue**: *Inteligencia Artificial* (IBERAMIA) — contribution is transparent recall vs. false-alarm trade-off under partial observation.  

---

## 1. Experimental Overview & Methodological Bounds

This evaluation benchmarks the independent multi-label **noisy-OR probabilistic reasoning layer** against the strict symbolic RiceKG reasoner,
the coverage-threshold `possible` grade, and the ontology-free Nearest Prototype heuristic. Every parameter was elicited from literature
and locked prior to benchmark execution (commit `6174e8e`).

> [!WARNING]
> **Statistical Power Disclosure**: With only 5 in-scope positive disease cases in the held-out `eval` split, positive recall differences
> cannot be statistically established (MDE is $\pm 29.5\%$). No claim of demonstrated field diagnostic superiority is supported by the evidence.
> Furthermore, calibration cannot be validated on 5 positive cases; Brier scores and reliability tables are reported for diagnostic transparency only.

> [!NOTE]
> **Holdout Status**: As documented in Section 8-2.5 of `PROBABILISTIC_REASONING_TASK.md`, the holdout partition was exposed during Part 6 and Part 7.
> All holdout figures are labelled **development-exposed**.

---

## 2. Field Benchmark: Dev Split (n=16: 7 positives, 9 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 42.9% [0.0, 80.1] | 42.9% | 75.0% | 60.0 [0.0, 88.9] | 0.0% | 0.0% |
| **RiceKG + possible** | 71.4% [33.3, 100.0] | 57.1% | 68.8% | 66.7 [36.3, 88.9] | 22.2% | 22.2% |
| **noisy-OR (with gates)** | 100.0% [100.0, 100.0] | 71.4% | 43.8% | 45.2 [23.5, 66.7] | 77.8% | 77.8% |
| **noisy-OR (without gates)** | 100.0% [100.0, 100.0] | 71.4% | 43.8% | 45.2 [23.5, 66.7] | 77.8% | 77.8% |
| **Rule: Nearest Prototype** | 57.1% [20.0, 100.0] | 57.1% | 81.2% | 72.7 [33.3, 100.0] | 0.0% | 0.0% |

---

## 2. Field Benchmark: Eval Split (Held-Out, n=22: 5 positives, 17 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 80.0% [40.0, 100.0] | 80.0% | 95.5% | 88.9 [50.0, 100.0] | 0.0% | 0.0% |
| **RiceKG + possible** | 100.0% [100.0, 100.0] | 80.0% | 81.8% | 71.4 [40.0, 92.3] | 17.6% | 17.6% |
| **noisy-OR (with gates)** | 100.0% [100.0, 100.0] | 20.0% | 27.3% | 25.0 [9.1, 40.0] | 70.6% | 70.6% |
| **noisy-OR (without gates)** | 100.0% [100.0, 100.0] | 20.0% | 27.3% | 25.0 [9.1, 40.0] | 70.6% | 70.6% |
| **Rule: Nearest Prototype** | 80.0% [40.0, 100.0] | 40.0% | 86.4% | 72.7 [50.0, 100.0] | 0.0% | 0.0% |

---

## 2. Field Benchmark: Holdout Split (Development-Exposed, n=18 positives, 0 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 22.2% [5.6, 44.4] | 22.2% | 22.2% | 34.8 [9.5, 56.0] | n/a | n/a |
| **RiceKG + possible** | 72.2% [50.0, 88.9] | 66.7% | 66.7% | 70.3 [47.4, 88.9] | n/a | n/a |
| **noisy-OR (with gates)** | 94.4% [83.3, 100.0] | 61.1% | 61.1% | 68.0 [54.8, 83.0] | n/a | n/a |
| **noisy-OR (without gates)** | 94.4% [83.3, 100.0] | 61.1% | 61.1% | 68.0 [54.8, 83.0] | n/a | n/a |
| **Rule: Nearest Prototype** | 44.4% [22.2, 66.7] | 33.3% | 33.3% | 50.0 [28.6, 68.8] | n/a | n/a |

---

## 2. Deductive Verification Suite (Rule-Derived, n=73: 55 positives, 18 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 14.6% [5.5, 24.5] | 16.7% | 58.9% | 30.2 [13.0, 45.2] | 0.0% | 0.0% |
| **RiceKG + possible** | 49.1% [35.9, 62.7] | 44.4% | 69.9% | 67.5 [56.4, 76.9] | 11.1% | 11.1% |
| **noisy-OR (with gates)** | 65.5% [52.5, 77.5] | 55.6% | 67.1% | 71.5 [63.5, 80.0] | 33.3% | 33.3% |
| **noisy-OR (without gates)** | 65.5% [52.5, 77.5] | 55.6% | 67.1% | 71.5 [63.5, 80.0] | 33.3% | 33.3% |
| **Rule: Nearest Prototype** | 65.5% [52.5, 77.5] | 77.8% | 86.3% | 89.8 [83.9, 95.0] | 11.1% | 11.1% |

---

## 3. Top-k Differential Ranking on Eval Split (n=22)

| System | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 80.0% | 80.0% | 80.0% | 0.800 | 0.0% | 0.0% | 100.0% | 0.18 |
| **RiceKG + possible** | 80.0% | 100.0% | 100.0% | 0.900 | 17.6% | 17.6% | 82.3% | 0.41 |
| **noisy-OR (with gates)** | 80.0% | 100.0% | 100.0% | 0.900 | 35.3% | 35.3% | 64.7% | 1.50 |
| **noisy-OR (without gates)** | 80.0% | 100.0% | 100.0% | 0.900 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Rule: Nearest Prototype** | 80.0% | 100.0% | 100.0% | 0.900 | 76.5% | 76.5% | 23.5% | 1.59 |

---

## 4. Paired Significance against RiceKG Strict on Eval Split (n=22)

> **Minimum Detectable Effect**: $\pm 30.2\%$ accuracy ($\alpha=0.05, 80\%$ power).

| Comparison System | McNemar Test Method | Discordant Pairs | Stat ($\chi^2$) | Raw $p$-value | Holm $p$-value | Delta Acc (%) | Significant |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG + possible** | Exact Binomial Test (discordant n < 25) | 3 | 1.33 | 2.5000e-01 | 5.0000e-01 | +13.6% | No |
| **noisy-OR (with gates)** | Exact Binomial Test (discordant n < 25) | 15 | 13.07 | 6.1035e-05 | 2.4414e-04 | +68.2% | **Yes** |
| **noisy-OR (without gates)** | Exact Binomial Test (discordant n < 25) | 15 | 13.07 | 6.1035e-05 | 2.4414e-04 | +68.2% | **Yes** |
| **Rule: Nearest Prototype** | Exact Binomial Test (discordant n < 25) | 2 | 0.50 | 5.0000e-01 | 5.0000e-01 | +9.1% | No |

---

## 5. Calibration & Reliability Analysis on Eval Split (n=22)

> **Brier Score (Multi-Label)**: `0.1195` across 132 hypothesis evaluations.  
> **Disclaimer**: With 5 eval positives, calibration cannot be validated; do not claim calibration. The sample size is insufficient to reliably populate intermediate probability bins.

| Probability Bin Range | Hypothesis Count | Mean Predicted Probability | Observed Empirical Frequency |
|:---|:---:|:---:|:---:|
| `[0.0, 0.2)` | 95 | 0.1000 | 0.0000 |
| `[0.2, 0.4)` | 2 | 0.3382 | 0.0000 |
| `[0.4, 0.6)` | 0 | 0.0000 | 0.0000 |
| `[0.6, 0.8)` | 26 | 0.6241 | 0.0385 |
| `[0.8, 1.0)` | 9 | 0.9879 | 0.4444 |

---

## 6. Parameter Sensitivity Analysis (Protocol 8-D.1 & 8-D.3)

| Variant | Eval Recall (%) | Eval FAR (%) | Dev Recall (%) | Dev FAR (%) |
|:---|:---:|:---:|:---:|:---:|
| `baseline` | 100.0% | 70.6% | 100.0% | 77.8% |
| `p_minus_0.1` | 100.0% | 70.6% | 100.0% | 77.8% |
| `p_plus_0.1` | 100.0% | 70.6% | 100.0% | 77.8% |
| `alt_scale` | 100.0% | 70.6% | 100.0% | 77.8% |
| `leaks_half` | 100.0% | 70.6% | 100.0% | 77.8% |
| `leaks_double` | 100.0% | 35.3% | 71.4% | 11.1% |
| `quantitative_only` | 0.0% | 0.0% | 0.0% | 0.0% |
| **Parameter Span (excl. quant-only)** | **100.0–100.0%** | **35.3–70.6%** | **71.4–100.0%** | **11.1–77.8%** |

---

## 7. Findings (computed dynamically from the evaluation JSON)

1. **Recall versus False Alarm Trade-Off.** On the field `eval` split (5 positives, 17 controls), strict RiceKG achieves 80.0% any-hit recall (80.0% exact positive-case recall) with 0.0% false alarms. The `possible` grade reaches 100.0% any-hit recall (80.0% exact) with 17.6% false alarms. The noisy-OR layer at default threshold $\theta = 0.50$ attains 100.0% any-hit recall (20.0% exact single-label match due to multi-threat differential candidate generation), but incurs a 70.6% false-alarm rate on negative controls (70.6% without out-of-scope gates). Probabilistic scoring trades precision for sensitivity, operating as an aggressive screening instrument.
2. **Comparative Equivalence to the `possible` Grade.** On `dev`, noisy-OR achieves 100.0% any-hit recall and 77.8% FAR. At no threshold operating point does noisy-OR achieve higher recall than the coverage-threshold `possible` grade without a corresponding elevation in false alarm rate.
3. **Statistical Power & Significance Limits.** Paired McNemar testing between strict RiceKG and noisy-OR on `eval` exact-match yields $p = 6.1035e-05$ (Holm-corrected $p = 2.4414e-04$), reflecting the large difference in negative-control false alarms (strict exact-match: 95.5%, noisy-OR: 27.3%). However, with only 5 eval positive disease cases, the study has an analytical Minimum Detectable Effect of $\pm 30.2\%$ at $\alpha=0.05, 80\%$ power. Positive recall differences on this split cannot be statistically distinguished from chance.
4. **Parameter Sensitivity Spans.** Across conditional probability shifts ($p \pm 0.1$), the alternative qualitative scale, and background leak scaling ($\times 0.5$, $\times 2.0$), noisy-OR recall spans [100.0%, 100.0%] on `eval` and [71.4%, 100.0%] on `dev`, while FAR spans [35.3%, 70.6%] on `eval` and [11.1%, 77.8%] on `dev`. Because system differences fall within these parameter perturbation envelopes, comparisons between calibrated points are formally inconclusive.
5. **Holdout Partition (Development-Exposed).** On the 18 holdout cases (18 positives, 0 controls), noisy-OR reaches 61.1% recall compared to strict RiceKG's 22.2% and `possible` grade's 66.7%. As established in Protocol 8-2.5, this partition was previously evaluated during Part 6 and Part 7; all holdout figures are development-exposed.
6. **Quantitative-Only Ablation.** Restricting links strictly to quantitative literature sources (dropping qualitative scales) collapses recall to 0.0% on `eval` and 0.0% on `dev`, demonstrating that the rule and probabilistic layers fundamentally depend on qualitative clinical descriptions in published phytopathological monographs.

---

## 8. Trade-Off Visualisation

![Probabilistic Trade-Off Curve](figures/probabilistic_tradeoff.png)
