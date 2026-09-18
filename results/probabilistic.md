# Probabilistic Reasoning Layer Evaluation (noisy-OR, PART 8)

> **Generated**: 2026-09-18T14:23:27.909402+00:00  
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
| **RiceKG strict** | 57.1% [16.7, 100.0] | 57.1% | 81.2% | 72.7 [28.6, 100.0] | 0.0% | 0.0% |
| **RiceKG + possible** | 85.7% [50.0, 100.0] | 71.4% | 75.0% | 75.0 [50.0, 94.1] | 22.2% | 25.0% |
| **noisy-OR (with gates)** | 100.0% [100.0, 100.0] | 28.6% | 18.8% | 33.3 [18.2, 47.6] | 88.9% | 100.0% |
| **noisy-OR (without gates)** | 100.0% [100.0, 100.0] | 28.6% | 18.8% | 33.3 [18.2, 47.6] | 88.9% | 100.0% |
| **Rule: Nearest Prototype** | 57.1% [16.7, 100.0] | 28.6% | 68.8% | 61.5 [25.0, 84.2] | 0.0% | 0.0% |

---

## 2. Field Benchmark: Eval Split (Held-Out, n=22: 5 positives, 17 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 40.0% [0.0, 100.0] | 40.0% | 86.4% | 57.1 [0.0, 100.0] | 0.0% | 0.0% |
| **RiceKG + possible** | 100.0% [100.0, 100.0] | 40.0% | 50.0% | 40.0 [18.2, 58.1] | 47.1% | 53.3% |
| **noisy-OR (with gates)** | 100.0% [100.0, 100.0] | 0.0% | 22.7% | 23.3 [9.1, 34.1] | 70.6% | 80.0% |
| **noisy-OR (without gates)** | 100.0% [100.0, 100.0] | 0.0% | 22.7% | 23.3 [9.1, 34.1] | 70.6% | 80.0% |
| **Rule: Nearest Prototype** | 100.0% [100.0, 100.0] | 20.0% | 77.3% | 58.8 [40.0, 80.0] | 5.9% | 6.7% |

---

## 2. Field Benchmark: Holdout Split (Development-Exposed, n=18 positives, 0 controls)

| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG strict** | 27.8% [5.6, 50.0] | 27.8% | 27.8% | 41.7 [10.5, 62.1] | n/a | n/a |
| **RiceKG + possible** | 77.8% [55.6, 94.4] | 66.7% | 66.7% | 73.7 [55.0, 91.4] | n/a | n/a |
| **noisy-OR (with gates)** | 94.4% [83.3, 100.0] | 55.6% | 55.6% | 64.2 [51.7, 79.1] | n/a | n/a |
| **noisy-OR (without gates)** | 94.4% [83.3, 100.0] | 55.6% | 55.6% | 64.2 [51.7, 79.1] | n/a | n/a |
| **Rule: Nearest Prototype** | 50.0% [27.8, 72.2] | 38.9% | 38.9% | 56.2 [33.3, 76.5] | n/a | n/a |

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
| **RiceKG strict** | 40.0% | 40.0% | 40.0% | 0.400 | 0.0% | 0.0% | 100.0% | 0.09 |
| **RiceKG + possible** | 40.0% | 80.0% | 100.0% | 0.667 | 47.1% | 47.1% | 52.9% | 0.91 |
| **noisy-OR (with gates)** | 80.0% | 80.0% | 100.0% | 0.867 | 64.7% | 64.7% | 35.3% | 2.18 |
| **noisy-OR (without gates)** | 80.0% | 80.0% | 100.0% | 0.867 | 88.2% | 88.2% | 11.8% | 2.73 |
| **Rule: Nearest Prototype** | 80.0% | 100.0% | 100.0% | 0.900 | 70.6% | 70.6% | 29.4% | 1.64 |

---

## 4. Paired Significance against RiceKG Strict on Eval Split (n=22)

> **Minimum Detectable Effect**: $\pm 30.2\%$ accuracy ($\alpha=0.05, 80\%$ power).

| Comparison System | McNemar Test Method | Discordant Pairs | Stat ($\chi^2$) | Raw $p$-value | Holm $p$-value | Delta Acc (%) | Significant |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG + possible** | Exact Binomial Test (discordant n < 25) | 8 | 6.12 | 7.8125e-03 | 1.5625e-02 | +36.4% | **Yes** |
| **noisy-OR (with gates)** | Exact Binomial Test (discordant n < 25) | 14 | 12.07 | 1.2207e-04 | 4.8828e-04 | +63.6% | **Yes** |
| **noisy-OR (without gates)** | Exact Binomial Test (discordant n < 25) | 14 | 12.07 | 1.2207e-04 | 4.8828e-04 | +63.6% | **Yes** |
| **Rule: Nearest Prototype** | Exact Binomial Test (discordant n < 25) | 2 | 0.50 | 5.0000e-01 | 5.0000e-01 | +9.1% | No |

