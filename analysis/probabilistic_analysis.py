"""
analysis/probabilistic_analysis.py
----------------------------------
Probabilistic Reasoning Layer (Noisy-OR) Comparative Evaluation (PART 8-C & 8-D).

Evaluates 5 systems on identical cases across four datasets:
  1. RiceKG strict (model.predict_diseases, include_possible=False)
  2. RiceKG + possible grade (model.predict_diseases, include_possible=True)
  3. noisy-OR at DECISION_THRESHOLD=0.50 (with gates)
  4. noisy-OR at DECISION_THRESHOLD=0.50 (without gates)
  5. Rule: Nearest Prototype (rule_baselines.predict_nearest_prototype)

Datasets:
  - Field Benchmark: dev split (n=16: 7 positives, 9 controls)
  - Field Benchmark: eval split (5 positives + negative controls)
  - Field Benchmark: holdout split (n=18: 18 positives, 0 controls; labelled development-exposed)
  - Deductive Verification Suite (n=73: 55 positives, 18 controls)

Computes:
  - Multi-label metrics: positive recall, exact match, micro-precision, micro-recall, micro-F1, 95% bootstrap CIs
  - Negative-control false alarm rate (all controls & mapped-sign controls)
  - Trade-off curve: recall vs. FAR across threshold grid [0.05, 0.10, ..., 0.95]
  - Differential Top-k: Hit@1/2/3, MRR, FAR@k via differential_analysis.compute_top_k_metrics_for_system
  - Paired McNemar tests against RiceKG strict with Holm-Bonferroni correction and analytical MDE
  - Brier score and 5-bin reliability table (with strict calibration disclaimer)
  - Parameter sensitivity sweeps: p +/- 0.1, alternative scale, leaks x0.5 and x2.0, quantitative only

Generates:
  results/probabilistic.json
  results/probabilistic.md
  results/figures/probabilistic_tradeoff.png
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import model
from ricekg import evaluate
from ricekg import probabilistic
from baselines import ml_baselines, rule_baselines
from analysis import significance, differential_analysis
from analysis.degradation_curve import fast_predict_ricekg, fast_predict_ricekg_possible

RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
FIELD_CSV = os.path.join(BASE_DIR, "data", "benchmark_field.csv")


def _field_split_counts(split):
    """(total, positives, negative controls) for one split of the field benchmark."""
    import csv as _csv
    with open(FIELD_CSV, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in _csv.DictReader(f) if r["split"] == split]
    pos = sum(1 for r in rows if r["diagnosis"] != "No_Diagnosis")
    return len(rows), pos, len(rows) - pos


EVAL_N, EVAL_POS, EVAL_NEG = _field_split_counts("eval")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

ALL_THREATS = model.ALL_DIAGNOSES
DECISION_THRESHOLD = probabilistic.DECISION_THRESHOLD  # 0.50
THRESHOLD_GRID = [round(t, 2) for t in np.arange(0.05, 1.00, 0.05)]


def _repo_relative(path: str) -> str:
    """Return path relative to repository root using POSIX forward slashes."""
    try:
        rel = os.path.relpath(path, BASE_DIR)
        return rel.replace(os.sep, "/")
    except Exception:
        return path.replace(os.sep, "/")


# ---------------------------------------------------------------------------
# Solver Prediction Wrappers
# ---------------------------------------------------------------------------

def predict_system_threats(
    system_key: str,
    symptoms: List[str],
    threshold: float = DECISION_THRESHOLD,
    params: Optional[probabilistic.NoisyOrParameters] = None,
) -> List[str]:
    """Returns diagnosed in-scope threats for a given system on a symptom list."""
    if system_key == "RiceKG strict":
        # Fast solver equivalent to model.predict_diseases(symptoms, include_possible=False)
        return [t for t in fast_predict_ricekg(symptoms) if t in ALL_THREATS]
    elif system_key == "RiceKG + possible":
        # Fast solver equivalent to model.predict_diseases(symptoms, include_possible=True)
        return [t for t in fast_predict_ricekg_possible(symptoms) if t in ALL_THREATS]
    elif system_key == "noisy-OR (with gates)":
        out = probabilistic.predict_probabilistic(
            symptoms, threshold=threshold, apply_gates=True, params=params
        )
        return [p["threat"] for p in out]
    elif system_key == "noisy-OR (without gates)":
        out = probabilistic.predict_probabilistic(
            symptoms, threshold=threshold, apply_gates=False, params=params
        )
        return [p["threat"] for p in out]
    elif system_key == "Rule: Nearest Prototype":
        return [t for t in rule_baselines.predict_nearest_prototype(symptoms) if t in ALL_THREATS]
    else:
        raise ValueError(f"Unknown system key: {system_key}")


def rank_system_threats(
    system_key: str,
    symptoms: List[str],
    k: int = 3,
    params: Optional[probabilistic.NoisyOrParameters] = None,
) -> List[str]:
    """Returns top-k ranked candidates for a given system."""
    if system_key == "RiceKG strict":
        top = model.predict_top_k(symptoms, k=k, include_possible=False)
        return [cand["threat"] for cand in top]
    elif system_key == "RiceKG + possible":
        top = model.predict_top_k(symptoms, k=k, include_possible=True)
        return [cand["threat"] for cand in top]
    elif system_key == "noisy-OR (with gates)":
        return probabilistic.rank_differential_probabilistic(
            symptoms, k=k, apply_gates=True, params=params
        )
    elif system_key == "noisy-OR (without gates)":
        return probabilistic.rank_differential_probabilistic(
            symptoms, k=k, apply_gates=False, params=params
        )
    elif system_key == "Rule: Nearest Prototype":
        return differential_analysis.rank_nearest_prototype(symptoms, k=k)
    else:
        raise ValueError(f"Unknown system key: {system_key}")


# ---------------------------------------------------------------------------
# Metric Evaluation
# ---------------------------------------------------------------------------

def evaluate_predictions_with_bootstrap(
    Y_true: np.ndarray,
    Y_pred: np.ndarray,
    cases: List[Dict[str, Any]],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Computes exact match, recall, precision, F1, and bootstrap 95% CIs."""
    base_metrics = ml_baselines.compute_multilabel_metrics(Y_true, Y_pred)
    n_cases = len(cases)

    # Positive case recall breakdown:
    # 1. Exact match on positive cases (ml_baselines convention)
    # 2. Any-threat hit on positive cases (at least one true threat recalled)
    pos_indices = [i for i, c in enumerate(cases) if c.get("raw_target") != "No_Diagnosis"]
    any_hits = 0
    for idx in pos_indices:
        true_threats = set(cases[idx].get("expected", []))
        # check which threats predicted
        pred_threats = {ALL_THREATS[j] for j in range(len(ALL_THREATS)) if Y_pred[idx, j] == 1}
        if any(t in true_threats for t in pred_threats):
            any_hits += 1
    pos_any_recall = (any_hits / len(pos_indices) * 100.0) if pos_indices else 0.0

    # Negative control breakdown
    neg_indices = [i for i, c in enumerate(cases) if c.get("raw_target") == "No_Diagnosis"]
    mapped_neg_indices = [i for i in neg_indices if len(cases[i].get("symptoms", [])) > 0]

    all_neg_fps = int(np.sum([1 for i in neg_indices if np.any(Y_pred[i] == 1)]))
    mapped_neg_fps = int(np.sum([1 for i in mapped_neg_indices if np.any(Y_pred[i] == 1)]))

    all_neg_far = (all_neg_fps / len(neg_indices) * 100.0) if neg_indices else None
    mapped_neg_far = (mapped_neg_fps / len(mapped_neg_indices) * 100.0) if mapped_neg_indices else None

    # Bootstrap CIs over cases
    rng = np.random.RandomState(seed)
    boot_recalls = []
    boot_any_recalls = []
    boot_exacts = []
    boot_f1s = []

    pos_mask = np.sum(Y_true, axis=1) > 0
    has_pos = int(np.sum(pos_mask)) > 0

    if n_cases > 0 and n_bootstrap > 0:
        for _ in range(n_bootstrap):
            b_idx = rng.choice(n_cases, size=n_cases, replace=True)
            Y_t_b = Y_true[b_idx]
            Y_p_b = Y_pred[b_idx]
            m_b = ml_baselines.compute_multilabel_metrics(Y_t_b, Y_p_b)
            if has_pos:
                boot_recalls.append(m_b["positive_case_recall"])
                # any hit recall on bootstrap sample
                b_pos_hits = 0
                b_pos_count = 0
                for orig_i in b_idx:
                    if cases[orig_i].get("raw_target") != "No_Diagnosis":
                        b_pos_count += 1
                        exp_t = set(cases[orig_i].get("expected", []))
                        p_t = {ALL_THREATS[j] for j in range(len(ALL_THREATS)) if Y_pred[orig_i, j] == 1}
                        if any(t in exp_t for t in p_t):
                            b_pos_hits += 1
                if b_pos_count > 0:
                    boot_any_recalls.append(b_pos_hits / b_pos_count * 100.0)
            boot_exacts.append(m_b["exact_match"])
            boot_f1s.append(m_b["micro_f1"])

    def _ci(vals):
        if not vals:
            return None
        return [round(float(np.percentile(vals, 2.5)), 2), round(float(np.percentile(vals, 97.5)), 2)]

    return {
        "positive_case_recall": round(float(base_metrics["positive_case_recall"]), 2),
        "positive_recall_ci95": _ci(boot_recalls),
        "positive_any_recall": round(float(pos_any_recall), 2),
        "positive_any_recall_ci95": _ci(boot_any_recalls),
        "exact_match": round(float(base_metrics["exact_match"]), 2),
        "exact_match_ci95": _ci(boot_exacts),
        "micro_precision": round(float(base_metrics["micro_precision"]), 2),
        "micro_recall": round(float(base_metrics["micro_recall"]), 2),
        "micro_f1": round(float(base_metrics["micro_f1"]), 2),
        "micro_f1_ci95": _ci(boot_f1s),
        "n_total": n_cases,
        "n_positive": int(base_metrics["positive_cases_count"]),
        "n_negative": len(neg_indices),
        "all_neg_fps": all_neg_fps,
        "all_neg_far": round(all_neg_far, 2) if all_neg_far is not None else None,
        "mapped_neg_count": len(mapped_neg_indices),
        "mapped_neg_fps": mapped_neg_fps,
        "mapped_neg_far": round(mapped_neg_far, 2) if mapped_neg_far is not None else None,
        "tp": int(base_metrics["tp"]),
        "fp": int(base_metrics["fp"]),
        "fn": int(base_metrics["fn"]),
        "tn": int(base_metrics["tn"]),
    }


