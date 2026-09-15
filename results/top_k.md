# Top-k Differential Diagnosis & Ranking Analysis (PART 7)

> **Generated**: 2026-09-15T11:33:07.749592+00:00  
> **Evaluation Protocol**: Pre-fixed deterministic ordering key (Part 7-A), fair comparative baselines (Part 7-C), secondary diagnostic utility analysis.

---

## 1. Experimental Overview & Agronomic Purpose

In field pathology, scouting reports often document partial symptom combinations that do not satisfy
strict canonical pathognomonic thresholds. The **Top-k Differential Diagnosis** surfaces a prioritized
list of diagnostic hypotheses ranked strictly by evidence strength:

1. **Pre-fixed Ordering Key**: Grade ordinal (`confirmed` > `suspected` > `possible` > `weak`) → `antecedent_coverage` desc → `confidence` desc → `threat` name alphabetical asc.
2. **Safety & Specificity Safeguard**: Top-k naturally inflates sensitivity by construction. Therefore, every **Hit@k** figure is presented alongside its corresponding **Negative-Control False Alarm Rate (FAR@k)**.

---
## 2. Dataset: Field Benchmark (Dev Split) ($n=16$, 7 positives, 9 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 71.4% | 85.7% | 85.7% | 0.786 | 22.2% | 22.2% | 77.8% | 0.56 |
| **Rule: Nearest Prototype** | 100.0% | 100.0% | 100.0% | 1.000 | 88.9% | 88.9% | 11.1% | 2.31 |
| **Rule: Flat Single-Tier** | 57.1% | 57.1% | 57.1% | 0.571 | 0.0% | 0.0% | 100.0% | 0.25 |
| **Decision Tree** | 71.4% | 100.0% | 100.0% | 0.857 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Random Forest** | 57.1% | 71.4% | 71.4% | 0.643 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Multinomial Naive Bayes** | 28.6% | 28.6% | 28.6% | 0.286 | 100.0% | 100.0% | 0.0% | 1.69 |
| **k-NN** | 57.1% | 71.4% | 71.4% | 0.643 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Logistic Regression (OvR)** | 28.6% | 28.6% | 28.6% | 0.286 | 100.0% | 100.0% | 0.0% | 2.50 |

---

## 2. Dataset: Field Benchmark (Eval Split, Held-Out) ($n=23$, 5 positives, 18 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 40.0% | 80.0% | 100.0% | 0.667 | 50.0% | 50.0% | 50.0% | 0.96 |
| **Rule: Nearest Prototype** | 80.0% | 100.0% | 100.0% | 0.900 | 72.2% | 72.2% | 27.8% | 1.65 |
| **Rule: Flat Single-Tier** | 40.0% | 40.0% | 40.0% | 0.400 | 0.0% | 0.0% | 100.0% | 0.09 |
| **Decision Tree** | 20.0% | 40.0% | 40.0% | 0.300 | 100.0% | 100.0% | 0.0% | 2.52 |
| **Random Forest** | 20.0% | 40.0% | 40.0% | 0.300 | 100.0% | 100.0% | 0.0% | 2.78 |
| **Multinomial Naive Bayes** | 0.0% | 0.0% | 0.0% | 0.000 | 61.1% | 61.1% | 38.9% | 1.17 |
| **k-NN** | 20.0% | 40.0% | 60.0% | 0.367 | 100.0% | 100.0% | 0.0% | 2.61 |
| **Logistic Regression (OvR)** | 20.0% | 20.0% | 40.0% | 0.267 | 100.0% | 100.0% | 0.0% | 2.04 |

---

## 2. Dataset: Field Benchmark (Holdout Split, Tiers A-C) ($n=18$, 18 positives, 0 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 72.2% | 72.2% | 77.8% | 0.741 | n/a | n/a | n/a | 1.11 |
| **Rule: Nearest Prototype** | 77.8% | 88.9% | 88.9% | 0.833 | n/a | n/a | n/a | 1.78 |
| **Rule: Flat Single-Tier** | 27.8% | 27.8% | 27.8% | 0.278 | n/a | n/a | n/a | 0.33 |
| **Decision Tree** | 50.0% | 50.0% | 50.0% | 0.500 | n/a | n/a | n/a | 1.00 |
| **Random Forest** | 66.7% | 77.8% | 83.3% | 0.741 | n/a | n/a | n/a | 2.78 |
| **Multinomial Naive Bayes** | 61.1% | 83.3% | 94.4% | 0.759 | n/a | n/a | n/a | 2.89 |
| **k-NN** | 61.1% | 83.3% | 83.3% | 0.722 | n/a | n/a | n/a | 2.33 |
| **Logistic Regression (OvR)** | 66.7% | 83.3% | 94.4% | 0.787 | n/a | n/a | n/a | 3.00 |

_No negative controls in this split: false-alarm rate and specificity are undefined (n/a)._

---

## 2. Dataset: Deductive Verification Suite ($n=73$, 55 positives, 18 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 45.5% | 47.3% | 49.1% | 0.470 | 11.1% | 11.1% | 88.9% | 0.48 |
| **Rule: Nearest Prototype** | 60.0% | 65.5% | 65.5% | 0.627 | 50.0% | 50.0% | 50.0% | 1.38 |
| **Rule: Flat Single-Tier** | 14.6% | 14.6% | 14.6% | 0.145 | 0.0% | 0.0% | 100.0% | 0.11 |
| **Decision Tree** | 47.3% | 47.3% | 47.3% | 0.473 | 5.6% | 5.6% | 94.4% | 0.40 |
| **Random Forest** | 61.8% | 63.6% | 65.5% | 0.633 | 61.1% | 61.1% | 38.9% | 1.75 |
| **Multinomial Naive Bayes** | 54.5% | 61.8% | 63.6% | 0.588 | 100.0% | 100.0% | 0.0% | 2.26 |
| **k-NN** | 61.8% | 63.6% | 63.6% | 0.627 | 16.7% | 16.7% | 83.3% | 1.00 |
| **Logistic Regression (OvR)** | 60.0% | 63.6% | 63.6% | 0.618 | 100.0% | 100.0% | 0.0% | 3.00 |

---

## 3. Key Findings

1. **Top-k raises hits and false alarms together.** On the field `eval` split (5 positives, 18 negative controls), RiceKG moves from Hit@1 = 40.0% to Hit@3 = 100.0% (MRR 0.667), with a negative-control false-alarm rate of 50.0% at k=3 (specificity 50.0%). The additional candidates are `possible`-grade threats, which are also raised on negative controls, so the list is a screening aid rather than a diagnosis. The set-based rules without partial evidence (Flat Single-Tier) stay at Hit@3 = 40.0% with FAR@3 = 0.0%.
2. **Nearest Prototype** reaches Hit@3 = 100.0% with FAR@3 = 72.2%.
3. **Supervised baselines** (5 models, trained on one 2-fold split of the same field cases) range over Hit@3 = 0.0–60.0% and FAR@3 = 61.1–100.0%.
4. **Resolution.** With 5 positives, one case moves Hit@k by 20.0 points; none of the differences above is statistically established.
