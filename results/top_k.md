# Top-k Differential Diagnosis & Ranking Analysis (PART 7)

> **Generated**: 2026-09-19T01:58:56.357273+00:00  
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
| **Rule: Nearest Prototype** | 85.7% | 100.0% | 100.0% | 0.929 | 88.9% | 88.9% | 11.1% | 1.38 |
| **Rule: Flat Single-Tier** | 71.4% | 71.4% | 71.4% | 0.714 | 0.0% | 0.0% | 100.0% | 0.31 |
| **Decision Tree** | 71.4% | 100.0% | 100.0% | 0.857 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Random Forest** | 57.1% | 71.4% | 71.4% | 0.643 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Multinomial Naive Bayes** | 28.6% | 28.6% | 28.6% | 0.286 | 100.0% | 100.0% | 0.0% | 2.12 |
| **k-NN** | 57.1% | 71.4% | 71.4% | 0.643 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Logistic Regression (OvR)** | 28.6% | 28.6% | 28.6% | 0.286 | 100.0% | 100.0% | 0.0% | 2.50 |

_k-NN tie sensitivity: 8 of 16 held-out predictions have a distance tie at the 3rd-neighbour boundary. Over 20 training-row orders, k-NN spans Hit@1 57.1–57.1%, Hit@3 71.4–71.4% and FAR@3 100.0–100.0%. The table row uses `algorithm="brute"` with the original row order; k-NN figures are not comparable with other systems more finely than this span._

---

## 2. Dataset: Field Benchmark (Eval Split, Held-Out) ($n=22$, 5 positives, 17 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 80.0% | 100.0% | 100.0% | 0.900 | 17.6% | 17.6% | 82.3% | 0.41 |
| **Rule: Nearest Prototype** | 80.0% | 100.0% | 100.0% | 0.900 | 76.5% | 76.5% | 23.5% | 1.45 |
| **Rule: Flat Single-Tier** | 80.0% | 80.0% | 80.0% | 0.800 | 0.0% | 0.0% | 100.0% | 0.18 |
| **Decision Tree** | 40.0% | 40.0% | 40.0% | 0.400 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Random Forest** | 40.0% | 40.0% | 40.0% | 0.400 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Multinomial Naive Bayes** | 40.0% | 40.0% | 40.0% | 0.400 | 64.7% | 64.7% | 35.3% | 1.32 |
| **k-NN** | 40.0% | 40.0% | 40.0% | 0.400 | 100.0% | 100.0% | 0.0% | 3.00 |
| **Logistic Regression (OvR)** | 40.0% | 40.0% | 40.0% | 0.400 | 100.0% | 100.0% | 0.0% | 2.50 |

_k-NN tie sensitivity: 16 of 22 held-out predictions have a distance tie at the 3rd-neighbour boundary. Over 20 training-row orders, k-NN spans Hit@1 40.0–40.0%, Hit@3 40.0–40.0% and FAR@3 100.0–100.0%. The table row uses `algorithm="brute"` with the original row order; k-NN figures are not comparable with other systems more finely than this span._

---

## 2. Dataset: Field Benchmark (Holdout Split, Tiers A-C) ($n=18$, 18 positives, 0 negative controls)

| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **RiceKG (Full Proposed)** | 77.8% | 77.8% | 77.8% | 0.778 | n/a | n/a | n/a | 1.06 |
| **Rule: Nearest Prototype** | 77.8% | 83.3% | 83.3% | 0.806 | n/a | n/a | n/a | 1.44 |
| **Rule: Flat Single-Tier** | 66.7% | 66.7% | 66.7% | 0.667 | n/a | n/a | n/a | 0.72 |
| **Decision Tree** | 55.6% | 55.6% | 55.6% | 0.556 | n/a | n/a | n/a | 1.00 |
| **Random Forest** | 66.7% | 77.8% | 77.8% | 0.722 | n/a | n/a | n/a | 2.50 |
| **Multinomial Naive Bayes** | 66.7% | 83.3% | 94.4% | 0.787 | n/a | n/a | n/a | 2.89 |
| **k-NN** | 61.1% | 77.8% | 83.3% | 0.713 | n/a | n/a | n/a | 2.28 |
| **Logistic Regression (OvR)** | 72.2% | 83.3% | 94.4% | 0.815 | n/a | n/a | n/a | 3.00 |

_No negative controls in this split: false-alarm rate and specificity are undefined (n/a)._

_k-NN tie sensitivity: 12 of 18 held-out predictions have a distance tie at the 3rd-neighbour boundary. Over 20 training-row orders, k-NN spans Hit@1 44.4–61.1%, Hit@3 77.8–94.4% and FAR@3 n/a. The table row uses `algorithm="brute"` with the original row order; k-NN figures are not comparable with other systems more finely than this span._

---

## 3. Key Findings

1. **Top-k raises hits and false alarms together.** On the field `eval` split (5 positives, 17 negative controls), RiceKG moves from Hit@1 = 80.0% to Hit@3 = 100.0% (MRR 0.900), with a negative-control false-alarm rate of 17.6% at k=3 (specificity 82.3%). The additional candidates are `possible`-grade threats, which are also raised on negative controls, so the list is a screening aid rather than a diagnosis. The set-based rules without partial evidence (Flat Single-Tier) stay at Hit@3 = 80.0% with FAR@3 = 0.0%.
2. **Nearest Prototype** reaches Hit@3 = 100.0% with FAR@3 = 76.5%.
3. **Supervised baselines** (5 models, trained on one 2-fold split of the same field cases) range over Hit@3 = 40.0–40.0% and FAR@3 = 64.7–100.0%.
4. **Resolution.** With 5 positives, one case moves Hit@k by 20.0 points; none of the differences above is statistically established.
