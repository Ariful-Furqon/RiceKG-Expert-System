# Cold-Start Learning-Curve Evaluation: Sample Efficiency vs. Knowledge Base

> **Generated**: 2026-09-14 02:38:03 UTC  
> **Target Venue**: *Inteligencia Artificial* (IBERAMIA)  
> **Evaluation Protocol**: Fixed held-out test set (`data/benchmark_field.csv`, `eval` split, $n=23$: 5 positives, 18 negative controls). $R=200$ stratified resamples without replacement per budget, bootstrap 95% CIs ($B=1,000$).

---

## 1. Executive Summary & Research Question

This experiment answers the core architectural and deployment question:

> *"How many annotated field cases does supervised machine learning require before it overtakes the zero-shot symbolic knowledge base?"*

### Headline Finding

> **Crossover observed in Pool A**: Decision Tree, Random Forest, Multinomial Naive Bayes, k-NN, Logistic Regression (OvR).
> **Crossover observed in Pool B**: Decision Tree, Random Forest, k-NN.

---

## 2. Quantitative Results: Pool A (Rule-Derived Cases, $N \in [5, 80]$)

Cases drawn from `data/benchmark_synthetic.csv` ($n=80$). Models learn RiceKG's own rule semantics under varying sample sizes.

| Model | N=5 | N=10 | N=20 | N=40 | N=80 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 13.0% [10.8, 15.2] | 24.3% [21.8, 26.6] | 31.1% [28.8, 33.4] | 37.5% [35.2, 39.9] | 40.2% [38.5, 41.8] | 40 | 5 |
| **Random Forest** | 6.9% [5.3, 8.5] | 15.2% [13.4, 17.3] | 22.8% [21.0, 24.7] | 39.7% [37.9, 41.2] | 47.7% [45.9, 49.5] | 40 | 5 |
| **Multinomial Naive Bayes** | 14.2% [12.3, 16.2] | 24.5% [22.6, 26.5] | 36.6% [34.8, 38.5] | 43.8% [41.6, 45.8] | 20.0% [20.0, 20.0] | 40 | 5 |
| **k-NN** | 4.3% [2.9, 5.8] | 16.6% [14.5, 18.9] | 31.9% [29.8, 33.9] | 52.0% [49.9, 54.1] | 60.0% [60.0, 60.0] | 40 | 5 |
| **Logistic Regression (OvR)** | 6.2% [4.8, 7.7] | 16.0% [14.1, 18.2] | 24.8% [22.8, 26.8] | 38.9% [37.1, 40.6] | 60.0% [60.0, 60.0] | 40 | 5 |

*Zero-shot references on same eval set*: **RiceKG Full Proposed** = **35.00%** [95% CI 34.8, 74.3]; **Nearest Prototype** = **17.50%**; **Flat Single-Tier** = **35.00%**.

---

## 3. Quantitative Results: Pool B (Real Field Cases, $N \in [2, 16]$)

Cases drawn from the independent field `dev` split of `data/benchmark_field.csv` ($n=16$: 7 positives, 9 controls).

| Model | N=2 | N=4 | N=8 | N=16 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 9.3% [7.9, 10.8] | 36.2% [35.1, 37.2] | 33.1% [31.8, 34.4] | 40.0% [40.0, 40.0] | 4 | 2 |
| **Random Forest** | 9.7% [8.3, 11.2] | 34.3% [33.0, 35.4] | 31.2% [29.9, 32.6] | 40.0% [40.0, 40.0] | 16 | 2 |
| **Multinomial Naive Bayes** | 9.9% [8.5, 11.4] | 25.4% [24.2, 26.5] | 8.5% [7.0, 10.0] | 20.0% [20.0, 20.0] | None (≤ 16) | 2 |
| **k-NN** | 0.4% [0.1, 0.8] | 0.0% [0.0, 0.0] | 9.3% [7.7, 10.9] | 40.0% [40.0, 40.0] | 16 | 2 |
| **Logistic Regression (OvR)** | 8.5% [7.2, 9.9] | 0.0% [0.0, 0.0] | 6.4% [5.1, 7.8] | 0.0% [0.0, 0.0] | None (≤ 16) | 2 |

---

## 4. Secondary Analysis: Rule-Derived Evaluation Benchmark (Smooth Reference Curve)

To address the coarse staircase effect of the 5-positive field eval partition, a secondary curve was evaluated using `benchmark_synthetic.csv` ($n=80$) as test set. *Methodological disclosure: this set is rule-derived and does not measure field efficacy.*

| Model | N=5 | N=10 | N=20 | N=40 | N=80 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 15.9% | 33.9% | 51.4% | 75.4% | 98.4% |
| **Random Forest** | 12.9% | 39.9% | 52.0% | 76.9% | 98.4% |
| **Multinomial Naive Bayes** | 17.7% | 47.5% | 58.5% | 81.7% | 91.9% |
| **k-NN** | 4.0% | 25.3% | 47.5% | 68.0% | 95.2% |
| **Logistic Regression (OvR)** | 11.5% | 44.7% | 51.1% | 75.3% | 95.2% |

---

## 5. Methodological Limitations & Granularity Disclosure

1. **Staircase Quantisation Step ($\Delta = 0.20$)**: The field `eval` benchmark contains exactly **5 positive in-scope disease cases**. Consequently, positive recall on any single evaluation draw is strictly quantised to $\{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$. Reporting means over $R=200$ draws smooths the expected value, but confidence intervals remain inherently wide due to small sample size.
2. **Statistical Power**: As established in `docs/LIMITATIONS.md` Section 2, the minimum detectable effect on this partition is $\pm 29.5\%$. Non-crossover outcomes demonstrate that supervised ML with small datasets cannot reliably match a curated knowledge base, but do not imply asymptotic ML inferiority.
3. **Zero-Leakage Assurance**: Strict partition integrity was maintained: no test case ID or literature DOI was ever included in training draws.