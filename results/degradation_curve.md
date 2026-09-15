# Observation Occlusion Degradation Analysis

> **Generated**: 2026-09-15T11:32:48.389532+00:00  
> **Test Benchmark Scale**: $n=500$ cases per evaluation point  
> **Replication**: $R=20$ independent random draws per occlusion level  
> **Execution Time**: 26.9 seconds  

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
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 78.2 ± 1.7 | 59.9 ± 2.5 | 44.4 ± 2.3 | 32.0 ± 1.3 | 21.4 ± 1.1 | 13.5 ± 1.2 | 7.2 ± 1.1 | 3.0 ± 0.8 |
| **RiceKG (+ possible grade)** | 100.0 ± 0.0 | 86.8 ± 1.9 | 75.9 ± 2.0 | 66.6 ± 2.5 | 59.4 ± 1.8 | 52.9 ± 1.9 | 46.5 ± 2.3 | 38.8 ± 2.3 | 33.8 ± 1.7 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 78.2 ± 1.7 | 59.9 ± 2.5 | 44.4 ± 2.3 | 32.0 ± 1.3 | 21.4 ± 1.1 | 13.5 ± 1.2 | 7.2 ± 1.1 | 3.0 ± 0.8 |
| **Rule: Nearest Prototype** | 69.2 ± 2.6 | 74.4 ± 2.5 | 77.0 ± 2.5 | 76.4 ± 2.4 | 74.2 ± 1.9 | 69.2 ± 2.6 | 59.9 ± 2.7 | 45.7 ± 2.6 | 28.4 ± 2.1 |
| **Decision Tree** | 97.6 ± 1.4 | 95.9 ± 1.1 | 92.7 ± 1.7 | 88.1 ± 1.9 | 81.8 ± 2.6 | 73.7 ± 3.4 | 65.4 ± 2.9 | 55.3 ± 3.6 | 46.5 ± 4.8 |
| **Random Forest** | 98.9 ± 1.0 | 97.8 ± 1.0 | 95.8 ± 1.4 | 92.6 ± 1.4 | 87.2 ± 1.3 | 78.5 ± 2.4 | 68.5 ± 2.8 | 55.8 ± 3.3 | 43.6 ± 3.6 |
| **Multinomial Naive Bayes** | 99.9 ± 0.1 | 99.0 ± 0.5 | 97.6 ± 0.9 | 95.6 ± 1.3 | 92.5 ± 1.3 | 88.7 ± 1.6 | 84.0 ± 1.5 | 77.0 ± 2.0 | 71.1 ± 2.2 |
| **k-NN** | 97.8 ± 1.4 | 95.8 ± 1.3 | 92.8 ± 1.7 | 87.8 ± 1.8 | 80.0 ± 1.7 | 68.7 ± 2.6 | 54.9 ± 3.3 | 39.5 ± 3.5 | 24.9 ± 3.7 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.2 ± 0.4 | 96.5 ± 0.9 | 91.0 ± 1.4 | 81.9 ± 1.4 | 68.7 ± 2.2 | 53.2 ± 2.9 | 36.0 ± 2.8 | 19.2 ± 1.6 |

---

