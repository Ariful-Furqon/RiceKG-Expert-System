<!-- GENERATED FILE — DO NOT EDIT BY HAND -->
<!-- content-sha256: a9e4bfb8abe04e4c5da1a5370f4b371dc0e21010e0632c1beefd63a6e74fcb1a -->
<!-- Regenerate with: python analysis/build_results_index.py -->
<!-- Wired into: make reproduce, CI (check_readme_consistency.py) -->

# Results Index

Auto-generated on 2026-09-15T05:57:18Z from `results/*.json`.
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
| Nearest Prototype field micro-F1 | `python baselines/run_baselines.py` | `results/baselines.json` | 51.52 |
| RiceKG verification-suite exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 58.88% |
| Field benchmark positive case count | `python baselines/run_baselines.py` | `results/baselines.json` | 5 |
| Field benchmark negative control count | `python baselines/run_baselines.py` | `results/baselines.json` | 18 |
| Decision Tree field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Random Forest field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Multinomial Naive Bayes field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| k-NN field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Logistic Regression (OvR) field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Ablation: full exact match (verification suite) | `python ablation.py` | `results/ablation.json` | 32.88% |
| Ablation: full multi-label accuracy (verification suite) | `python ablation.py` | `results/ablation.json` | 91.55% |
| Ablation: full positive recall (verification suite) | `python ablation.py` | `results/ablation.json` | 17.78% |
| Ablation: tier1_only exact match (verification suite) | `python ablation.py` | `results/ablation.json` | 27.40% |
| Ablation: tier1_only multi-label accuracy (verification suite) | `python ablation.py` | `results/ablation.json` | 90.18% |
| Ablation: tier1_only positive recall (verification suite) | `python ablation.py` | `results/ablation.json` | 4.44% |
| Ablation: tier2_only exact match (verification suite) | `python ablation.py` | `results/ablation.json` | 32.88% |
| Ablation: tier2_only multi-label accuracy (verification suite) | `python ablation.py` | `results/ablation.json` | 91.55% |
| Ablation: tier2_only positive recall (verification suite) | `python ablation.py` | `results/ablation.json` | 17.78% |
| Ablation: flat_rules exact match (verification suite) | `python ablation.py` | `results/ablation.json` | 32.88% |
| Ablation: flat_rules multi-label accuracy (verification suite) | `python ablation.py` | `results/ablation.json` | 91.55% |
| Ablation: flat_rules positive recall (verification suite) | `python ablation.py` | `results/ablation.json` | 17.78% |
| Ablation: no_reasoner exact match (verification suite) | `python ablation.py` | `results/ablation.json` | 58.90% |
| Ablation: no_reasoner multi-label accuracy (verification suite) | `python ablation.py` | `results/ablation.json` | 91.55% |
| Ablation: no_reasoner positive recall (verification suite) | `python ablation.py` | `results/ablation.json` | 17.78% |
| Learning-curve crossover detected (Pool A (verification suite)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| Learning-curve crossover detected (Pool B (field dev)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| LC zero-shot reference: RiceKG (Full Proposed) positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 35.00% |
| LC zero-shot reference: Rule: Flat Single-Tier positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 35.00% |
| LC zero-shot reference: Rule: Nearest Prototype positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 17.50% |
| RiceKG degradation positive recall at 0.0 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 100.00% |
| RiceKG degradation positive recall at 0.4 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 31.96% |
| RiceKG degradation positive recall at 0.8 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 2.98% |
| RiceKG Top-1 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 40.00% |
| RiceKG Top-3 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 100.00% |
| RiceKG Top-k MRR on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 0.667 |
| RiceKG Top-3 negative-control specificity on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 50.00% |
| Nearest Prototype Top-3 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 100.00% |
| Flat Single-Tier Top-1 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 40.00% |
| RiceKG Top-3 differential hit on holdout (Tier C) | `python analysis/differential_analysis.py` | `results/top_k.json` | 77.78% |

---
_This file is produced by `analysis/build_results_index.py` and validated by `analysis/check_readme_consistency.py`. A stale or missing index fails the CI build._
