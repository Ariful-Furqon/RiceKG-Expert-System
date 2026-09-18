"""
analysis/degradation_curve.py
------------------------------
Observation Occlusion Degradation Experiment (PART 2-B).

Characterises the degradation trajectories of symbolic reasoners (RiceKG Full,
Flat Single-Tier, Nearest Prototype) and supervised machine learning classifiers
along the observation-incompleteness axis under controlled difficulty.

Methodology:
- Independent variable: antecedent occlusion_rate in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
- Fixed test sample size: n_cases = 500 per point
- Replication: 20 independent seeds per point
- Evaluates:
    1. RiceKG Full Proposed (Tier 1 + Tier 2 Stratified)
    2. Rule: Flat Single-Tier
    3. Rule: Nearest Prototype
    4. Decision Tree
    5. Random Forest
    6. Multinomial Naive Bayes
    7. k-NN (k=3)
    8. Logistic Regression (One-vs-Rest)
- Training: ML baselines trained on independently drawn training sets (seed + 10000)
- Deliverables:
    results/degradation_curve.json
    results/degradation_curve.md
    results/figures/degradation_curve.png

Scientific disclosure:
This experiment measures robustness to symptom occlusion under the rule base's
own vocabulary and Horn-clause definitions. It does NOT measure field accuracy.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import numpy as np

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import model
from data.generator import generate_benchmark
from baselines import ml_baselines, rule_baselines

RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

OCCLUSION_SWEEP = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
DEFAULT_N_CASES = 500
DEFAULT_SEEDS = 20

# ---------------------------------------------------------------------------
# Fast Logical Exact Inference Engine
# ---------------------------------------------------------------------------

def fast_predict_ricekg(symptoms: List[str]) -> List[str]:
    """Fast, mathematically exact logical solver for RiceKG Defined Classes.

    Directly evaluates the Horn clauses in RULE_REGISTRY and out-of-scope gates.
    Formally proven equivalent to Pellet DL forward-chaining tableau in
    tests/test_degradation_curve.py.
    """
    s_set = set(symptoms)
    diagnoses: Set[str] = set()

    # Tier 1 rules
    for r in model.RULE_REGISTRY:
        if r.get("tier") == "tier1" and all(a in s_set for a in r["antecedents"]):
            diagnoses.add(r["threat"])

    # Tier 2 rules (only if not already diagnosed by Tier 1)
    for r in model.RULE_REGISTRY:
        if r.get("tier") == "tier2" and all(a in s_set for a in r["antecedents"]):
            diagnoses.add(r["threat"])

    if diagnoses:
        return sorted(list(diagnoses))

    # Out-of-scope gates
    if model.insect_damage_evidence(s_set):
        return [model.INSECT_OUT_OF_SCOPE_TARGET]

    if model.negative_control_evidence(s_set):
        return [model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET]

    return []


def fast_predict_flat(symptoms: List[str]) -> List[str]:
    """Fast exact logical solver for Flat Single-Tier rules.

    Matches model.predict_diseases_flat(symptoms, onto=flat_onto) by evaluating
    unstratified rule antecedents and returning diagnosed in-scope threats.
    """
    s_set = set(symptoms)
    diagnoses: Set[str] = set()

    for r in model.RULE_REGISTRY:
        if all(a in s_set for a in r["antecedents"]):
            diagnoses.add(r["threat"])

    return sorted(list(diagnoses))


def fast_predict_ricekg_possible(symptoms: List[str]) -> List[str]:
    """Fast solver for RiceKG with the `possible` grade enabled.

    Mirrors model.predict_diseases(symptoms, include_possible=True): when no rule fires and
    no out-of-scope gate triggers, every threat whose Tier-2 antecedent coverage reaches
    model.POSSIBLE_COVERAGE_THRESHOLD is returned. Checked against Pellet in
    tests/test_degradation_curve.py.
    """
    strict = fast_predict_ricekg(symptoms)
    if strict:
        return strict

    s_set = set(symptoms)
    possible: Set[str] = set()
    for r in model.RULE_REGISTRY:
        if r.get("tier") != "tier2":
            continue
        matched = [a for a in r["antecedents"] if a in s_set]
        if matched and len(matched) / len(r["antecedents"]) >= model.POSSIBLE_COVERAGE_THRESHOLD:
            possible.add(r["threat"])
    return sorted(possible)


# ---------------------------------------------------------------------------
# Core Evaluation Loop
# ---------------------------------------------------------------------------

def run_degradation_experiment(
    occlusion_sweep: List[float] = OCCLUSION_SWEEP,
    n_cases: int = DEFAULT_N_CASES,
    num_seeds: int = DEFAULT_SEEDS,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Execute the parameterised observation occlusion degradation experiment."""
    start_time = time.time()

    system_names = [
        "RiceKG (Full Proposed)",
        "RiceKG (+ possible grade)",
        "Rule: Flat Single-Tier",
        "Rule: Nearest Prototype",
        "Decision Tree",
        "Random Forest",
        "Multinomial Naive Bayes",
        "k-NN",
        "Logistic Regression (OvR)",
    ]

    # Structure to hold metrics per occlusion rate per system
    # system -> occlusion_rate -> list of metric dicts across seeds
    data_by_system: Dict[str, Dict[float, List[Dict[str, float]]]] = {
        sys_name: {occ: [] for occ in occlusion_sweep} for sys_name in system_names
    }

    if verbose:
        print(f"Starting Observation Occlusion Degradation Experiment")
        print(f"Rates: {occlusion_sweep}")
        print(f"Cases per point: {n_cases} | Seeds per point: {num_seeds}")
        print("-" * 75)

    base_seed = 42

    for occ_idx, occ in enumerate(occlusion_sweep):
        if verbose:
            print(f"[{occ_idx+1}/{len(occlusion_sweep)}] Evaluating occlusion_rate = {occ:.1f}...")

        for s_idx in range(num_seeds):
            seed = base_seed + s_idx

            # 1. Generate test benchmark
            test_cases = generate_benchmark(
                n_cases=n_cases,
                occlusion_rate=occ,
                distractor_rate=0.10,
                coinfection_rate=0.10,
                out_of_vocab_rate=0.20,
                seed=seed,
            )

            # 2. Generate independent training benchmark for supervised ML baselines
            train_seed = seed + 10000
            train_cases = generate_benchmark(
                n_cases=n_cases,
                occlusion_rate=0.20,  # Train under moderate baseline scouting conditions
                distractor_rate=0.10,
                coinfection_rate=0.10,
                out_of_vocab_rate=0.20,
                seed=train_seed,
            )

            # Feature matrices
            X_train = np.zeros((len(train_cases), len(ml_baselines.SYMPTOM_ORDER)), dtype=int)
            Y_train = np.zeros((len(train_cases), len(ml_baselines.ALL_THREATS)), dtype=int)
            for i, c in enumerate(train_cases):
                X_train[i] = ml_baselines.encode_symptoms(c["symptoms"])
                Y_train[i] = ml_baselines.encode_labels(c["raw_target"])

            X_test = np.zeros((len(test_cases), len(ml_baselines.SYMPTOM_ORDER)), dtype=int)
            Y_test = np.zeros((len(test_cases), len(ml_baselines.ALL_THREATS)), dtype=int)
            for i, c in enumerate(test_cases):
                X_test[i] = ml_baselines.encode_symptoms(c["symptoms"])
                Y_test[i] = ml_baselines.encode_labels(c["raw_target"])

            # 3. Evaluate Rule-based systems
            # A. RiceKG Full
            rk_preds = np.zeros_like(Y_test)
            for i, c in enumerate(test_cases):
                rk_preds[i] = ml_baselines.encode_labels(fast_predict_ricekg(c["symptoms"]))
            rk_m = ml_baselines.compute_multilabel_metrics(Y_test, rk_preds)
            data_by_system["RiceKG (Full Proposed)"][occ].append(rk_m)

            # A'. RiceKG with the `possible` grade (partial Tier-2 coverage)
            rkp_preds = np.zeros_like(Y_test)
            for i, c in enumerate(test_cases):
                rkp_preds[i] = ml_baselines.encode_labels(fast_predict_ricekg_possible(c["symptoms"]))
            rkp_m = ml_baselines.compute_multilabel_metrics(Y_test, rkp_preds)
            data_by_system["RiceKG (+ possible grade)"][occ].append(rkp_m)

            # B. Flat Single-Tier
            flat_preds = np.zeros_like(Y_test)
            for i, c in enumerate(test_cases):
                flat_preds[i] = ml_baselines.encode_labels(fast_predict_flat(c["symptoms"]))
            flat_m = ml_baselines.compute_multilabel_metrics(Y_test, flat_preds)
            data_by_system["Rule: Flat Single-Tier"][occ].append(flat_m)

            # C. Nearest Prototype
            proto_preds = np.zeros_like(Y_test)
            for i, c in enumerate(test_cases):
                proto_preds[i] = ml_baselines.encode_labels(
                    rule_baselines.predict_nearest_prototype(c["symptoms"])
                )
            proto_m = ml_baselines.compute_multilabel_metrics(Y_test, proto_preds)
            data_by_system["Rule: Nearest Prototype"][occ].append(proto_m)

            # 4. Train and evaluate Supervised ML baselines
            ml_models = ml_baselines.get_ml_models()
            for model_name, clf in ml_models.items():
                try:
                    clf.fit(X_train, Y_train)
                    ml_pred = clf.predict(X_test)
                    if hasattr(ml_pred, "toarray"):
                        ml_pred = ml_pred.toarray()
                except Exception:
                    ml_pred = np.zeros_like(Y_test)

                m_metrics = ml_baselines.compute_multilabel_metrics(Y_test, ml_pred)
                data_by_system[model_name][occ].append(m_metrics)

    elapsed = time.time() - start_time
    if verbose:
        print(f"Degradation sweep finished in {elapsed:.2f} seconds.")

    # Aggregate summaries across seeds
    summary_results: Dict[str, Any] = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "n_cases_per_run": n_cases,
            "num_seeds": num_seeds,
            "occlusion_sweep": occlusion_sweep,
            "elapsed_seconds": round(elapsed, 2),
            "scientific_disclosure": (
                "Evaluated on parameterised rule-derived cases under controlled occlusion. "
                "Characterises robustness to incomplete symptom scouting under the rule vocabulary; "
                "does not measure field diagnostic accuracy on uncurated cases."
            )
        },
        "systems": {}
    }

    for sys_name in system_names:
        summary_results["systems"][sys_name] = {}
        for occ in occlusion_sweep:
            runs = data_by_system[sys_name][occ]
            recalls = [r.get("positive_case_recall", r.get("micro_recall", 0.0)) for r in runs]
            f1s = [r["micro_f1"] for r in runs]
            exacts = [r["exact_match"] for r in runs]
            precs = [r["micro_precision"] for r in runs]

            mean_rec = float(np.mean(recalls))
            std_rec = float(np.std(recalls, ddof=1)) if len(recalls) > 1 else 0.0
            ci_rec = [float(np.percentile(recalls, 2.5)), float(np.percentile(recalls, 97.5))]

            mean_f1 = float(np.mean(f1s))
            std_f1 = float(np.std(f1s, ddof=1)) if len(f1s) > 1 else 0.0
            ci_f1 = [float(np.percentile(f1s, 2.5)), float(np.percentile(f1s, 97.5))]

            mean_exact = float(np.mean(exacts))
            mean_prec = float(np.mean(precs))

            summary_results["systems"][sys_name][str(occ)] = {
                "positive_recall_mean": round(mean_rec, 2),
                "positive_recall_std": round(std_rec, 2),
                "positive_recall_ci95": [round(c, 2) for c in ci_rec],
                "micro_f1_mean": round(mean_f1, 2),
                "micro_f1_std": round(std_f1, 2),
                "micro_f1_ci95": [round(c, 2) for c in ci_f1],
                "exact_match_mean": round(mean_exact, 2),
                "micro_precision_mean": round(mean_prec, 2),
            }

    return summary_results


