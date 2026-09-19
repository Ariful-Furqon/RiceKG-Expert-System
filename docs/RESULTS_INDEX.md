<!-- GENERATED FILE — DO NOT EDIT BY HAND -->
<!-- content-sha256: 34a57d640a3eb55cddee66f9fed801036a06d2b297224a0968d228976ca2a959 -->
<!-- Regenerate with: python analysis/build_results_index.py -->
<!-- Wired into: make reproduce, CI (check_readme_consistency.py) -->

# Results Index

Auto-generated on 2026-09-19T02:07:25Z from `results/*.json`.
Each row maps a manuscript claim to the command that produces it and the
source artifact that stores the value. Edit
`analysis/build_results_index.py` to change what is indexed.

| Manuscript claim | Command | Source artifact | Value |
|---|---|---|---|
| RiceKG field positive-case recall | `python baselines/run_baselines.py` | `results/baselines.json` | 85.00% |
| RiceKG field exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 95.45% |
| RiceKG field micro-F1 [95% CI] | `python baselines/run_baselines.py` | `results/baselines.json` | 91.14 [77.4, 97.6] |
| Nearest Prototype field positive-case recall | `python baselines/run_baselines.py` | `results/baselines.json` | 40.83% |
| Nearest Prototype field exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 86.36% |
| Nearest Prototype field micro-F1 | `python baselines/run_baselines.py` | `results/baselines.json` | 74.83 |
| RiceKG verification-suite exact match | `python baselines/run_baselines.py` | `results/baselines.json` | 68.51% |
| Field benchmark positive case count | `python baselines/run_baselines.py` | `results/baselines.json` | 5 |
| Field benchmark negative control count | `python baselines/run_baselines.py` | `results/baselines.json` | 17 |
| Decision Tree field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Random Forest field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Multinomial Naive Bayes field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| k-NN field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Logistic Regression (OvR) field positive-recall (5×2-fold CV) | `python baselines/run_baselines.py` | `results/baselines.json` | 0.00% |
| Ablation: Pellet vs set matching, identical graded output | `python analysis/ablation.py` | `results/ablation.json` | 129/129 |
| Ablation (dev+eval): RiceKG v2.4.0 (full) committed recall | `python analysis/ablation.py` | `results/ablation.json` | 9/12 |
| Ablation (dev+eval): Without diagnostic-sign rules (R21–R26) committed recall | `python analysis/ablation.py` | `results/ablation.json` | 7/12 |
| Ablation (dev+eval): Tier-1 rules only committed recall | `python analysis/ablation.py` | `results/ablation.json` | 0/12 |
| Ablation (dev+eval): Without out-of-scope gates committed recall | `python analysis/ablation.py` | `results/ablation.json` | 9/12 |
| Ablation (holdout (development-exposed)): RiceKG v2.4.0 (full) committed recall | `python analysis/ablation.py` | `results/ablation.json` | 12/18 |
| Ablation (holdout (development-exposed)): Without diagnostic-sign rules (R21–R26) committed recall | `python analysis/ablation.py` | `results/ablation.json` | 4/18 |
| Ablation (holdout (development-exposed)): Tier-1 rules only committed recall | `python analysis/ablation.py` | `results/ablation.json` | 0/18 |
| Ablation (holdout (development-exposed)): Without out-of-scope gates committed recall | `python analysis/ablation.py` | `results/ablation.json` | 12/18 |
| Ablation (occlusion 0.3): RiceKG v2.4.0 (full) positive recall | `python analysis/ablation.py` | `results/ablation.json` | 67.91% |
| Ablation (occlusion 0.3): Without diagnostic-sign rules (R21–R26) positive recall | `python analysis/ablation.py` | `results/ablation.json` | 44.33% |
| Ablation (occlusion 0.3): Tier-1 rules only positive recall | `python analysis/ablation.py` | `results/ablation.json` | 15.63% |
| Learning-curve crossover detected (Pool A (verification suite)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| Learning-curve crossover detected (Pool B (field dev)) | `python analysis/learning_curve.py` | `results/learning_curve.json` | None (all test-set CIs include zero) |
| LC zero-shot reference: RiceKG (Full Proposed) positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 85.00% |
| LC zero-shot reference: Rule: Flat Single-Tier positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 85.00% |
| LC zero-shot reference: Rule: Nearest Prototype positive recall | `python analysis/learning_curve.py` | `results/learning_curve.json` | 40.83% |
| RiceKG degradation positive recall at 0.0 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 100.00% |
| RiceKG degradation positive recall at 0.4 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 57.53% |
| RiceKG degradation positive recall at 0.8 occlusion | `python analysis/degradation_curve.py` | `results/degradation_curve.json` | 25.14% |
| RiceKG Top-1 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 80.00% |
| RiceKG Top-3 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 100.00% |
| RiceKG Top-k MRR on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 0.900 |
| RiceKG Top-3 negative-control specificity on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 82.35% |
| Nearest Prototype Top-3 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 100.00% |
| Flat Single-Tier Top-1 differential hit on field eval | `python analysis/differential_analysis.py` | `results/top_k.json` | 80.00% |
| RiceKG Top-3 differential hit on holdout (tiers A-C) | `python analysis/differential_analysis.py` | `results/top_k.json` | 77.78% |

---
_This file is produced by `analysis/build_results_index.py` and validated by `analysis/check_readme_consistency.py`. A stale or missing index fails the CI build._
