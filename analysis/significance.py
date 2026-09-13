"""
analysis/significance.py
------------------------
Paired statistical significance testing and effect size estimation for RiceKG
comparative evaluations against machine learning and rule-based baselines.

Implements:
1. McNemar's test on paired exact-match case agreement (with continuity correction
   and exact binomial test for small sample sizes).
2. Paired effect size estimation: difference in proportions (Delta Acc), Odds Ratio,
   and Cohen's g.
3. Non-parametric bootstrap 95% confidence intervals on Micro-F1 and Delta Micro-F1
   (fixed random seed, explicit resample count).
4. Holm-Bonferroni step-down correction controlling Family-Wise Error Rate (FWER)
   across multiple baseline comparisons.
5. Minimum Detectable Effect (MDE) analytical calculations for n=80 and n=32 to
   prevent misinterpreting underpowered null results as equivalence.
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy import stats


def compute_mcnemar_test(y_true: np.ndarray, y_pred_a: np.ndarray, y_pred_b: np.ndarray) -> Dict[str, Any]:
    """Computes paired McNemar's test between Model A (RiceKG) and Model B (Baseline)
    on exact-match correctness across identical test cases.

    Contingency table:
      a: Both correct
      b: Model A correct, Model B incorrect (favorable to A)
      c: Model A incorrect, Model B correct (favorable to B)
      d: Both incorrect
    """
    correct_a = np.all(y_true == y_pred_a, axis=1)
    correct_b = np.all(y_true == y_pred_b, axis=1)
    n = len(y_true)

    a = int(np.sum(correct_a & correct_b))
    b = int(np.sum(correct_a & (~correct_b)))
    c = int(np.sum((~correct_a) & correct_b))
    d = int(np.sum((~correct_a) & (~correct_b)))

    total_discordant = b + c

    if total_discordant == 0:
        statistic = 0.0
        p_value = 1.0
        method = "Exact (0 discordant pairs)"
    elif total_discordant < 25:
        # Exact two-sided binomial test on discordant pairs
        # Under H0: b ~ Binomial(b+c, 0.5)
        res = stats.binomtest(b, total_discordant, p=0.5, alternative="two-sided")
        p_value = float(res.pvalue)
        statistic = float((abs(b - c) - 1.0) ** 2 / total_discordant) if total_discordant > 0 else 0.0
        method = "Exact Binomial Test (discordant n < 25)"
    else:
        # Edwards continuity-corrected McNemar Chi-Square
        statistic = float((abs(b - c) - 1.0) ** 2 / total_discordant)
        p_value = float(stats.chi2.sf(statistic, df=1))
        method = "McNemar Chi-Square with Edwards Continuity Correction"

    # Effect sizes: Risk Difference (Delta Acc) with paired Wald 95% CI
    acc_a = (a + b) / n if n > 0 else 0.0
    acc_b = (a + c) / n if n > 0 else 0.0
    delta_acc = acc_a - acc_b

    # Paired Wald variance for difference of proportions:
    # Var(d) = ((b + c) - (b - c)^2 / n) / n^2
    var_d = ((b + c) - ((b - c) ** 2) / n) / (n ** 2) if n > 0 else 0.0
    se_d = float(np.sqrt(max(0.0, var_d)))
    z_crit = 1.959963984540054
    delta_acc_ci = (
        float(max(-100.0, (delta_acc - z_crit * se_d) * 100.0)),
        float(min(100.0, (delta_acc + z_crit * se_d) * 100.0))
    )

    # Odds Ratio with Haldane-Anscombe 0.5 continuity correction if c == 0
    if c == 0 and b == 0:
        odds_ratio = 1.0
    elif c == 0:
        odds_ratio = float((b + 0.5) / 0.5)
    else:
        odds_ratio = float(b / c)

    # Cohen's g: effect size for paired proportions, g = (b / (b+c)) - 0.5
    # Bounded strictly on [-0.5, +0.5]. Bounded ceiling at +0.5 when c = 0.
    cohens_g = float((b / total_discordant) - 0.5) if total_discordant > 0 else 0.0

    return {
        "n_cases": n,
        "contingency_table": {"both_correct": a, "a_only": b, "b_only": c, "neither_correct": d},
        "total_discordant": total_discordant,
        "statistic": statistic,
        "p_value": p_value,
        "test_method": method,
        "acc_a": acc_a * 100.0,
        "acc_b": acc_b * 100.0,
        "delta_acc": delta_acc * 100.0,
        "delta_acc_ci": delta_acc_ci,
        "odds_ratio": odds_ratio,
        "cohens_g": cohens_g,
    }


def compute_micro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes micro-averaged F1 score in percentage [0.0, 100.0]."""
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    return float(f1 * 100.0)


