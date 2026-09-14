<!-- GENERATED FILE — DO NOT EDIT BY HAND -->
<!-- Regenerate with: python analysis/build_results_index.py -->
<!-- Wired into: make reproduce, CI (check_readme_consistency.py) -->

# Results Index

Auto-generated on 2026-09-14T05:16:09Z from `results/*.json`.
Each row maps a manuscript claim to the command that produces it and the
source artifact that stores the value. Edit
`analysis/build_results_index.py` to change what is indexed.

| Manuscript claim | Command | Source artifact | Value |
|---|---|---|---|
| RiceKG field positive-case recall | `python baselines/run_baselines.py` | `results/baselines.json` | 35.00% |
| RiceKG field exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 86.82% |
| RiceKG field micro-F1 [95% CI] | `python baselines/run_baselines.py` | `results/baselines.json` | 40.67 [34.8, 74.3] |
| Nearest Prototype field positive-case recall | `python baselines/run_baselines.py` | `results/baselines.json` | 17.50% |
| Nearest Prototype field exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 73.94% |
| Nearest Prototype field micro-F1 | `python baselines/run_baselines.py` | `results/baselines.json` | 43.29 |
| RiceKG synthetic exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 60.00% |
| Field benchmark positive case count | `python baselines/run_baselines.py` | `results/baselines.json` | 5 |
| Field benchmark negative control count | `python baselines/run_baselines.py` | `results/baselines.json` | 18 |
| Decision Tree field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 10.00% |
| Random Forest field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Multinomial Naive Bayes field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| k-NN field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Logistic Regression (OvR) field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Ablation: full exact match (synthetic) | `python ablation.py` | `results/ablation.json` | 60.00% |
| Ablation: full multi-label accuracy (synthetic) | `python ablation.py` | `results/ablation.json` | 95.12% |
| Ablation: full positive recall (synthetic) | `python ablation.py` | `results/ablation.json` | 52.50% |
| Ablation: tier1_only exact match (synthetic) | `python ablation.py` | `results/ablation.json` | 32.50% |
| Ablation: tier1_only multi-label accuracy (synthetic) | `python ablation.py` | `results/ablation.json` | 91.00% |
| Ablation: tier1_only positive recall (synthetic) | `python ablation.py` | `results/ablation.json` | 10.00% |
| Ablation: tier2_only exact match (synthetic) | `python ablation.py` | `results/ablation.json` | 55.00% |
| Ablation: tier2_only multi-label accuracy (synthetic) | `python ablation.py` | `results/ablation.json` | 94.62% |
| Ablation: tier2_only positive recall (synthetic) | `python ablation.py` | `results/ablation.json` | 47.50% |
| Ablation: flat_rules exact match (synthetic) | `python ablation.py` | `results/ablation.json` | 60.00% |
| Ablation: flat_rules multi-label accuracy (synthetic) | `python ablation.py` | `results/ablation.json` | 95.12% |
| Ablation: flat_rules positive recall (synthetic) | `python ablation.py` | `results/ablation.json` | 52.50% |
| Ablation: no_reasoner exact match (synthetic) | `python ablation.py` | `results/ablation.json` | 60.00% |
| Ablation: no_reasoner multi-label accuracy (synthetic) | `python ablation.py` | `results/ablation.json` | 95.12% |
| Ablation: no_reasoner positive recall (synthetic) | `python ablation.py` | `results/ablation.json` | 52.50% |
| Learning-curve crossover detected (Pool A (synthetic)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| Learning-curve crossover detected (Pool B (field dev)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| LC zero-shot reference: RiceKG (Full Proposed) positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 35.00% |
| LC zero-shot reference: Rule: Flat Single-Tier positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 35.00% |
| LC zero-shot reference: Rule: Nearest Prototype positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 17.50% |

---
_This file is produced by `analysis/build_results_index.py` and validated by `analysis/check_readme_consistency.py`. A stale or missing index fails the CI build._