## 3. Micro-Average F1-Score (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 88.8 ± 1.1 | 76.9 ± 1.9 | 64.1 ± 2.3 | 51.1 ± 1.9 | 37.7 ± 1.9 | 25.8 ± 2.0 | 14.9 ± 1.9 | 6.6 ± 1.5 |
| **RiceKG (+ possible grade)** | 99.7 ± 0.2 | 92.0 ± 1.1 | 85.7 ± 1.3 | 80.2 ± 1.6 | 75.7 ± 1.2 | 70.7 ± 1.5 | 65.1 ± 1.9 | 57.8 ± 2.1 | 50.9 ± 1.8 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 88.8 ± 1.1 | 76.9 ± 1.9 | 64.1 ± 2.3 | 51.1 ± 1.9 | 37.7 ± 1.9 | 25.8 ± 2.0 | 14.9 ± 1.9 | 6.6 ± 1.5 |
| **Rule: Nearest Prototype** | 87.7 ± 1.0 | 89.5 ± 0.9 | 90.4 ± 1.0 | 90.0 ± 0.9 | 88.6 ± 0.8 | 85.6 ± 1.4 | 79.4 ± 1.6 | 68.3 ± 1.8 | 50.3 ± 2.2 |
| **Decision Tree** | 98.6 ± 0.9 | 97.6 ± 0.8 | 95.9 ± 1.2 | 93.3 ± 1.5 | 89.7 ± 1.9 | 84.7 ± 2.3 | 79.2 ± 2.2 | 71.8 ± 2.9 | 64.4 ± 3.7 |
| **Random Forest** | 99.5 ± 0.5 | 99.0 ± 0.5 | 98.0 ± 0.7 | 96.3 ± 0.8 | 93.5 ± 0.8 | 88.4 ± 1.4 | 81.9 ± 1.8 | 72.5 ± 2.5 | 61.4 ± 3.4 |
| **Multinomial Naive Bayes** | 97.8 ± 0.4 | 97.3 ± 0.5 | 96.7 ± 0.6 | 95.8 ± 0.8 | 94.3 ± 0.8 | 92.3 ± 0.9 | 89.5 ± 1.1 | 85.4 ± 1.0 | 82.0 ± 1.2 |
| **k-NN** | 98.9 ± 0.7 | 98.0 ± 0.7 | 96.5 ± 0.9 | 93.8 ± 0.9 | 89.5 ± 0.9 | 82.4 ± 1.7 | 72.2 ± 2.4 | 58.4 ± 3.4 | 41.3 ± 4.4 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.6 ± 0.2 | 98.3 ± 0.4 | 95.6 ± 0.7 | 90.7 ± 0.8 | 82.6 ± 1.6 | 70.8 ± 2.5 | 54.9 ± 3.0 | 33.8 ± 1.9 |

---

## 4. Micro-Average Precision (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **RiceKG (+ possible grade)** | 99.4 | 88.2 | 80.8 | 76.0 | 73.1 | 71.4 | 70.5 | 69.1 | 68.9 |
| **Rule: Flat Single-Tier** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **Rule: Nearest Prototype** | 78.0 | 81.1 | 82.8 | 83.3 | 84.1 | 85.5 | 86.2 | 86.8 | 87.3 |
| **Decision Tree** | 98.6 | 98.2 | 97.8 | 97.2 | 96.5 | 95.5 | 94.6 | 93.2 | 92.0 |
| **Random Forest** | 100.0 | 99.9 | 99.9 | 99.8 | 99.5 | 99.2 | 99.0 | 98.9 | 98.7 |
| **Multinomial Naive Bayes** | 95.6 | 95.3 | 94.8 | 94.1 | 93.3 | 92.8 | 91.9 | 90.7 | 90.7 |
| **k-NN** | 99.9 | 99.9 | 99.8 | 99.5 | 99.3 | 98.8 | 98.3 | 97.8 | 96.3 |
| **Logistic Regression (OvR)** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | 99.9 | 99.9 | 99.7 |

---

## 5. Findings (computed from the tables above)

1. **Strict RiceKG collapses under occlusion.** Positive recall falls from 100.0% at occlusion 0.0 to 44.4% at 0.3 and 3.0% at 0.8. Its lowest micro-precision across the sweep is 100.0%: it misses cases rather than returning wrong threats.
2. **Tier stratification does not change the diagnosed set.** The maximum recall difference between RiceKG and Flat Single-Tier over the sweep is 0.0 points. Tier-1 antecedents contain the Tier-2 antecedents, so any case that satisfies Tier 1 also satisfies Tier 2; the tiers change the reported grade, not which threats are returned.
3. **Supervised baselines are more robust on this benchmark.** Strict RiceKG recall is below every supervised baseline at 8 of 9 occlusion levels; at 0.8 the best one (Multinomial Naive Bayes) reaches 71.1%.
4. **The `possible` grade trades precision for recall.** With it enabled, recall at 0.3 is 66.6% (strict: 44.4%) and micro-precision is 76.0% (strict: 100.0%); at 0.8, recall is 33.8% and precision 68.9%.

---

## 6. Visual Degradation Trajectory

![Observation Occlusion Degradation Curve](figures/degradation_curve.png)
