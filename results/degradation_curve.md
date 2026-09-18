# Observation Occlusion Degradation Analysis

> **Generated**: 2026-09-18T14:24:45.217407+00:00  
> **Test Benchmark Scale**: $n=500$ cases per evaluation point  
> **Replication**: $R=20$ independent random draws per occlusion level  
> **Execution Time**: 32.6 seconds  

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
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 78.9 ± 1.3 | 60.2 ± 2.6 | 44.4 ± 2.6 | 31.6 ± 1.8 | 21.5 ± 1.4 | 13.5 ± 1.4 | 7.2 ± 1.1 | 3.1 ± 0.8 |
| **RiceKG (+ possible grade)** | 100.0 ± 0.0 | 87.3 ± 1.4 | 76.4 ± 1.9 | 67.0 ± 2.3 | 59.2 ± 2.1 | 52.3 ± 2.2 | 46.2 ± 2.1 | 38.7 ± 2.4 | 33.4 ± 1.9 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 78.9 ± 1.3 | 60.2 ± 2.6 | 44.4 ± 2.6 | 31.6 ± 1.8 | 21.5 ± 1.4 | 13.5 ± 1.4 | 7.2 ± 1.1 | 3.1 ± 0.8 |
| **Rule: Nearest Prototype** | 69.2 ± 2.5 | 74.4 ± 2.8 | 77.0 ± 3.2 | 77.0 ± 2.2 | 74.7 ± 2.0 | 69.2 ± 2.4 | 60.1 ± 2.2 | 45.6 ± 2.3 | 28.5 ± 1.7 |
| **Decision Tree** | 97.9 ± 1.4 | 96.3 ± 1.3 | 93.7 ± 1.9 | 89.4 ± 2.2 | 83.0 ± 2.0 | 75.4 ± 2.8 | 66.9 ± 3.0 | 57.8 ± 3.1 | 49.0 ± 3.1 |
| **Random Forest** | 99.0 ± 0.9 | 98.1 ± 1.1 | 96.5 ± 1.3 | 93.3 ± 1.3 | 87.5 ± 1.9 | 79.3 ± 2.2 | 69.0 ± 2.2 | 56.6 ± 3.6 | 43.7 ± 5.1 |
| **Multinomial Naive Bayes** | 100.0 ± 0.1 | 98.9 ± 0.8 | 97.9 ± 1.0 | 95.8 ± 1.3 | 92.7 ± 1.6 | 89.1 ± 2.0 | 84.3 ± 1.6 | 77.2 ± 1.8 | 71.2 ± 2.1 |
| **k-NN** | 97.7 ± 1.3 | 95.8 ± 1.2 | 93.1 ± 1.3 | 88.2 ± 1.4 | 80.3 ± 2.5 | 69.0 ± 2.9 | 55.3 ± 4.2 | 39.7 ± 4.5 | 25.1 ± 4.1 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.2 ± 0.5 | 96.7 ± 0.9 | 91.3 ± 1.7 | 82.2 ± 2.1 | 69.0 ± 2.6 | 53.3 ± 3.1 | 36.0 ± 2.4 | 19.2 ± 1.6 |

---

