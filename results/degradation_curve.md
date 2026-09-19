# Observation Occlusion Degradation Analysis

> **Generated**: 2026-09-19T01:27:43.955539+00:00  
> **Test Benchmark Scale**: $n=500$ cases per evaluation point  
> **Replication**: $R=20$ independent random draws per occlusion level  
> **Execution Time**: 33.77 seconds  

---

## 1. Experimental Overview & Methodological Bounds

This experiment subjects RiceKG, two knowledge-based reference baselines, and five supervised
machine learning classifiers to a controlled **observation-incompleteness degradation sweep**.
Canonical diagnostic antecedents are randomly masked at rates from $0.0$ (complete pathognomonic scouting)
to $0.8$ (severe partial observation where 80% of diagnostic signs are hidden).

> [!IMPORTANT]
> **Scientific Boundary**: This experiment measures robustness to symptom occlusion under the rule base's
> own vocabulary, **not field accuracy**. Test cases are generated from the same `RULE_REGISTRY` antecedents
> that the knowledge-based systems use, so the 0.0 column is 100% for RiceKG by construction.

Confidence intervals come from 20 seeds with $n=500$ generated cases per point, so the 0.20-step
quantisation of the 5-positive field `eval` split does not apply here.

RiceKG predictions are computed with set-containment solvers (`fast_predict_ricekg`,
`fast_predict_ricekg_possible`) whose outputs are checked against Pellet on sampled cases in
`tests/test_degradation_curve.py`; the sweep itself does not run the DL reasoner.

---

## 2. Positive-Case Recall (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 89.1 ± 1.5 | 78.0 ± 1.8 | 67.9 ± 2.4 | 57.5 ± 2.1 | 48.1 ± 2.1 | 39.4 ± 2.9 | 31.3 ± 2.0 | 25.1 ± 1.6 |
| **RiceKG (+ possible grade)** | 100.0 ± 0.0 | 96.0 ± 0.9 | 90.6 ± 1.3 | 84.6 ± 2.0 | 77.2 ± 2.3 | 69.0 ± 1.7 | 60.8 ± 2.7 | 52.8 ± 2.4 | 44.6 ± 2.0 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 89.1 ± 1.5 | 78.0 ± 1.8 | 67.9 ± 2.4 | 57.5 ± 2.1 | 48.1 ± 2.1 | 39.4 ± 2.9 | 31.3 ± 2.0 | 25.1 ± 1.6 |
| **Rule: Nearest Prototype** | 72.8 ± 2.3 | 77.0 ± 2.1 | 80.1 ± 1.9 | 80.9 ± 2.1 | 77.4 ± 2.1 | 70.8 ± 2.0 | 59.5 ± 2.0 | 43.8 ± 2.6 | 25.4 ± 2.5 |
| **Decision Tree** | 98.0 ± 0.9 | 96.4 ± 1.1 | 93.3 ± 1.6 | 89.1 ± 2.0 | 83.7 ± 2.4 | 76.2 ± 3.5 | 68.9 ± 3.7 | 60.0 ± 3.4 | 51.4 ± 3.6 |
| **Random Forest** | 99.2 ± 0.8 | 98.1 ± 0.9 | 96.2 ± 1.2 | 93.1 ± 1.2 | 88.0 ± 1.5 | 81.3 ± 1.6 | 73.0 ± 2.9 | 63.6 ± 3.3 | 53.6 ± 4.1 |
| **Multinomial Naive Bayes** | 100.0 ± 0.1 | 99.5 ± 0.5 | 98.3 ± 1.0 | 96.5 ± 1.1 | 94.0 ± 1.5 | 91.0 ± 2.0 | 87.3 ± 1.9 | 82.5 ± 1.9 | 78.2 ± 2.3 |
| **k-NN** | 97.5 ± 1.1 | 95.5 ± 1.3 | 92.5 ± 1.2 | 87.9 ± 1.7 | 81.2 ± 1.8 | 72.4 ± 2.3 | 61.8 ± 4.3 | 50.3 ± 4.3 | 39.6 ± 5.5 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.4 ± 0.5 | 96.5 ± 0.8 | 91.0 ± 1.2 | 81.4 ± 1.9 | 68.8 ± 2.2 | 52.7 ± 3.1 | 35.5 ± 2.5 | 19.2 ± 2.4 |

---

