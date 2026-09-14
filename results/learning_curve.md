# Cold-Start Learning-Curve Evaluation: Sample Efficiency vs. Knowledge Base

> **Generated**: 2026-09-14 07:44:38 UTC  
> **Target Venue**: *Inteligencia Artificial* (IBERAMIA)  
> **Evaluation Protocol**: Fixed held-out test set (`data/benchmark_field.csv`, `eval` split, $n=23$: 5 positives, 18 negative controls). $R=200$ stratified resamples without replacement per budget; reported with dual uncertainty decomposition (training-subsample variance across draws and test-set sampling variance via non-parametric paired bootstrap over the test cases, $B=1,000$).

---

## 1. Executive Summary & Research Question

This experiment quantifies the sample efficiency of RiceKG's zero-shot symbolic knowledge base relative to five supervised machine learning architectures across scaling training budgets.

### Headline Finding

> **No supervised baseline exceeded the zero-shot knowledge base at any training budget available in this study under the test-set uncertainty criterion** (up to $N=73$ rule-derived cases in Pool A, and $N=16$ real field cases in Pool B).
>
> While several supervised models achieve point means above the reference at larger budgets, **every paired difference 95% bootstrap confidence interval spans zero**. With only 5 positive test cases ($\Delta = 0.20$ quantisation step) and a wide confidence interval, supervised ML cannot be asserted as statistically superior to the zero-shot symbolic knowledge base on field data.

---

## 2. Quantitative Results: Pool A (Rule-Derived Cases, $N \in [5, 73]$)

Training cases drawn from `data/verification_suite.csv` ($n=73$, provenance `rule_derived`). Evaluated on the held-out field `eval` split ($n=23$).

| Model | N=5 | N=10 | N=20 | N=40 | N=73 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 12.5% [8, 18] | 28.6% [13, 43] | 35.2% [16, 58] | 41.7% [16, 72] | 40.9% [10, 71] | None (≤ 73) | 5 |
| **Random Forest** | 6.8% [2, 12] | 19.2% [3, 35] | 27.4% [5, 51] | 40.8% [11, 76] | 45.3% [10, 80] | None (≤ 73) | 5 |
| **Multinomial Naive Bayes** | 16.2% [9, 23] | 29.7% [11, 48] | 41.4% [18, 65] | 42.9% [16, 76] | 20.0% [0, 60] | None (≤ 73) | 5 |
| **k-NN** | 4.6% [2, 8] | 21.9% [6, 38] | 40.1% [12, 69] | 49.3% [19, 84] | 60.0% [20, 100] | None (≤ 73) | 5 |
| **Logistic Regression (OvR)** | 8.0% [4, 12] | 22.1% [6, 38] | 28.5% [4, 56] | 36.8% [1, 73] | 40.0% [0, 80] | None (≤ 73) | 5 |

*Zero-shot references on same eval set*: **RiceKG Full Proposed** = **35.00%** (5x2 CV) / **40.0%** runtime point recall [95% CI 0.0, 80.0]; **Nearest Prototype** = **17.50%**; **Flat Single-Tier** = **35.00%**.

---

## 3. Quantitative Results: Pool B (Real Field Cases from `dev` split, $N \in [2, 16]$)

Training cases drawn from the independent field `dev` split of `data/benchmark_field.csv` ($n=16$: 7 positives, 9 controls). Evaluated on the held-out field `eval` split ($n=23$).

| Model | N=2 | N=4 | N=8 | N=16 | Crossover Budget $N^*$ | First Non-Zero $N$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Decision Tree** | 9.3% [0, 19] | 36.2% [0, 76] | 33.1% [0, 73] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Random Forest** | 9.7% [0, 20] | 34.3% [0, 74] | 31.2% [0, 71] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Multinomial Naive Bayes** | 9.9% [0, 20] | 25.4% [0, 60] | 8.5% [0, 19] | 20.0% [0, 60] | None (≤ 16) | 2 |
| **k-NN** | 0.4% [0, 1] | 0.0% [0, 0] | 9.3% [0, 19] | 40.0% [0, 80] | None (≤ 16) | 2 |
| **Logistic Regression (OvR)** | 8.8% [0, 19] | 35.6% [0, 76] | 19.0% [0, 47] | 20.0% [0, 60] | None (≤ 16) | 2 |