## 3. Micro-Average F1-Score (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 ± 0.0 | 89.2 ± 0.8 | 77.1 ± 1.9 | 64.1 ± 2.6 | 50.7 ± 2.3 | 37.9 ± 2.2 | 25.6 ± 2.5 | 15.0 ± 1.9 | 6.8 ± 1.6 |
| **RiceKG (+ possible grade)** | 99.7 ± 0.2 | 92.3 ± 1.0 | 86.1 ± 1.2 | 80.7 ± 1.6 | 75.6 ± 1.4 | 70.2 ± 1.9 | 64.5 ± 1.7 | 57.6 ± 2.1 | 50.6 ± 2.0 |
| **Rule: Flat Single-Tier** | 100.0 ± 0.0 | 89.2 ± 0.8 | 77.1 ± 1.9 | 64.1 ± 2.6 | 50.7 ± 2.3 | 37.9 ± 2.2 | 25.6 ± 2.5 | 15.0 ± 1.9 | 6.8 ± 1.6 |
| **Rule: Nearest Prototype** | 87.7 ± 0.9 | 89.5 ± 1.1 | 90.4 ± 1.2 | 90.2 ± 0.8 | 88.8 ± 0.8 | 85.5 ± 1.2 | 79.6 ± 1.2 | 68.2 ± 1.6 | 50.6 ± 1.9 |
| **Decision Tree** | 98.9 ± 0.9 | 98.0 ± 0.9 | 96.6 ± 1.2 | 94.2 ± 1.6 | 90.6 ± 1.7 | 86.0 ± 2.0 | 80.3 ± 2.2 | 73.8 ± 2.6 | 66.7 ± 2.6 |
| **Random Forest** | 99.5 ± 0.4 | 99.0 ± 0.5 | 98.3 ± 0.7 | 96.6 ± 0.7 | 93.6 ± 1.0 | 88.8 ± 1.3 | 82.0 ± 1.6 | 73.0 ± 2.8 | 61.0 ± 4.7 |
| **Multinomial Naive Bayes** | 97.9 ± 0.3 | 97.4 ± 0.4 | 97.0 ± 0.6 | 96.1 ± 0.7 | 94.5 ± 0.8 | 92.8 ± 1.1 | 90.1 ± 1.1 | 85.9 ± 1.1 | 82.3 ± 1.1 |
| **k-NN** | 98.9 ± 0.7 | 98.0 ± 0.7 | 96.7 ± 0.7 | 94.1 ± 0.7 | 89.7 ± 1.4 | 82.6 ± 1.8 | 72.3 ± 3.0 | 58.3 ± 4.3 | 41.5 ± 4.8 |
| **Logistic Regression (OvR)** | 100.0 ± 0.0 | 99.6 ± 0.2 | 98.5 ± 0.4 | 95.8 ± 0.9 | 90.8 ± 1.2 | 82.7 ± 1.6 | 70.7 ± 2.6 | 54.8 ± 2.7 | 33.7 ± 2.6 |

---

## 4. Micro-Average Precision (%) vs. Occlusion Rate

| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **RiceKG (+ possible grade)** | 99.4 | 88.5 | 81.1 | 76.5 | 73.0 | 71.1 | 70.0 | 69.1 | 68.6 |
| **Rule: Flat Single-Tier** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| **Rule: Nearest Prototype** | 78.0 | 81.1 | 82.8 | 83.6 | 84.4 | 85.3 | 86.3 | 86.7 | 87.5 |
| **Decision Tree** | 99.0 | 98.8 | 98.6 | 98.0 | 97.3 | 96.7 | 95.6 | 95.0 | 93.7 |
| **Random Forest** | 99.9 | 99.8 | 99.8 | 99.6 | 99.4 | 99.2 | 98.8 | 99.0 | 98.4 |
| **Multinomial Naive Bayes** | 95.9 | 95.5 | 95.2 | 94.6 | 93.8 | 93.6 | 92.9 | 91.8 | 91.6 |
| **k-NN** | 99.9 | 99.9 | 99.8 | 99.6 | 99.3 | 98.8 | 98.1 | 97.5 | 96.4 |
| **Logistic Regression (OvR)** | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | 99.9 | 99.9 | 99.9 | 99.6 |

---

## 5. Findings (computed from the tables above)

1. **Strict RiceKG collapses under occlusion.** Positive recall falls from 100.0% at occlusion 0.0 to 44.4% at 0.3 and 3.1% at 0.8. Its lowest micro-precision across the sweep is 100.0%: it misses cases rather than returning wrong threats.
2. **Tier stratification does not change the diagnosed set.** The maximum recall difference between RiceKG and Flat Single-Tier over the sweep is 0.0 points. Tier-1 antecedents contain the Tier-2 antecedents, so any case that satisfies Tier 1 also satisfies Tier 2; the tiers change the reported grade, not which threats are returned.
3. **Supervised baselines are more robust on this benchmark.** Strict RiceKG recall is below every supervised baseline at 8 of 9 occlusion levels; at 0.8 the best one (Multinomial Naive Bayes) reaches 71.2%.
4. **The `possible` grade trades precision for recall.** With it enabled, recall at 0.3 is 67.0% (strict: 44.4%) and micro-precision is 76.5% (strict: 100.0%); at 0.8, recall is 33.4% and precision 68.6%.

---

## 6. Visual Degradation Trajectory

![Observation Occlusion Degradation Curve](figures/degradation_curve.png)