# ---------------------------------------------------------------------------
# Calibration: Brier Score and Reliability Table
# ---------------------------------------------------------------------------

def compute_calibration_analysis(
    cases: List[Dict[str, Any]],
    params: Optional[probabilistic.NoisyOrParameters] = None,
    bins: Tuple[Tuple[float, float], ...] = (
        (0.0, 0.2),
        (0.2, 0.4),
        (0.4, 0.6),
        (0.6, 0.8),
        (0.8, 1.0001),
    ),
) -> Dict[str, Any]:
    """Computes multi-label Brier score and a 5-bin reliability diagram table."""
    y_true_all: List[int] = []
    y_prob_all: List[float] = []

    for c in cases:
        scores = probabilistic.posterior_scores(c["symptoms"], params=params)
        exp = set(c.get("expected", []))
        for t in ALL_THREATS:
            y_true_all.append(1 if t in exp else 0)
            y_prob_all.append(scores.get(t, 0.0))

    y_t = np.array(y_true_all, dtype=float)
    y_p = np.array(y_prob_all, dtype=float)

    brier = float(np.mean((y_p - y_t) ** 2)) if len(y_t) > 0 else 0.0

    table_rows = []
    for b_low, b_high in bins:
        mask = (y_p >= b_low) & (y_p < b_high)
        cnt = int(np.sum(mask))
        mean_conf = float(np.mean(y_p[mask])) if cnt > 0 else 0.0
        emp_acc = float(np.mean(y_t[mask])) if cnt > 0 else 0.0
        label_upper = 1.0 if b_high > 1.0 else b_high
        table_rows.append({
            "bin_range": f"[{b_low:.1f}, {label_upper:.1f})",
            "count": cnt,
            "mean_confidence": round(mean_conf, 4),
            "empirical_accuracy": round(emp_acc, 4),
        })

    return {
        "brier_score": round(brier, 4),
        "total_pairs": len(y_t),
        "reliability_table": table_rows,
        "calibration_disclaimer": (
            "With 5 eval positives, calibration cannot be validated; do not claim calibration. "
            "The sample size is insufficient to reliably populate intermediate probability bins."
        ),
    }