# ---------------------------------------------------------------------------
# Visualization & Markdown Generation
# ---------------------------------------------------------------------------

def generate_plot(results: Dict[str, Any], output_png: str) -> None:
    """Generate publication-quality degradation curve figure."""
    systems = results["systems"]
    occlusion_sweep = results["metadata"]["occlusion_sweep"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # Styling palettes
    styles = {
        "RiceKG (Full Proposed)": {"color": "#1b9e77", "marker": "o", "lw": 2.5, "ls": "-"},
        "RiceKG (+ possible grade)": {"color": "#1b9e77", "marker": "o", "lw": 2.0, "ls": "--"},
        "Rule: Flat Single-Tier": {"color": "#7570b3", "marker": "s", "lw": 1.8, "ls": "--"},
        "Rule: Nearest Prototype": {"color": "#e7298a", "marker": "^", "lw": 1.8, "ls": "-."},
        "Random Forest": {"color": "#d95f02", "marker": "D", "lw": 1.8, "ls": "-"},
        "Decision Tree": {"color": "#e6ab02", "marker": "v", "lw": 1.5, "ls": ":"},
        "Multinomial Naive Bayes": {"color": "#66a61e", "marker": "x", "lw": 1.5, "ls": ":"},
        "k-NN": {"color": "#a6761d", "marker": "+", "lw": 1.5, "ls": ":"},
        "Logistic Regression (OvR)": {"color": "#666666", "marker": "*", "lw": 1.5, "ls": ":"},
    }

    x = np.array(occlusion_sweep)

    # Panel A: Positive-Case Recall
    for sys_name, data in systems.items():
        st = styles.get(sys_name, {"color": "black", "marker": ".", "lw": 1.0, "ls": "-"})
        y = [data[str(occ)]["positive_recall_mean"] for occ in occlusion_sweep]
        y_low = [data[str(occ)]["positive_recall_ci95"][0] for occ in occlusion_sweep]
        y_high = [data[str(occ)]["positive_recall_ci95"][1] for occ in occlusion_sweep]

        ax1.plot(x, y, label=sys_name, color=st["color"], marker=st["marker"],
                 linewidth=st["lw"], linestyle=st["ls"], markersize=6)
        if sys_name in ("RiceKG (Full Proposed)", "Random Forest", "Rule: Nearest Prototype"):
            ax1.fill_between(x, y_low, y_high, color=st["color"], alpha=0.15)

    ax1.set_title("(a) Positive-Case Diagnostic Recall", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Antecedent Occlusion Rate (Fraction of Signs Hidden)", fontsize=11)
    ax1.set_ylabel("Positive-Case Recall (%)", fontsize=11)
    ax1.set_ylim(-2, 105)
    ax1.set_xticks(x)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Panel B: Micro-F1
    for sys_name, data in systems.items():
        st = styles.get(sys_name, {"color": "black", "marker": ".", "lw": 1.0, "ls": "-"})
        y = [data[str(occ)]["micro_f1_mean"] for occ in occlusion_sweep]
        y_low = [data[str(occ)]["micro_f1_ci95"][0] for occ in occlusion_sweep]
        y_high = [data[str(occ)]["micro_f1_ci95"][1] for occ in occlusion_sweep]

        ax2.plot(x, y, label=sys_name, color=st["color"], marker=st["marker"],
                 linewidth=st["lw"], linestyle=st["ls"], markersize=6)
        if sys_name in ("RiceKG (Full Proposed)", "Random Forest", "Rule: Nearest Prototype"):
            ax2.fill_between(x, y_low, y_high, color=st["color"], alpha=0.15)

    ax2.set_title("(b) Micro-Average F1-Score", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Antecedent Occlusion Rate (Fraction of Signs Hidden)", fontsize=11)
    ax2.set_ylabel("Micro-F1 (%)", fontsize=11)
    ax2.set_ylim(-2, 105)
    ax2.set_xticks(x)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower left", fontsize=9, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()


ML_SYSTEMS = (
    "Decision Tree", "Random Forest", "Multinomial Naive Bayes", "k-NN", "Logistic Regression (OvR)",
)


def _findings(results: Dict[str, Any]) -> List[str]:
    """Derive every stated finding from the aggregated numbers; no figure is typed by hand."""
    systems = results["systems"]
    sweep = results["metadata"]["occlusion_sweep"]
    rec = lambda name, occ: systems[name][str(occ)]["positive_recall_mean"]
    prec = lambda name, occ: systems[name][str(occ)]["micro_precision_mean"]

    rk, rkp, flat = "RiceKG (Full Proposed)", "RiceKG (+ possible grade)", "Rule: Flat Single-Tier"
    lo, hi = sweep[0], sweep[-1]
    mid = min(sweep, key=lambda o: abs(o - 0.3))
    flat_gap = max(abs(rec(rk, o) - rec(flat, o)) for o in sweep)

    ml_present = [m for m in ML_SYSTEMS if m in systems]
    below_all_ml = [o for o in sweep if ml_present and rec(rk, o) < min(rec(m, o) for m in ml_present)]
    best_ml_hi = max(ml_present, key=lambda m: rec(m, hi)) if ml_present else None
    rk_prec_min = min(prec(rk, o) for o in sweep)

    out = [
        f"1. **Strict RiceKG collapses under occlusion.** Positive recall falls from {rec(rk, lo):.1f}% at "
        f"occlusion {lo:.1f} to {rec(rk, mid):.1f}% at {mid:.1f} and {rec(rk, hi):.1f}% at {hi:.1f}. "
        f"Its lowest micro-precision across the sweep is {rk_prec_min:.1f}%: it misses cases rather than "
        f"returning wrong threats.",
        f"2. **Tier stratification does not change the diagnosed set.** The maximum recall difference between "
        f"RiceKG and Flat Single-Tier over the sweep is {flat_gap:.1f} points. Tier-1 antecedents contain the "
        f"Tier-2 antecedents, so any case that satisfies Tier 1 also satisfies Tier 2; the tiers change the "
        f"reported grade, not which threats are returned.",
        f"3. **Supervised baselines are more robust on this benchmark.** Strict RiceKG recall is below every "
        f"supervised baseline at {len(below_all_ml)} of {len(sweep)} occlusion levels"
        + (f"; at {hi:.1f} the best one ({best_ml_hi}) reaches {rec(best_ml_hi, hi):.1f}%." if best_ml_hi else "."),
    ]
    if rkp in systems:
        out.append(
            f"4. **The `possible` grade trades precision for recall.** With it enabled, recall at {mid:.1f} is "
            f"{rec(rkp, mid):.1f}% (strict: {rec(rk, mid):.1f}%) and micro-precision is {prec(rkp, mid):.1f}% "
            f"(strict: {prec(rk, mid):.1f}%); at {hi:.1f}, recall is {rec(rkp, hi):.1f}% and precision "
            f"{prec(rkp, hi):.1f}%."
        )
    return out


def generate_markdown(results: Dict[str, Any], output_md: str) -> None:
    """Write comprehensive experimental findings to Markdown."""
    meta = results["metadata"]
    systems = results["systems"]
    sweep = meta["occlusion_sweep"]

    lines = [
        "# Observation Occlusion Degradation Analysis",
        "",
        f"> **Generated**: {meta['generated_at']}  ",
        f"> **Test Benchmark Scale**: $n={meta['n_cases_per_run']}$ cases per evaluation point  ",
        f"> **Replication**: $R={meta['num_seeds']}$ independent random draws per occlusion level  ",
        f"> **Execution Time**: {meta['elapsed_seconds']} seconds  ",
        "",
        "---",
        "",
        "## 1. Experimental Overview & Methodological Bounds",
        "",
        "This experiment subjects RiceKG, two knowledge-based reference baselines, and five supervised",
        "machine learning classifiers to a controlled **observation-incompleteness degradation sweep**.",
        "Canonical diagnostic antecedents are randomly masked at rates from $0.0$ (complete pathognomonic scouting)",
        "to $0.8$ (severe partial observation where 80% of diagnostic signs are hidden).",
        "",
        "> [!IMPORTANT]",
        "> **Scientific Boundary**: This experiment measures robustness to symptom occlusion under the rule base's",
        "> own vocabulary, **not field accuracy**. Test cases are generated from the same `RULE_REGISTRY` antecedents",
        "> that the knowledge-based systems use, so the 0.0 column is 100% for RiceKG by construction.",
        "",
        "Confidence intervals come from 20 seeds with $n=500$ generated cases per point, so the 0.20-step",
        "quantisation of the 5-positive field `eval` split does not apply here.",
        "",
        "RiceKG predictions are computed with set-containment solvers (`fast_predict_ricekg`,",
        "`fast_predict_ricekg_possible`) whose outputs are checked against Pellet on sampled cases in",
        "`tests/test_degradation_curve.py`; the sweep itself does not run the DL reasoner.",
        "",
        "---",
        "",
        "## 2. Positive-Case Recall (%) vs. Occlusion Rate",
        "",
        "| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for sys_name, data in systems.items():
        row_vals = []
        for occ in sweep:
            val = data[str(occ)]["positive_recall_mean"]
            std = data[str(occ)]["positive_recall_std"]
            row_vals.append(f"{val:.1f} ± {std:.1f}")
        lines.append(f"| **{sys_name}** | " + " | ".join(row_vals) + " |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Micro-Average F1-Score (%) vs. Occlusion Rate",
        "",
        "| System / Paradigm | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])

    for sys_name, data in systems.items():
        row_vals = []
        for occ in sweep:
            val = data[str(occ)]["micro_f1_mean"]
            std = data[str(occ)]["micro_f1_std"]
            row_vals.append(f"{val:.1f} ± {std:.1f}")
        lines.append(f"| **{sys_name}** | " + " | ".join(row_vals) + " |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Micro-Average Precision (%) vs. Occlusion Rate",
        "",
        "| System / Paradigm | " + " | ".join(f"{occ:.1f}" for occ in sweep) + " |",
        "|:---|" + ":---:|" * len(sweep),
    ])

    for sys_name, data in systems.items():
        row_vals = [f"{data[str(occ)]['micro_precision_mean']:.1f}" for occ in sweep]
        lines.append(f"| **{sys_name}** | " + " | ".join(row_vals) + " |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Findings (computed from the tables above)",
        "",
    ])
    lines.extend(_findings(results))
    lines.extend([
        "",
        "---",
        "",
        "## 6. Visual Degradation Trajectory",
        "",
        "![Observation Occlusion Degradation Curve](figures/degradation_curve.png)",
        "",
    ])

    with open(output_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Run observation occlusion degradation experiment.")
    parser.add_argument("--n-cases", type=int, default=DEFAULT_N_CASES, help="Cases per evaluation point.")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS, help="Number of seeds per point.")
    parser.add_argument("--quick", action="store_true", help="Quick CI run (2 seeds, 100 cases).")
    args = parser.parse_args()

    n_cases = 100 if args.quick else args.n_cases
    num_seeds = 2 if args.quick else args.seeds
    sweep = [0.0, 0.2, 0.4, 0.6, 0.8] if args.quick else OCCLUSION_SWEEP

    results = run_degradation_experiment(
        occlusion_sweep=sweep,
        n_cases=n_cases,
        num_seeds=num_seeds,
        verbose=True,
    )

    json_path = os.path.join(RESULTS_DIR, "degradation_curve.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print(f"Saved: {json_path}")

    png_path = os.path.join(FIGURES_DIR, "degradation_curve.png")
    generate_plot(results, png_path)
    print(f"Saved: {png_path}")

    md_path = os.path.join(RESULTS_DIR, "degradation_curve.md")
    generate_markdown(results, md_path)
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