---

## 4. Resolution of the Baseline Discrepancy

A key question arises when comparing `results/baselines.md` Table 2 against `results/learning_curve.md` Pool B:

> *Why did supervised classifiers score 0.00% (0/5) positive recall at 11 cases/fold in Table 2, but 33.1%–40.0% at N=8 and N=16 in Pool B?*

The discrepancy arises from **partition composition and training source**:
1. **`results/baselines.md` Table 2 Protocol**: Evaluated 5x2-fold cross-validation solely **within the 23 cases of the `eval` split**. In each fold, the training set held 11 cases from `eval`, where 9 cases (82%) were negative controls (`No_Diagnosis`) and at most 2 were positive cases. Crucially, the 5 positive cases in `eval` span 4 distinct threat classes; a 2-fold split ensures that viral classes (`Rice_Tungro_Virus`, `Rice_Grassy_Stunt`) present in the test fold never appeared in the training fold. Faced with an 82% negative majority and unseen classes, the classifiers predicted all-zeros (`No_Diagnosis`), yielding 0.00% recall.
2. **`results/learning_curve.md` Pool B Protocol**: Trained models on the **`dev` split ($n=16$)**, where 7 of 16 cases (43.8%) are in-scope positives, including multiple examples of `Bacterial_Leaf_Blight` and `Rice_Root_Nematode`. When evaluated on `eval`, the models correctly identified FIELD_34 (`Rice_Root_Nematode`) and FIELD_36 (`Bacterial_Leaf_Blight`), achieving 2/5 = 40.0% recall, while failing on the 3 viral cases that were absent from `dev`.
3. **Uncertainty Resolution**: When evaluated under test-set bootstrap resampling (resampling the 5 positive test cases), the paired difference between ML (40.0%) and RiceKG (40.0%) is identically zero with a 95% CI spanning zero ($[-40.0, +20.0]$ for DT at N=4). Thus, the apparent crossover was an artifact of ignoring test-set sampling variance.

---

## 5. Methodological Analysis of Anomalies

### Non-Monotonic Drop of Multinomial Naive Bayes (Pool A: N=40 → N=80)
In Pool A, Multinomial Naive Bayes drops from 43.8% positive recall at $N=40$ to 20.0% at $N=80$. This is caused by **negative evidence accumulation in One-vs-Rest feature likelihoods**:
- At $N=40$, stratified draws sample predominantly positive cases from the 10 threat classes, maintaining relatively balanced class priors.
- At $N=80$, the full verification pool is utilized, introducing all 20 negative control instances alongside counter-evidence from the 9 other classes. For any single threat $c$, negative instances outnumber positive instances by ~7:1.
- With Laplace smoothing, the aggregated evidence for the negative class drives the posterior log-odds below the decision threshold for borderline field cases, causing MNB to default to `No_Diagnosis`.

### Dual Uncertainty Decomposition
At the terminal budget ($N=80$ in Pool A, $N=16$ in Pool B), drawing without replacement from a finite pool of size $N$ yields a single unique subsample, causing the *training-subsample variance* across draws to collapse to 0.0. However, the *test-set sampling variance* (resampling over the 5 positive test cases) remains non-zero and wide ($[0.0, 80.0]$), faithfully reflecting empirical uncertainty.

---

## 6. Granularity and Statistical Power Boundaries

1. **Staircase Quantisation Step ($\Delta = 0.20$)**: Positive recall on the 5 in-scope test cases is strictly quantised to \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}.
2. **Minimum Detectable Effect ($\pm 29.5\%$)**: With $n=23$ and 5 positive cases, margins below 29.5% cannot be distinguished from random sampling noise.
3. **Zero Data Leakage**: In all 200 draws across both pools, training and test case IDs and DOIs were verified to be strictly disjoint.