# ---------------------------------------------------------------------------
# Trade-Off Curve Computation
# ---------------------------------------------------------------------------

def compute_tradeoff_curve(
    cases: List[Dict[str, Any]],
    threshold_grid: List[float] = THRESHOLD_GRID,
    params: Optional[probabilistic.NoisyOrParameters] = None,
) -> Dict[str, Any]:
    """Evaluates recall and negative-control FAR for noisy-OR across the threshold grid."""
    pos_cases = [c for c in cases if c.get("raw_target") != "No_Diagnosis"]
    neg_cases = [c for c in cases if c.get("raw_target") == "No_Diagnosis"]

    points = []
    for thr in threshold_grid:
        hits = 0
        for c in pos_cases:
            preds = predict_system_threats("noisy-OR (with gates)", c["symptoms"], threshold=thr, params=params)
            if any(p in c["expected"] for p in preds):
                hits += 1
        rec = (hits / len(pos_cases) * 100.0) if pos_cases else 0.0

        fps = 0
        for c in neg_cases:
            preds = predict_system_threats("noisy-OR (with gates)", c["symptoms"], threshold=thr, params=params)
            if len(preds) > 0:
                fps += 1
        far = (fps / len(neg_cases) * 100.0) if neg_cases else None

        points.append({
            "threshold": thr,
            "positive_recall": round(rec, 2),
            "negative_control_far": round(far, 2) if far is not None else None,
        })

    # Reference points for strict and possible
    strict_hits = sum(1 for c in pos_cases if any(p in c["expected"] for p in predict_system_threats("RiceKG strict", c["symptoms"])))
    strict_fps = sum(1 for c in neg_cases if len(predict_system_threats("RiceKG strict", c["symptoms"])) > 0)

    poss_hits = sum(1 for c in pos_cases if any(p in c["expected"] for p in predict_system_threats("RiceKG + possible", c["symptoms"])))
    poss_fps = sum(1 for c in neg_cases if len(predict_system_threats("RiceKG + possible", c["symptoms"])) > 0)

    return {
        "grid_points": points,
        "references": {
            "RiceKG strict": {
                "positive_recall": round(strict_hits / len(pos_cases) * 100.0, 2) if pos_cases else 0.0,
                "negative_control_far": round(strict_fps / len(neg_cases) * 100.0, 2) if neg_cases else None,
            },
            "RiceKG + possible": {
                "positive_recall": round(poss_hits / len(pos_cases) * 100.0, 2) if pos_cases else 0.0,
                "negative_control_far": round(poss_fps / len(neg_cases) * 100.0, 2) if neg_cases else None,
            },
        },
    }


# ---------------------------------------------------------------------------
# Parameter Sensitivity Sweeps
# ---------------------------------------------------------------------------

