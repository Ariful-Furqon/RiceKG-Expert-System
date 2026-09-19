# Cold-Start Learning-Curve Evaluation: Sample Efficiency vs. Knowledge Base

> **Generated**: 2026-09-19 01:31:42 UTC  
> **Target Venue**: *Inteligencia Artificial* (IBERAMIA)  
> **Evaluation Protocol**: Fixed held-out test set (`data/benchmark_field.csv`, `eval` split, $n=22$: 5 positives, 17 negative controls). $R=200$ stratified resamples without replacement per budget; reported with dual uncertainty decomposition (training-subsample variance across draws and test-set sampling variance via non-parametric paired bootstrap over the test cases, $B=1,000$).

---

## 1. Executive Summary & Research Question

This experiment quantifies the sample efficiency of RiceKG's zero-shot symbolic knowledge base relative to five supervised machine learning architectures across scaling training budgets.

### Headline Finding

> **No supervised baseline exceeded the zero-shot knowledge base at any training budget under the test-set uncertainty criterion** (up to $N=73$ rule-derived cases in Pool A and $N=16$ real field cases in Pool B). No model reaches RiceKG's 80.0% point recall at any budget; the best is Multinomial Naive Bayes with 44.5% at $N=40$ (Pool A). At the largest budgets, 5 of 10 model comparisons have a paired interval entirely below zero (RiceKG ahead). With only 5 positive test cases these intervals are wide.

---

## 2. Quantitative Results: Pool A (Rule-Derived Cases, $N \in [5, 73]$)

Training cases drawn from `data/verification_suite.csv` ($n=73$, provenance `rule_derived`). Evaluated on the held-out field `eval` split ($n=22$).

| Model | N=5 | N=10 | N=20 | N=40 | N=73 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 9.1% [4, 16] | 23.3% [9, 38] | 28.2% [7, 52] | 34.8% [8, 71] | 39.2% [9, 70] | None (≤ 73) | 5 |
| **Random Forest** | 4.2% [1, 8] | 12.1% [1, 28] | 14.8% [1, 38] | 25.3% [2, 61] | 28.4% [2, 67] | None (≤ 73) | 5 |
| **Multinomial Naive Bayes** | 13.3% [7, 22] | 26.3% [11, 46] | 36.7% [14, 60] | 44.5% [20, 71] | 40.0% [0, 80] | None (≤ 73) | 5 |
| **k-NN** | 3.7% [2, 6] | 16.5% [6, 28] | 24.9% [4, 54] | 33.1% [3, 70] | 40.0% [0, 80] | None (≤ 73) | 5 |
| **Logistic Regression (OvR)** | 6.2% [2, 10] | 14.6% [3, 29] | 16.1% [1, 44] | 18.4% [0, 55] | 20.0% [0, 60] | None (≤ 73) | 5 |

*Zero-shot references on same eval set*: **RiceKG Full Proposed** = **85.00%** (5x2 CV) / **80.0%** runtime point recall [95% CI 40.0, 100.0]; **Nearest Prototype** = **40.83%**; **Flat Single-Tier** = **85.00%**.

---

## 3. Quantitative Results: Pool B (Real Field Cases from `dev` split, $N \in [2, 16]$)

Training cases drawn from the independent field `dev` split of `data/benchmark_field.csv` ($n=16$: 7 positives, 9 controls). Evaluated on the held-out field `eval` split ($n=22$).

| Model | N=2 | N=4 | N=8 | N=16 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 8.4% [0, 17] | 31.6% [0, 66] | 31.5% [0, 65] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Random Forest** | 9.5% [0, 19] | 25.4% [0, 53] | 23.2% [0, 47] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Multinomial Naive Bayes** | 9.3% [0, 19] | 30.2% [0, 70] | 13.1% [0, 28] | 20.0% [0, 60] | None (≤ 16) | 2 |
| **k-NN** | 0.4% [0, 1] | 0.0% [0, 0] | 9.3% [0, 19] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Logistic Regression (OvR)** | 9.3% [0, 19] | 40.0% [0, 80] | 17.6% [0, 40] | 20.0% [0, 60] | None (≤ 16) | 2 |

---

## 4. Resolution of the Baseline Discrepancy

> *Why do supervised classifiers reach 0.00% positive recall under the 5x2-fold protocol of `results/baselines.md`, but up to 40.0% in Pool B?*

The discrepancy arises from **partition composition and training source**:
1. **`results/baselines.md` Table 2 Protocol**: 5x2-fold cross-validation solely **within the 22 cases of the `eval` split**. Each training fold holds about 11 cases, about 77% of them negative controls and only 2–3 positive cases spread over several threat classes, so a class present in the test fold is often absent from the training fold.
2. **`results/learning_curve.md` Pool B Protocol**: models are trained on the `dev` split ($n=16$, 7 positives) and tested on `eval`. At $N=16$ they reach 20.0–40.0% positive recall, against RiceKG's 80.0%.
3. **Uncertainty**: at $N=16$ the paired test-set bootstrap differences (model − RiceKG, 95% CI) are Decision Tree -40.7 [-80.0, 0.0]; Random Forest -40.7 [-80.0, 0.0]; Multinomial Naive Bayes -60.6 [-100.0, -20.0]; k-NN -40.7 [-80.0, 0.0]; Logistic Regression (OvR) -60.6 [-100.0, -20.0].

---

## 5. Methodological Notes

Multinomial Naive Bayes falls from 44.5% at $N=40$ to 40.0% at $N=73$ in Pool A; a change of this size lies well inside the test-set interval and is not interpreted.

### Dual Uncertainty Decomposition
At the terminal budget ($N=73$ in Pool A, $N=16$ in Pool B), drawing without replacement from a finite pool of size $N$ yields a single unique subsample, so the *training-subsample variance* across draws collapses to 0.0. The *test-set sampling variance* (resampling over the 5 positive test cases) stays wide, e.g. [9.2, 70.0] for the Decision Tree in Pool A.

---

## 6. Granularity and Statistical Power Boundaries

1. **Staircase Quantisation Step ($\Delta = 0.20$)**: Positive recall on the 5 in-scope test cases takes only multiples of 20%.
2. **Minimum Detectable Effect ($\pm 30.2\%$)**: With $n=22$ and 5 positive cases, margins below 30.2% cannot be distinguished from random sampling noise (`results/baselines.json`).
3. **Zero Data Leakage**: In all 200 draws across both pools, training and test case IDs and DOIs were verified to be strictly disjoint.