---

## 5. Calibration & Reliability Analysis on Eval Split (n=22)

> **Brier Score (Multi-Label)**: `0.1491` across 132 hypothesis evaluations.  
> **Disclaimer**: With 5 eval positives, calibration cannot be validated; do not claim calibration. The sample size is insufficient to reliably populate intermediate probability bins.

| Probability Bin Range | Hypothesis Count | Mean Predicted Probability | Observed Empirical Frequency |
|:---|:---:|:---:|:---:|
| `[0.0, 0.2)` | 94 | 0.1000 | 0.0000 |
| `[0.2, 0.4)` | 0 | 0.0000 | 0.0000 |
| `[0.4, 0.6)` | 0 | 0.0000 | 0.0000 |
| `[0.6, 0.8)` | 22 | 0.6187 | 0.0000 |
| `[0.8, 1.0)` | 16 | 0.9733 | 0.3125 |

---

## 6. Parameter Sensitivity Analysis (Protocol 8-D.1 & 8-D.3)

| Variant | Eval Recall (%) | Eval FAR (%) | Dev Recall (%) | Dev FAR (%) |
|:---|:---:|:---:|:---:|:---:|
| `baseline` | 100.0% | 70.6% | 100.0% | 88.9% |
| `p_minus_0.1` | 100.0% | 70.6% | 100.0% | 88.9% |
| `p_plus_0.1` | 100.0% | 70.6% | 100.0% | 88.9% |
| `alt_scale` | 100.0% | 70.6% | 100.0% | 88.9% |
| `leaks_half` | 100.0% | 70.6% | 100.0% | 88.9% |
| `leaks_double` | 100.0% | 35.3% | 71.4% | 11.1% |
| `quantitative_only` | 0.0% | 0.0% | 0.0% | 0.0% |
| **Parameter Span (excl. quant-only)** | **100.0–100.0%** | **35.3–70.6%** | **71.4–100.0%** | **11.1–88.9%** |

---

## 7. Findings (computed dynamically from the evaluation JSON)

1. **Recall versus False Alarm Trade-Off.** On the field `eval` split (5 positives, 17 controls), strict RiceKG achieves 40.0% any-hit recall (40.0% exact positive-case recall) with 0.0% false alarms. The `possible` grade reaches 100.0% any-hit recall (40.0% exact) with 47.1% false alarms. The noisy-OR layer at default threshold $\theta = 0.50$ attains 100.0% any-hit recall (0.0% exact single-label match due to multi-threat differential candidate generation), but incurs a 70.6% false-alarm rate on negative controls (70.6% without out-of-scope gates). Probabilistic scoring trades precision for sensitivity, operating as an aggressive screening instrument.
2. **Comparative Equivalence to the `possible` Grade.** On `dev`, noisy-OR achieves 100.0% any-hit recall and 88.9% FAR. At no threshold operating point does noisy-OR achieve higher recall than the coverage-threshold `possible` grade without a corresponding elevation in false alarm rate.
3. **Statistical Power & Significance Limits.** Paired McNemar testing between strict RiceKG and noisy-OR on `eval` exact-match yields $p = 1.2207e-04$ (Holm-corrected $p = 4.8828e-04$), reflecting the large difference in negative-control false alarms (strict exact-match: 86.4%, noisy-OR: 22.7%). However, with only 5 eval positive disease cases, the study has an analytical Minimum Detectable Effect of $\pm 30.2\%$ at $\alpha=0.05, 80\%$ power. Positive recall differences on this split cannot be statistically distinguished from chance.
4. **Parameter Sensitivity Spans.** Across conditional probability shifts ($p \pm 0.1$), the alternative qualitative scale, and background leak scaling ($\times 0.5$, $\times 2.0$), noisy-OR recall spans [100.0%, 100.0%] on `eval` and [71.4%, 100.0%] on `dev`, while FAR spans [35.3%, 70.6%] on `eval` and [11.1%, 88.9%] on `dev`. Because system differences fall within these parameter perturbation envelopes, comparisons between calibrated points are formally inconclusive.
5. **Holdout Partition (Development-Exposed).** On the 18 holdout cases (18 positives, 0 controls), noisy-OR reaches 55.6% recall compared to strict RiceKG's 27.8% and `possible` grade's 66.7%. As established in Protocol 8-2.5, this partition was previously evaluated during Part 6 and Part 7; all holdout figures are development-exposed.
6. **Quantitative-Only Ablation.** Restricting links strictly to quantitative literature sources (dropping qualitative scales) collapses recall to 0.0% on `eval` and 0.0% on `dev`, demonstrating that the rule and probabilistic layers fundamentally depend on qualitative clinical descriptions in published phytopathological monographs.

---

## 8. Trade-Off Visualisation

![Probabilistic Trade-Off Curve](figures/probabilistic_tradeoff.png)