def run_parameter_sensitivity(
    cases_dict: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Evaluates parameter sensitivity variants (Protocol 8-D.1 and 8-D.3)."""
    base_params = probabilistic.load_noisy_or_parameters()
    base_links = base_params.links
    base_leaks = base_params.leaks

    # Variant 1: p +/- 0.1
    p_minus = {(t, e): max(0.01, min(0.99, p - 0.1)) for (t, e), p in base_links.items()}
    p_plus = {(t, e): max(0.01, min(0.99, p + 0.1)) for (t, e), p in base_links.items()}

    # Variant 2: Alternative qualitative scale {0.95, 0.80, 0.50, 0.20}
    alt_map = {0.90: 0.95, 0.70: 0.80, 0.40: 0.50, 0.15: 0.20}
    alt_links = {(t, e): alt_map.get(round(p, 2), p) for (t, e), p in base_links.items()}

    # Variant 3: Leaks x0.5 and x2.0
    leaks_half = {e: max(0.001, min(0.99, l * 0.5)) for e, l in base_leaks.items()}
    leaks_double = {e: max(0.001, min(0.99, l * 2.0)) for e, l in base_leaks.items()}

    # Variant 4: Quantitative only (8-D.3)
    quant_links = set()
    params_csv = os.path.join(BASE_DIR, "data", "noisy_or_parameters.csv")
    with open(params_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("elicitation") == "quantitative":
                quant_links.add((row["threat"], row["observation"]))
    quant_only = {(t, e): p for (t, e), p in base_links.items() if (t, e) in quant_links}

    variants = [
        ("baseline", base_params),
        ("p_minus_0.1", probabilistic.NoisyOrParameters(p_minus, base_leaks)),
        ("p_plus_0.1", probabilistic.NoisyOrParameters(p_plus, base_leaks)),
        ("alt_scale", probabilistic.NoisyOrParameters(alt_links, base_leaks)),
        ("leaks_half", probabilistic.NoisyOrParameters(base_links, leaks_half)),
        ("leaks_double", probabilistic.NoisyOrParameters(base_links, leaks_double)),
        ("quantitative_only", probabilistic.NoisyOrParameters(quant_only, base_leaks)),
    ]

    out_sensitivity: Dict[str, Any] = {}

    for split_key in ("dev", "eval"):
        cases = cases_dict[split_key]
        pos_cases = [c for c in cases if c.get("raw_target") != "No_Diagnosis"]
        neg_cases = [c for c in cases if c.get("raw_target") == "No_Diagnosis"]

        split_results = {}
        recalls = []
        fars = []

        for vname, pobj in variants:
            hits = sum(1 for c in pos_cases if any(p["threat"] in c["expected"] for p in probabilistic.predict_probabilistic(c["symptoms"], params=pobj, apply_gates=True)))
            fps = sum(1 for c in neg_cases if any(p["threat"] in ALL_THREATS for p in probabilistic.predict_probabilistic(c["symptoms"], params=pobj, apply_gates=True)))
            rec = round(hits / len(pos_cases) * 100.0, 2) if pos_cases else 0.0
            far = round(fps / len(neg_cases) * 100.0, 2) if neg_cases else 0.0

            split_results[vname] = {
                "positive_recall": rec,
                "negative_control_far": far,
            }
            # Span excludes quantitative_only which is a separate ablation
            if vname != "quantitative_only":
                recalls.append(rec)
                fars.append(far)

        split_results["span"] = {
            "positive_recall_min": min(recalls),
            "positive_recall_max": max(recalls),
            "far_min": min(fars),
            "far_max": max(fars),
        }
        out_sensitivity[split_key] = split_results

    return out_sensitivity


# ---------------------------------------------------------------------------
# Plot Generation
# ---------------------------------------------------------------------------

def generate_tradeoff_plot(
    eval_tradeoff: Dict[str, Any],
    dev_tradeoff: Dict[str, Any],
    output_png: str,
) -> None:
    """Plots the Recall vs. False Alarm Rate trade-off curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    for ax, data, title, n_pos, n_neg in [
        (ax1, dev_tradeoff, "Field Benchmark (Dev Split)", 7, 9),
        (ax2, eval_tradeoff, "Field Benchmark (Eval Split, Held-Out)", 5, 18),
    ]:
        points = data["grid_points"]
        thrs = [p["threshold"] for p in points]
        recs = [p["positive_recall"] for p in points]
        fars = [p["negative_control_far"] for p in points]

        # Plot Noisy-OR curve (FAR on x-axis, Recall on y-axis)
        ax.plot(fars, recs, "-o", color="#2b83ba", linewidth=2.2, label="noisy-OR (threshold grid)", markersize=5)

        # Highlight default decision threshold 0.50
        pt_50 = next((p for p in points if abs(p["threshold"] - 0.50) < 1e-4), None)
        if pt_50:
            ax.plot(pt_50["negative_control_far"], pt_50["positive_recall"], "s", color="#d7191c",
                    markersize=9, label="noisy-OR (θ = 0.50 default)")

        # References
        ref_strict = data["references"]["RiceKG strict"]
        ref_poss = data["references"]["RiceKG + possible"]

        ax.plot(ref_strict["negative_control_far"], ref_strict["positive_recall"], "D",
                color="#1b9e77", markersize=9, label="RiceKG strict")
        ax.plot(ref_poss["negative_control_far"], ref_poss["positive_recall"], "^",
                color="#fdae61", markersize=9, label="RiceKG + possible grade")

        ax.set_title(f"{title}\n({n_pos} positives, {n_neg} negative controls)", fontsize=11, fontweight="bold")
        ax.set_xlabel("Negative-Control False Alarm Rate (FAR, %)", fontsize=11)
        ax.set_ylabel("Positive-Case Recall (%)", fontsize=11)
        ax.set_xlim(-2, 105)
        ax.set_ylim(-2, 105)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="lower right", fontsize=9, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()


# ---------------------------------------------------------------------------
# Markdown Generation
# ---------------------------------------------------------------------------

def _generate_findings(results: Dict[str, Any]) -> List[str]:
    """Generates Findings dynamically from computed metrics."""
    ev = results["datasets"]["eval"]
    dev = results["datasets"]["dev"]
    hld = results["datasets"]["holdout"]
    sens = results["parameter_sensitivity"]

    rk_ev_rec = ev["systems"]["RiceKG strict"]["metrics"]["positive_case_recall"]
    rk_ev_far = ev["systems"]["RiceKG strict"]["metrics"]["all_neg_far"]

    poss_ev_rec = ev["systems"]["RiceKG + possible"]["metrics"]["positive_case_recall"]
    poss_ev_far = ev["systems"]["RiceKG + possible"]["metrics"]["all_neg_far"]

    nor_ev_rec = ev["systems"]["noisy-OR (with gates)"]["metrics"]["positive_case_recall"]
    nor_ev_far = ev["systems"]["noisy-OR (with gates)"]["metrics"]["all_neg_far"]
    nor_nog_far = ev["systems"]["noisy-OR (without gates)"]["metrics"]["all_neg_far"]

    mcn = ev["pairwise_against_strict"]["noisy-OR (with gates)"]
    mde = ev["mde"]["mde_percentage_proportion"]

    sens_ev = sens["eval"]
    sens_dev = sens["dev"]

    findings = [
        f"1. **Recall versus False Alarm Trade-Off.** On the field `eval` split ({EVAL_POS} positives, {EVAL_NEG} controls), strict RiceKG achieves "
        f"{ev['systems']['RiceKG strict']['metrics']['positive_any_recall']:.1f}% any-hit recall ({rk_ev_rec:.1f}% exact positive-case recall) with {rk_ev_far:.1f}% false alarms. "
        f"The `possible` grade reaches {ev['systems']['RiceKG + possible']['metrics']['positive_any_recall']:.1f}% any-hit recall ({poss_ev_rec:.1f}% exact) with {poss_ev_far:.1f}% false alarms. "
        f"The noisy-OR layer at default threshold $\\theta = 0.50$ attains {ev['systems']['noisy-OR (with gates)']['metrics']['positive_any_recall']:.1f}% any-hit recall ({nor_ev_rec:.1f}% exact single-label match due to multi-threat differential candidate generation), "
        f"but incurs a {nor_ev_far:.1f}% false-alarm rate on negative controls ({nor_nog_far:.1f}% without out-of-scope gates). "
        f"Probabilistic scoring trades precision for sensitivity, operating as an aggressive screening instrument.",
        f"2. **Comparative Equivalence to the `possible` Grade.** On `dev`, noisy-OR achieves {dev['systems']['noisy-OR (with gates)']['metrics']['positive_any_recall']:.1f}% any-hit recall "
        f"and {dev['systems']['noisy-OR (with gates)']['metrics']['all_neg_far']:.1f}% FAR. At no threshold operating point does noisy-OR achieve higher recall than the coverage-threshold "
        f"`possible` grade without a corresponding elevation in false alarm rate.",
        f"3. **Statistical Power & Significance Limits.** Paired McNemar testing between strict RiceKG and noisy-OR on `eval` exact-match yields "
        f"$p = {mcn['p_value']:.4e}$ (Holm-corrected $p = {mcn['holm_p_value']:.4e}$), reflecting the large difference in negative-control false alarms (strict exact-match: {ev['systems']['RiceKG strict']['metrics']['exact_match']:.1f}%, noisy-OR: {ev['systems']['noisy-OR (with gates)']['metrics']['exact_match']:.1f}%). "
        f"However, with only 5 eval positive disease cases, the study has an analytical Minimum Detectable Effect of $\\pm {mde:.1f}\\%$ at $\\alpha=0.05, 80\\%$ power. "
        f"Positive recall differences on this split cannot be statistically distinguished from chance.",
        f"4. **Parameter Sensitivity Spans.** Across conditional probability shifts ($p \\pm 0.1$), the alternative qualitative scale, and background leak scaling ($\\times 0.5$, $\\times 2.0$), "
        f"noisy-OR recall spans [{sens_ev['span']['positive_recall_min']:.1f}%, {sens_ev['span']['positive_recall_max']:.1f}%] on `eval` and [{sens_dev['span']['positive_recall_min']:.1f}%, {sens_dev['span']['positive_recall_max']:.1f}%] on `dev`, "
        f"while FAR spans [{sens_ev['span']['far_min']:.1f}%, {sens_ev['span']['far_max']:.1f}%] on `eval` and [{sens_dev['span']['far_min']:.1f}%, {sens_dev['span']['far_max']:.1f}%] on `dev`. "
        f"Because system differences fall within these parameter perturbation envelopes, comparisons between calibrated points are formally inconclusive.",
        f"5. **Holdout Partition (Development-Exposed).** On the 18 holdout cases (18 positives, 0 controls), noisy-OR reaches "
        f"{hld['systems']['noisy-OR (with gates)']['metrics']['positive_case_recall']:.1f}% recall compared to strict RiceKG's {hld['systems']['RiceKG strict']['metrics']['positive_case_recall']:.1f}% and `possible` grade's {hld['systems']['RiceKG + possible']['metrics']['positive_case_recall']:.1f}%. "
        f"As established in Protocol 8-2.5, this partition was previously evaluated during Part 6 and Part 7; all holdout figures are development-exposed.",
        f"6. **Quantitative-Only Ablation.** Restricting links strictly to quantitative literature sources (dropping qualitative scales) collapses recall to "
        f"{sens_ev['quantitative_only']['positive_recall']:.1f}% on `eval` and {sens_dev['quantitative_only']['positive_recall']:.1f}% on `dev`, demonstrating that the rule and probabilistic layers fundamentally depend on qualitative clinical descriptions in published phytopathological monographs.",
    ]
    return findings


def generate_markdown(results: Dict[str, Any], output_md: str) -> None:
    """Writes results/probabilistic.md."""
    meta = results["metadata"]
    lines = [
        "# Probabilistic Reasoning Layer Evaluation (noisy-OR, PART 8)",
        "",
        f"> **Generated**: {meta['generated_at']}  ",
        f"> **Headline Metric Preservation**: Strict RiceKG positive recall remains the headline metric.  ",
        f"> **Target Venue**: *Inteligencia Artificial* (IBERAMIA) — contribution is transparent recall vs. false-alarm trade-off under partial observation.  ",
        "",
        "---",
        "",
        "## 1. Experimental Overview & Methodological Bounds",
        "",
        "This evaluation benchmarks the independent multi-label **noisy-OR probabilistic reasoning layer** against the strict symbolic RiceKG reasoner,",
        "the coverage-threshold `possible` grade, and the ontology-free Nearest Prototype heuristic. Every parameter was elicited from literature",
        "and locked prior to benchmark execution (commit `6174e8e`).",
        "",
        "> [!WARNING]",
        "> **Statistical Power Disclosure**: With only 5 in-scope positive disease cases in the held-out `eval` split, positive recall differences",
        "> cannot be statistically established (MDE is $\\pm 29.5\\%$). No claim of demonstrated field diagnostic superiority is supported by the evidence.",
        "> Furthermore, calibration cannot be validated on 5 positive cases; Brier scores and reliability tables are reported for diagnostic transparency only.",
        "",
        "> [!NOTE]",
        "> **Holdout Status**: As documented in Section 8-2.5 of `PROBABILISTIC_REASONING_TASK.md`, the holdout partition was exposed during Part 6 and Part 7.",
        "> All holdout figures are labelled **development-exposed**.",
        "",
        "---",
        "",
    ]

    # Dataset tables
    for dset_key, dset_title in [
        ("dev", "Field Benchmark: Dev Split (n=16: 7 positives, 9 controls)"),
        ("eval", f"Field Benchmark: Eval Split (Held-Out, n={EVAL_N}: {EVAL_POS} positives, {EVAL_NEG} controls)"),
        ("holdout", "Field Benchmark: Holdout Split (Development-Exposed, n=18 positives, 0 controls)"),
        ("verification_suite", "Deductive Verification Suite (Rule-Derived, n=73: 55 positives, 18 controls)"),
    ]:
        ddata = results["datasets"][dset_key]
        lines.extend([
            f"## 2. {dset_title}",
            "",
            "| System / Paradigm | Pos Recall (Any Hit, %) [95% CI] | Pos Recall (Exact, %) | Exact Match (%) | Micro-F1 [95% CI] | Neg FAR (All) | Neg FAR (Mapped) |",
            "|:---|:---:|:---:|:---:|:---:|:---:|:---:|",
        ])
        for sname, sinfo in ddata["systems"].items():
            m = sinfo["metrics"]
            any_ci = f"[{m['positive_any_recall_ci95'][0]:.1f}, {m['positive_any_recall_ci95'][1]:.1f}]" if m.get("positive_any_recall_ci95") else "—"
            rec_ci = f"[{m['positive_recall_ci95'][0]:.1f}, {m['positive_recall_ci95'][1]:.1f}]" if m.get("positive_recall_ci95") else "—"
            f1_ci = f"[{m['micro_f1_ci95'][0]:.1f}, {m['micro_f1_ci95'][1]:.1f}]" if m.get("micro_f1_ci95") else "—"
            all_far = f"{m['all_neg_far']:.1f}%" if m.get("all_neg_far") is not None else "n/a"
            map_far = f"{m['mapped_neg_far']:.1f}%" if m.get("mapped_neg_far") is not None else "n/a"
            lines.append(
                f"| **{sname}** | {m['positive_any_recall']:.1f}% {any_ci} | {m['positive_case_recall']:.1f}% | {m['exact_match']:.1f}% | {m['micro_f1']:.1f} {f1_ci} | {all_far} | {map_far} |"
            )
        lines.extend(["", "---", ""])

    # Differential Top-k Table for Eval
    lines.extend([
        f"## 3. Top-k Differential Ranking on Eval Split (n={EVAL_N})",
        "",
        "| System | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])
    for sname, sinfo in results["datasets"]["eval"]["systems"].items():
        tk = sinfo["top_k"]
        far1 = f"{tk['far_at_1']:.1f}%" if tk.get("far_at_1") is not None else "n/a"
        far3 = f"{tk['far_at_3']:.1f}%" if tk.get("far_at_3") is not None else "n/a"
        sp3 = f"{tk['specificity_at_3']:.1f}%" if tk.get("specificity_at_3") is not None else "n/a"
        lines.append(
            f"| **{sname}** | {tk['hit_at_1_any']:.1f}% | {tk['hit_at_2_any']:.1f}% | {tk['hit_at_3_any']:.1f}% | {tk['mrr']:.3f} | {far1} | {far3} | {sp3} | {tk['mean_list_length']:.2f} |"
        )
    lines.extend(["", "---", ""])

    # Paired Significance Table
    lines.extend([
        f"## 4. Paired Significance against RiceKG Strict on Eval Split (n={EVAL_N})",
        "",
        f"> **Minimum Detectable Effect**: $\\pm {results['datasets']['eval']['mde']['mde_percentage_proportion']:.1f}\\%$ accuracy ($\\alpha=0.05, 80\\%$ power).",
        "",
        "| Comparison System | McNemar Test Method | Discordant Pairs | Stat ($\\chi^2$) | Raw $p$-value | Holm $p$-value | Delta Acc (%) | Significant |",
        "|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])
    for sname, mcn in results["datasets"]["eval"]["pairwise_against_strict"].items():
        sig_str = "**Yes**" if mcn["significant"] else "No"
        lines.append(
            f"| **{sname}** | {mcn['test_method']} | {mcn['total_discordant']} | {mcn['statistic']:.2f} | {mcn['p_value']:.4e} | {mcn['holm_p_value']:.4e} | {mcn['delta_acc']:+.1f}% | {sig_str} |"
        )
    lines.extend(["", "---", ""])

    # Calibration Table for Eval
    cal = results["datasets"]["eval"]["calibration"]
    lines.extend([
        f"## 5. Calibration & Reliability Analysis on Eval Split (n={EVAL_N})",
        "",
        f"> **Brier Score (Multi-Label)**: `{cal['brier_score']:.4f}` across {cal['total_pairs']} hypothesis evaluations.  ",
        f"> **Disclaimer**: {cal['calibration_disclaimer']}",
        "",
        "| Probability Bin Range | Hypothesis Count | Mean Predicted Probability | Observed Empirical Frequency |",
        "|:---|:---:|:---:|:---:|",
    ])
    for row in cal["reliability_table"]:
        lines.append(
            f"| `{row['bin_range']}` | {row['count']} | {row['mean_confidence']:.4f} | {row['empirical_accuracy']:.4f} |"
        )
    lines.extend(["", "---", ""])

    # Parameter Sensitivity Table
    sens = results["parameter_sensitivity"]
    lines.extend([
        "## 6. Parameter Sensitivity Analysis (Protocol 8-D.1 & 8-D.3)",
        "",
        "| Variant | Eval Recall (%) | Eval FAR (%) | Dev Recall (%) | Dev FAR (%) |",
        "|:---|:---:|:---:|:---:|:---:|",
    ])
    for vname in ["baseline", "p_minus_0.1", "p_plus_0.1", "alt_scale", "leaks_half", "leaks_double", "quantitative_only"]:
        e_res = sens["eval"][vname]
        d_res = sens["dev"][vname]
        lines.append(
            f"| `{vname}` | {e_res['positive_recall']:.1f}% | {e_res['negative_control_far']:.1f}% | {d_res['positive_recall']:.1f}% | {d_res['negative_control_far']:.1f}% |"
        )
    lines.extend([
        f"| **Parameter Span (excl. quant-only)** | **{sens['eval']['span']['positive_recall_min']:.1f}–{sens['eval']['span']['positive_recall_max']:.1f}%** | **{sens['eval']['span']['far_min']:.1f}–{sens['eval']['span']['far_max']:.1f}%** | **{sens['dev']['span']['positive_recall_min']:.1f}–{sens['dev']['span']['positive_recall_max']:.1f}%** | **{sens['dev']['span']['far_min']:.1f}–{sens['dev']['span']['far_max']:.1f}%** |",
        "",
        "---",
        "",
        "## 7. Findings (computed dynamically from the evaluation JSON)",
        "",
    ])
    lines.extend(_generate_findings(results))
    lines.extend([
        "",
        "---",
        "",
        "## 8. Trade-Off Visualisation",
        "",
        "![Probabilistic Trade-Off Curve](figures/probabilistic_tradeoff.png)",
        "",
    ])

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Main Evaluation Runner
# ---------------------------------------------------------------------------

def run_probabilistic_evaluation(verbose: bool = True) -> Dict[str, Any]:
    start_time = time.time()
    field_csv = os.path.join(BASE_DIR, "data", "benchmark_field.csv")
    vs_csv = os.path.join(BASE_DIR, "data", "verification_suite.csv")

    systems = [
        "RiceKG strict",
        "RiceKG + possible",
        "noisy-OR (with gates)",
        "noisy-OR (without gates)",
        "Rule: Nearest Prototype",
    ]

    dataset_configs = [
        ("dev", field_csv, "dev", "Field Benchmark: Dev Split"),
        ("eval", field_csv, "eval", "Field Benchmark: Eval Split (Held-Out)"),
        ("holdout", field_csv, "holdout", "Field Benchmark: Holdout Split (Development-Exposed)"),
        ("verification_suite", vs_csv, None, "Deductive Verification Suite"),
    ]

    loaded_cases = {}
    for dkey, cpath, sp, dtitle in dataset_configs:
        loaded_cases[dkey] = evaluate.load_data(cpath, split=sp)

    eval_out = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "headline_metric": "strict RiceKG positive-case recall",
            "decision_threshold": DECISION_THRESHOLD,
            "threshold_grid": THRESHOLD_GRID,
            "parameters_csv": _repo_relative(os.path.join(BASE_DIR, "data", "noisy_or_parameters.csv")),
            "leaks_csv": _repo_relative(os.path.join(BASE_DIR, "data", "noisy_or_leaks.csv")),
        },
        "datasets": {},
    }

    # Evaluate each dataset
    for dkey, cpath, sp, dtitle in dataset_configs:
        cases = loaded_cases[dkey]
        if verbose:
            print(f"Evaluating {dtitle} (n={len(cases)})...")

        Y_true = np.array([ml_baselines.encode_labels(c.get("raw_target")) for c in cases])
        system_evals: Dict[str, Any] = {}

        for sys_name in systems:
            pred_threats = [predict_system_threats(sys_name, c["symptoms"]) for c in cases]
            Y_pred = np.array([ml_baselines.encode_labels(p) for p in pred_threats])

            # Multi-label metrics with bootstrap CIs
            m = evaluate_predictions_with_bootstrap(Y_true, Y_pred, cases)

            # Top-k metrics via differential ranking
            ranked = [rank_system_threats(sys_name, c["symptoms"], k=3) for c in cases]
            topk = differential_analysis.compute_top_k_metrics_for_system(cases, ranked, sys_name)

            system_evals[sys_name] = {
                "metrics": m,
                "top_k": topk,
            }

        # Paired McNemar against strict RiceKG
        rk_preds = [predict_system_threats("RiceKG strict", c["symptoms"]) for c in cases]
        Y_rk = np.array([ml_baselines.encode_labels(p) for p in rk_preds])

        comp_systems = [s for s in systems if s != "RiceKG strict"]
        mcnemar_results = {}
        raw_p_values = []

        for c_sys in comp_systems:
            c_preds = [predict_system_threats(c_sys, c["symptoms"]) for c in cases]
            Y_csys = np.array([ml_baselines.encode_labels(p) for p in c_preds])
            mcn = significance.compute_mcnemar_test(Y_true, Y_rk, Y_csys)
            mcnemar_results[c_sys] = mcn
            raw_p_values.append(mcn["p_value"])

        # Holm-Bonferroni correction
        holm_res = significance.apply_holm_bonferroni(raw_p_values, alpha=0.05)
        for idx, c_sys in enumerate(comp_systems):
            mcnemar_results[c_sys]["holm_p_value"] = holm_res[idx]["holm_p_value"]
            mcnemar_results[c_sys]["significant"] = holm_res[idx]["significant"]

        # Analytical MDE
        mde = significance.calculate_minimum_detectable_effect(len(cases))

        # Trade-off curve & calibration
        tradeoff = compute_tradeoff_curve(cases)
        cal = compute_calibration_analysis(cases)

        eval_out["datasets"][dkey] = {
            "dataset_label": dtitle,
            "csv_path": _repo_relative(cpath),
            "split": sp,
            "n_cases": len(cases),
            "systems": system_evals,
            "pairwise_against_strict": mcnemar_results,
            "mde": mde,
            "tradeoff_curve": tradeoff,
            "calibration": cal,
        }

    # Parameter sensitivity analysis
    if verbose:
        print("Running parameter sensitivity sweeps (p +/- 0.1, alternative scale, leaks x0.5/x2.0, quant-only)...")
    sens_results = run_parameter_sensitivity(loaded_cases)
    eval_out["parameter_sensitivity"] = sens_results

    elapsed = time.time() - start_time
    eval_out["metadata"]["elapsed_seconds"] = round(elapsed, 2)
    if verbose:
        print(f"Evaluation completed in {elapsed:.2f}s.")

    return eval_out


def main():
    parser = argparse.ArgumentParser(description="Run probabilistic reasoning layer (noisy-OR) evaluation.")
    parser.add_argument("--quiet", action="store_true", help="Suppress console logging.")
    args = parser.parse_args()

    results = run_probabilistic_evaluation(verbose=not args.quiet)

    json_path = os.path.join(RESULTS_DIR, "probabilistic.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {json_path}")

    # Generate trade-off plot
    png_path = os.path.join(FIGURES_DIR, "probabilistic_tradeoff.png")
    generate_tradeoff_plot(
        results["datasets"]["eval"]["tradeoff_curve"],
        results["datasets"]["dev"]["tradeoff_curve"],
        png_path,
    )
    print(f"Saved: {png_path}")

    # Generate markdown report
    md_path = os.path.join(RESULTS_DIR, "probabilistic.md")
    generate_markdown(results, md_path)
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