## 3. Micro-Average F1-Score (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 94.7 ± 0.8 | 88.6 ± 0.9 | 82.3 ± 1.5 | 74.8 ± 1.6 | 67.1 ± 1.9 | 59.1 ± 2.6 | 50.4 ± 2.0 | 42.5 ± 2.4 |
| **RiceKG (+ possible grade)** | 99.5 ± 0.3 | 97.6 ± 0.6 | 95.0 ± 0.8 | 92.0 ± 1.1 | 87.9 ± 1.2 | 82.8 ± 1.2 | 77.0 ± 1.5 | 70.5 ± 1.7 | 63.2 ± 2.1 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 94.7 ± 0.8 | 88.6 ± 0.9 | 82.3 ± 1.5 | 74.8 ± 1.6 | 67.1 ± 1.9 | 59.1 ± 2.6 | 50.4 ± 2.0 | 42.5 ± 2.4 |
| **Rule: Nearest Prototype** | 89.0 ± 0.9 | 90.5 ± 0.8 | 91.6 ± 0.8 | 91.6 ± 0.9 | 89.5 ± 1.0 | 85.6 ± 1.1 | 78.1 ± 1.1 | 65.1 ± 2.1 | 44.8 ± 3.0 |
| **Decision Tree** | 99.0 ± 0.5 | 98.2 ± 0.6 | 96.6 ± 1.0 | 94.4 ± 1.2 | 91.3 ± 1.4 | 86.8 ± 2.4 | 82.0 ± 2.6 | 75.6 ± 2.8 | 68.9 ± 3.3 |
| **Random Forest** | 99.6 ± 0.4 | 99.1 ± 0.4 | 98.2 ± 0.6 | 96.6 ± 0.6 | 93.9 ± 0.8 | 90.1 ± 0.9 | 84.8 ± 1.7 | 78.0 ± 2.1 | 69.5 ± 2.9 |
| **Multinomial Naive Bayes** | 97.6 ± 0.5 | 97.4 ± 0.5 | 96.8 ± 0.7 | 96.1 ± 0.7 | 94.9 ± 0.9 | 93.5 ± 1.1 | 91.6 ± 1.3 | 88.5 ± 1.0 | 86.1 ± 1.2 |
| **k-NN** | 98.8 ± 0.5 | 97.9 ± 0.6 | 96.4 ± 0.6 | 94.0 ± 0.8 | 90.0 ± 0.8 | 84.5 ± 1.1 | 76.9 ± 2.9 | 67.1 ± 2.9 | 56.2 ± 4.6 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.7 ± 0.2 | 98.4 ± 0.4 | 95.7 ± 0.6 | 90.4 ± 1.0 | 82.7 ± 1.4 | 70.7 ± 2.4 | 54.4 ± 2.5 | 33.7 ± 3.0 |

---

## 4. Micro-Average Precision (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **RiceKG (+ possible grade)** | 99.0 | 97.5 | 96.3 | 95.3 | 94.0 | 93.1 | 92.6 | 91.1 | 89.5 |
| **Rule: Flat Single-Tier** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **Rule: Nearest Prototype** | 80.1 | 82.8 | 85.5 | 87.9 | 89.3 | 90.8 | 91.9 | 92.4 | 91.3 |
| **Decision Tree** | 99.1 | 99.0 | 98.8 | 98.5 | 98.0 | 97.2 | 96.5 | 95.1 | 94.3 |
| **Random Forest** | 100.0 | 100.0 | 99.9 | 99.8 | 99.5 | 99.3 | 99.0 | 98.4 | 97.7 |
| **Multinomial Naive Bayes** | 95.3 | 95.1 | 94.6 | 94.3 | 93.5 | 93.2 | 93.0 | 91.5 | 91.1 |
| **k-NN** | 100.0 | 100.0 | 99.8 | 99.6 | 99.0 | 98.2 | 97.2 | 95.0 | 92.1 |
| **Logistic Regression (OvR)** | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | 99.9 | 99.9 | 99.8 | 99.5 |

---

## 5. Findings (computed from the tables above)

1. **Strict RiceKG loses recall under occlusion but not precision.** Positive recall falls from 100.0% at occlusion 0.0 to 67.9% at 0.3 and 25.1% at 0.8. Its lowest micro-precision across the sweep is 100.0%: it misses cases rather than returning wrong threats.
2. **Tier stratification does not change the diagnosed set.** The maximum recall difference between RiceKG and Flat Single-Tier over the sweep is 0.0 points. Tier-1 antecedents contain the Tier-2 antecedents, so any case that satisfies Tier 1 also satisfies Tier 2; the tiers change the reported grade, not which threats are returned.
3. **Supervised baselines are more robust on this benchmark.** Strict RiceKG recall is below every supervised baseline at 7 of 9 occlusion levels; at 0.8 the best one (Multinomial Naive Bayes) reaches 78.2%.
4. **The `possible` grade trades precision for recall.** With it enabled, recall at 0.3 is 84.6% (strict: 67.9%) and micro-precision is 95.3% (strict: 100.0%); at 0.8, recall is 44.6% and precision 89.5%.

---

## 6. Visual Degradation Trajectory

![Observation Occlusion Degradation Curve](figures/degradation_curve.png)