def bootstrap_micro_f1_ci(
    y_true: np.ndarray,
    y_pred_a: np.ndarray,
    y_pred_b: Optional[np.ndarray] = None,
    n_resamples: int = 1000,
    random_state: int = 42,
    ci_level: float = 0.95
) -> Dict[str, Any]:
    """Calculates non-parametric bootstrap percentile confidence intervals
    for Micro-F1 and paired difference (Delta Micro-F1 = F1_a - F1_b).
    """
    rng = np.random.default_rng(random_state)
    n = len(y_true)

    alpha = 1.0 - ci_level
    lower_pct = (alpha / 2.0) * 100.0
    upper_pct = (1.0 - alpha / 2.0) * 100.0

    f1_a_boot = np.empty(n_resamples, dtype=float)
    f1_b_boot = np.empty(n_resamples, dtype=float) if y_pred_b is not None else None
    delta_f1_boot = np.empty(n_resamples, dtype=float) if y_pred_b is not None else None

    for i in range(n_resamples):
        boot_idx = rng.choice(n, size=n, replace=True)
        yt_b = y_true[boot_idx]
        ya_b = y_pred_a[boot_idx]
        f1_a = compute_micro_f1(yt_b, ya_b)
        f1_a_boot[i] = f1_a

        if y_pred_b is not None:
            yb_b = y_pred_b[boot_idx]
            f1_b = compute_micro_f1(yt_b, yb_b)
            f1_b_boot[i] = f1_b
            delta_f1_boot[i] = f1_a - f1_b

    f1_a_ci = (float(np.percentile(f1_a_boot, lower_pct)), float(np.percentile(f1_a_boot, upper_pct)))
    f1_a_mean = float(np.mean(f1_a_boot))

    result = {
        "n_resamples": n_resamples,
        "ci_level": ci_level,
        "f1_a_mean": f1_a_mean,
        "f1_a_ci": f1_a_ci,
    }

    if y_pred_b is not None:
        f1_b_ci = (float(np.percentile(f1_b_boot, lower_pct)), float(np.percentile(f1_b_boot, upper_pct)))
        delta_ci = (float(np.percentile(delta_f1_boot, lower_pct)), float(np.percentile(delta_f1_boot, upper_pct)))
        result.update({
            "f1_b_mean": float(np.mean(f1_b_boot)),
            "f1_b_ci": f1_b_ci,
            "delta_f1_mean": float(np.mean(delta_f1_boot)),
            "delta_f1_ci": delta_ci,
        })

    return result


def apply_holm_bonferroni(p_values: List[float], alpha: float = 0.05) -> List[Dict[str, Any]]:
    """Applies Holm-Bonferroni step-down correction across a list of p-values.
    Returns ordered results with adjusted p-values and significance flags.
    """
    m = len(p_values)
    # Sort indices by unadjusted p-value ascending
    sorted_indices = sorted(range(m), key=lambda i: p_values[i])
    
    adjusted = [0.0] * m
    running_max = 0.0

    for rank, orig_idx in enumerate(sorted_indices):
        k = rank + 1  # 1-indexed rank
        multiplier = m - k + 1
        raw_p = p_values[orig_idx]
        adj_p = min(1.0, raw_p * multiplier)
        # Enforce monotonicity: adj_p cannot decrease as rank increases
        running_max = max(running_max, adj_p)
        adjusted[orig_idx] = min(1.0, running_max)

    results = []
    for i in range(m):
        results.append({
            "original_index": i,
            "raw_p_value": p_values[i],
            "holm_p_value": adjusted[i],
            "significant": adjusted[i] < alpha
        })
    return results


def calculate_minimum_detectable_effect(n: int, alpha: float = 0.05, power: float = 0.80, baseline_rate: float = 0.85) -> Dict[str, Any]:
    """Calculates the Minimum Detectable Effect (MDE) in proportion for a given sample size n,
    significance level alpha (two-tailed), and power (1 - beta).
    """
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)  # ~1.96 for 0.05
    z_beta = stats.norm.ppf(power)                # ~0.84 for 0.80
    z_sum = z_alpha + z_beta

    # For paired comparison with discordant rate ~0.30
    psi = 0.30
    mde_mcnemar = z_sum * math.sqrt(psi / n) if n > 0 else float("nan")

    # Standard paired proportion MDE approximation
    p0 = baseline_rate
    mde_prop = z_sum * math.sqrt((2.0 * p0 * (1.0 - p0)) / n) if n > 0 else float("nan")

    return {
        "n": n,
        "alpha": alpha,
        "power": power,
        "baseline_rate": baseline_rate,
        "z_alpha_half": z_alpha,
        "z_beta": z_beta,
        "mde_percentage_mcnemar": float(mde_mcnemar * 100.0),
        "mde_percentage_proportion": float(mde_prop * 100.0),
        "disclosure": (
            f"With n={n} (alpha={alpha:.2f}, power={power:.2f}), the study can only reliably detect "
            f"accuracy differences of at least +/-{mde_prop * 100.0:.1f} percentage points. "
            f"Null hypothesis tests (p > {alpha:.2f}) must NOT be interpreted as proof of equivalence."
        )
    }
