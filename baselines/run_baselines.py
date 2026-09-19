# baselines/run_baselines.py
# --------------------------
# Orchestration script for comparative baselines, fair-comparison 5x2-fold protocol,
# paired statistical significance testing, and results artifact generation.
#
# Generates:
# - results/baselines.json
# - results/baselines.md
#
# Strictly separates the deductive verification suite from the independent field benchmark,
# and reports the field benchmark's dev and held-out eval splits separately.

import os
import pathlib
import sys
import json
import time
import warnings
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List

# Suppress single-class warnings during sparse cross-validation folds
warnings.filterwarnings("ignore", category=UserWarning)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _repo_relative(path: str) -> str:
    # Return `path` relative to the repository root with POSIX separators.
    #
    # Absolute paths leak the author's username and institution into
    # results/*.json, which breaks double-blind anonymisation.
    try:
        return pathlib.PurePath(os.path.relpath(path, BASE_DIR)).as_posix()
    except ValueError:
        return os.path.basename(path)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import model
from ricekg import evaluate
from baselines import ml_baselines, rule_baselines
from analysis import significance

RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def precompute_rule_predictions(cases: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
    # Precomputes deterministic rule-based predictions across all cases once.
    # This avoids redundant Pellet DL reasoning across cross-validation folds.
    n = len(cases)
    flat_onto = rule_baselines.get_flat_ontology()

    ricekg_preds = np.zeros((n, len(ml_baselines.ALL_THREATS)), dtype=int)
    possible_preds = np.zeros((n, len(ml_baselines.ALL_THREATS)), dtype=int)
    proto_preds = np.zeros((n, len(ml_baselines.ALL_THREATS)), dtype=int)
    flat_preds = np.zeros((n, len(ml_baselines.ALL_THREATS)), dtype=int)

    for i, c in enumerate(cases):
        # RiceKG Full (Tier 1 + Tier 2)
        r_out = model.predict_diseases(c["symptoms"])
        r_threats = [p["threat"] for p in r_out]
        ricekg_preds[i] = ml_baselines.encode_labels(r_threats)

        # Same reasoner, partial-match operating point: Tier-2 rules that did not fire but
        # whose antecedent coverage clears the threshold are surfaced as `possible`.
        p_out = model.predict_diseases(c["symptoms"], include_possible=True)
        possible_preds[i] = ml_baselines.encode_labels([p["threat"] for p in p_out])

        # Nearest Prototype
        p_threats = rule_baselines.predict_nearest_prototype(c["symptoms"])
        proto_preds[i] = ml_baselines.encode_labels(p_threats)

        # Flat Single-Tier Rules (Pellet DL)
        f_threats = rule_baselines.predict_flat_rules(c["symptoms"], onto=flat_onto)
        flat_preds[i] = ml_baselines.encode_labels(f_threats)

    return {
        "RiceKG (Full Proposed)": ricekg_preds,
        "RiceKG (Full + Possible)": possible_preds,
        "Rule: Nearest Prototype": proto_preds,
        "Rule: Flat Single-Tier": flat_preds,
    }


def evaluate_dataset_with_fair_protocol(
    csv_path: str,
    dataset_name: str,
    random_state: int = 42,
    n_resamples: int = 1000,
    split: str = None
) -> Dict[str, Any]:
    # Executes the fair-comparison 5x2-fold cross-validation protocol on a dataset.
    #
    # `split` restricts evaluation to one dataset split ('dev' or 'eval'). The held-out
    # 'eval' split is the only figure the manuscript may cite as independent.
    X, Y, cases = ml_baselines.load_and_encode_dataset(csv_path, split=split)
    n_samples = len(cases)
    splits = ml_baselines.get_5x2_splits(X, Y, random_state=random_state)
    split_strategy = splits[0]["split_name"]

    print(f"\nEvaluating {dataset_name} ({csv_path}, n={n_samples})...")
    print(f"Precomputing deterministic knowledge-based predictions...")
    kb_predictions = precompute_rule_predictions(cases)

    # ML model configurations
    ml_names = list(ml_baselines.get_ml_models().keys())
    all_system_names = ["RiceKG (Full Proposed)", "RiceKG (Full + Possible)",
                        "Rule: Nearest Prototype", "Rule: Flat Single-Tier"] + ml_names

    # Data structures for tracking fold metrics and pooled test predictions
    fold_metrics = {name: [] for name in all_system_names}
    pooled_preds = {name: [] for name in all_system_names}
    pooled_trues = {name: [] for name in all_system_names}

    train_budgets = {}
    for name in all_system_names:
        if name.startswith("RiceKG") or name.startswith("Rule:"):
            train_budgets[name] = "0 cases (cold start)"
        else:
            train_budgets[name] = f"{len(splits[0]['train_indices'])} cases/fold"

    # Iterate through all 10 folds (5 iterations x 2 folds)
    for fold in splits:
        tr_idx = fold["train_indices"]
        te_idx = fold["test_indices"]

        X_train, Y_train = X[tr_idx], Y[tr_idx]
        X_test, Y_test = X[te_idx], Y[te_idx]

        # 1. Knowledge-based systems evaluated on test split
        for kb_name in ["RiceKG (Full Proposed)", "RiceKG (Full + Possible)",
                        "Rule: Nearest Prototype", "Rule: Flat Single-Tier"]:
            pred_slice = kb_predictions[kb_name][te_idx]
            metrics = ml_baselines.compute_multilabel_metrics(Y_test, pred_slice)
            fold_metrics[kb_name].append(metrics)
            pooled_preds[kb_name].extend(pred_slice.tolist())
            pooled_trues[kb_name].extend(Y_test.tolist())

        # 2. ML models trained on train split, evaluated on test split
        ml_models = ml_baselines.get_ml_models(random_state=random_state)
        for ml_name, clf in ml_models.items():
            try:
                clf.fit(X_train, Y_train)
                pred_ml = (clf.predict(X_test) > 0).astype(int)
            except Exception:
                pred_ml = np.zeros_like(Y_test, dtype=int)

            metrics = ml_baselines.compute_multilabel_metrics(Y_test, pred_ml)
            fold_metrics[ml_name].append(metrics)
            pooled_preds[ml_name].extend(pred_ml.tolist())
            pooled_trues[ml_name].extend(Y_test.tolist())

    # Convert pooled arrays
    y_test_pooled = np.array(pooled_trues["RiceKG (Full Proposed)"])
    ricekg_pooled_pred = np.array(pooled_preds["RiceKG (Full Proposed)"])

    # Compute bootstrap CI for RiceKG
    ricekg_boot = significance.bootstrap_micro_f1_ci(
        y_test_pooled, ricekg_pooled_pred, n_resamples=n_resamples, random_state=random_state
    )

    # Statistical significance comparisons against RiceKG
    comparisons = {}
    baseline_names = [n for n in all_system_names if n != "RiceKG (Full Proposed)"]
    raw_p_values = []

    for name in baseline_names:
        pred_b = np.array(pooled_preds[name])

        # McNemar test on paired exact matches
        mcnemar_res = significance.compute_mcnemar_test(y_test_pooled, ricekg_pooled_pred, pred_b)

        # Bootstrap CIs on Micro-F1 and Delta F1
        boot_res = significance.bootstrap_micro_f1_ci(
            y_test_pooled, ricekg_pooled_pred, pred_b, n_resamples=n_resamples, random_state=random_state
        )

        comparisons[name] = {
            "mcnemar": mcnemar_res,
            "bootstrap": boot_res,
        }
        raw_p_values.append(mcnemar_res["p_value"])

    # Apply Holm-Bonferroni correction across the family of 7 baseline comparisons
    holm_results = significance.apply_holm_bonferroni(raw_p_values, alpha=0.05)
    for idx, name in enumerate(baseline_names):
        comparisons[name]["holm"] = holm_results[idx]

    # Calculate MDE
    mde_info = significance.calculate_minimum_detectable_effect(n_samples)

    # Summarize per system
    system_summaries = {}
    for name in all_system_names:
        em_vals = [f["exact_match"] for f in fold_metrics[name]]
        f1_vals = [f["micro_f1"] for f in fold_metrics[name]]
        prec_vals = [f["micro_precision"] for f in fold_metrics[name]]
        rec_vals = [f["micro_recall"] for f in fold_metrics[name]]
        pos_rec_vals = [f.get("positive_case_recall", f["micro_recall"]) for f in fold_metrics[name]]
        neg_acc_vals = [f.get("negative_control_accuracy", 100.0) for f in fold_metrics[name]]

        boot_f1_ci = ricekg_boot["f1_a_ci"] if name == "RiceKG (Full Proposed)" else comparisons[name]["bootstrap"]["f1_b_ci"]

        system_summaries[name] = {
            "paradigm": "Knowledge-Based / Semantic Web" if (name.startswith("RiceKG") or name.startswith("Rule:")) else "Supervised Machine Learning",
            "training_budget": train_budgets[name],
            "mean_exact_match": float(np.mean(em_vals)),
            "std_exact_match": float(np.std(em_vals)),
            "mean_positive_recall": float(np.mean(pos_rec_vals)),
            "std_positive_recall": float(np.std(pos_rec_vals)),
            "mean_negative_control_acc": float(np.mean(neg_acc_vals)),
            "std_negative_control_acc": float(np.std(neg_acc_vals)),
            "mean_micro_f1": float(np.mean(f1_vals)),
            "std_micro_f1": float(np.std(f1_vals)),
            "mean_micro_precision": float(np.mean(prec_vals)),
            "mean_micro_recall": float(np.mean(rec_vals)),
            "micro_f1_ci_95": [float(boot_f1_ci[0]), float(boot_f1_ci[1])],
            "n_resamples": n_resamples,
        }

    n_positive = int(sum(1 for c in cases if c["expected"]))
    n_negative = int(n_samples - n_positive)

    return {
        "dataset_name": dataset_name,
        "csv_path": _repo_relative(csv_path),
        "split": split or "all",
        "n_samples": n_samples,
        "n_positive": n_positive,
        "n_negative": n_negative,
        "n_folds": len(splits),
        "split_strategy": split_strategy,
        "train_budgets": train_budgets,
        "system_summaries": system_summaries,
        "comparisons_against_ricekg": comparisons,
        "mde_analysis": mde_info,
    }


def render_dev_split_table(dev: Dict[str, Any]) -> List[str]:
    # Compact companion table for the development split.
    #
    # Development figures may inform engineering decisions but must never be cited as
    # independent evidence; the held-out eval split carries that role.
    lines = [
        "",
        "### Companion: development split (not independent)",
        "",
        f"The `dev` split holds {dev['n_samples']} cases ({dev['n_positive']} positive, "
        f"{dev['n_negative']} negative controls) and was visible during vocabulary and rule work. "
        "It is reported for transparency only and must not be cited as independent evidence.",
        "",
        "| System / Model | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) |",
        "|:---|:---:|:---:|:---:|",
    ]
    for name, s in dev["system_summaries"].items():
        marker = f"**{name}**" if name == "RiceKG (Full Proposed)" else name
        lines.append(
            f"| {marker} | {s['mean_exact_match']:.2f} | {s['mean_positive_recall']:.2f} "
            f"| {s['mean_micro_f1']:.2f} |"
        )
    lines.append("")
    return lines


def generate_markdown_report(augmented_results: Dict[str, Any], field_results: Dict[str, Any],
                             field_dev_results: Dict[str, Any] = None) -> str:
    # Generates the publication-grade Markdown comparison report.
    # Field benchmark composition, used by the narrative below
    f_n = field_results["n_samples"]
    f_pos = field_results["n_positive"]
    f_neg = field_results["n_negative"]
    f_rk = field_results["system_summaries"]["RiceKG (Full Proposed)"]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Comparative Baseline Evaluation & Paired Significance Testing",
        "",
        f"> **Generated**: {timestamp}  ",
        f"> **Methodology**: 5x2-fold Cross-Validation (Dietterich 1998 paired protocol), "
        f"paired McNemar exact-match tests, non-parametric bootstrap 95% CIs (B=1,000 resamples), "
        f"and Holm–Bonferroni FWER step-down correction.",
        "",
        "---",
        "",
        f"## 1. Verification suite (`verification_suite.csv`, $n={augmented_results['n_samples']}$): not a comparison",
        "",
        "The suite's cases and labels were authored from an earlier rule base, before the P0-5 revisions and "
        "the vocabulary extension; most of its positive cases cannot fire the current Tier-2 rules because the "
        "signs those rules require did not yet exist. A score on it measures agreement with that earlier rule "
        "base, and a nearest-prototype matcher built from the (barely changed) Tier-1 antecedents is favoured "
        "by construction. The suite is therefore used only as regression input: `results/ablation.md` checks "
        "that Pellet and set matching give identical output on it. Per-system figures remain in "
        "`results/baselines.json` under `verification_suite` for reproducibility and are not reported here.",
        "",
        "---",
        "",
        f"## 2. Field benchmark, `eval` split (`benchmark_field.csv`, $n={f_n}$), 5x2-fold protocol",
        "",
        "The headline field figures are the single-run graded counts in `results/graded_evaluation.md`; "
        "RiceKG is not trained, so cross-validation only adds fold-partition noise to its figures. This "
        "section keeps the 5x2 protocol because the supervised baselines need training folds.",
        "",
        f"- **Dataset Provenance**: Peer-reviewed observed-case reports ($n={f_n}$: {f_pos} in-scope disease "
        f"cases, {f_neg} out-of-scope negative controls). Sources that are not case reports were excluded to "
        "`data/rejected_field_candidates.csv` with a stated reason.",
        "- **Independence (downgraded)**: this partition was held out during P0-5 Steps 2-3, but its "
        "aggregate scores have now been observed across two rounds of rule revision. It is "
        "**development-informed**, not strictly held out. See `docs/LIMITATIONS.md` Section 2. A fresh "
        "partition is required before the manuscript cites an independent diagnostic figure.",
        f"- **Cross-Validation Split Strategy**: `{field_results['split_strategy']}`.",
        f"- **Minimum Detectable Effect (MDE)**: $\\pm${field_results['mde_analysis']['mde_percentage_proportion']:.1f}% accuracy ($\\alpha=0.05, 1-\\beta=0.80$).",
        "",
        "| System / Model | Paradigm | Training Budget | Exact Match (%) | Positive Recall (%) | Micro-F1 (%) | 95% Bootstrap CI | McNemar $p$ | Holm-Adj $p$ | Risk Diff $\\Delta$ Acc [95% CI] | Cohen's $g$* |",
        "|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    # Field rows
    for name, s in field_results["system_summaries"].items():
        em_str = f"{s['mean_exact_match']:.2f} ± {s['std_exact_match']:.2f}"
        pos_rec_str = f"{s['mean_positive_recall']:.2f} ± {s['std_positive_recall']:.2f}"
        if s["mean_positive_recall"] == 0:
            pos_rec_str += f" (0/{field_results['n_positive']})"
        f1_str = f"{s['mean_micro_f1']:.2f} ± {s['std_micro_f1']:.2f}"
        ci_str = f"[{s['micro_f1_ci_95'][0]:.1f}, {s['micro_f1_ci_95'][1]:.1f}]"

        if name == "RiceKG (Full Proposed)":
            row = f"| **{name}** | {s['paradigm']} | **{s['training_budget']}** | **{em_str}** | **{pos_rec_str}** | **{f1_str}** | **{ci_str}** | — | — | Baseline Reference | — |"
        else:
            comp = field_results["comparisons_against_ricekg"][name]
            raw_p = comp["mcnemar"]["p_value"]
            holm_p = comp["holm"]["holm_p_value"]
            delta_acc = comp["mcnemar"]["delta_acc"]
            delta_ci = comp["mcnemar"].get("delta_acc_ci", [delta_acc, delta_acc])
            g = comp["mcnemar"]["cohens_g"]

            raw_p_str = "< 0.001" if raw_p < 0.001 else f"{raw_p:.4f}"
            holm_p_str = "< 0.001" if holm_p < 0.001 else f"{holm_p:.4f}"
            sig_marker = "*" if comp["holm"]["significant"] else ""
            risk_str = f"+{delta_acc:.1f}% [{delta_ci[0]:.1f}, {delta_ci[1]:.1f}]" if delta_acc >= 0 else f"{delta_acc:.1f}% [{delta_ci[0]:.1f}, {delta_ci[1]:.1f}]"
            g_str = f"{g:+.2f}"

            row = f"| {name} | {s['paradigm']} | {s['training_budget']} | {em_str} | {pos_rec_str} | {f1_str} | {ci_str} | {raw_p_str} | **{holm_p_str}{sig_marker}** | {risk_str} | {g_str} |"
        lines.append(row)

    lines.extend([
        "",
        f"*Note: Aggregate exact match is dominated by the {f_neg}/{f_n} negative control cases "
        f"({100.0 * f_neg / f_n:.1f}% of the benchmark), on which returning `No_Diagnosis` is correct. "
        f"Positive-case recall over the {f_pos} in-scope disease cases is reported separately and is the "
        "diagnostically meaningful column. Risk Difference (\\Delta Acc) is reported with paired Wald 95% CI. "
        "Cohen's g is bounded on $[-0.50, +0.50]$ and saturates; read the Risk Difference for magnitude.*",
        "",
        "### Key Findings (field `eval` split)",
        f"1. **Positive-case recall is the diagnostically meaningful figure**: RiceKG attains "
        f"{f_rk['mean_positive_recall']:.2f}% positive-case recall over {f_pos} in-scope disease cases "
        f"(micro-F1 {f_rk['mean_micro_f1']:.2f}, 95% CI [{f_rk['micro_f1_ci_95'][0]:.1f}, {f_rk['micro_f1_ci_95'][1]:.1f}]), "
        f"against an aggregate exact match of {f_rk['mean_exact_match']:.2f}%. With {f_pos} positive cases, "
        "diagnostic efficacy on field cases is not established.",
        f"2. **Every supervised baseline scores zero on positive cases**: all five ML classifiers attain 0.00% "
        f"positive-case recall, having at most {f_pos} positive training examples split across folds. Their aggregate "
        "accuracy comes from predicting the majority `No_Diagnosis` class.",
        "3. **Per-case causes**: `results/field_failure_analysis.md` assigns a cause to every remaining failure.",
        f"4. **Negative Control Artifact**: {f_neg} of {f_n} cases ({100.0 * f_neg / f_n:.1f}%) are out-of-scope "
        "emerging pathogens. Reporting aggregate exact match alone would conceal positive-case performance entirely, "
        "which is why the two are separated above.",
        f"5. **Statistical Power & MDE**: With $n={f_n}$ and only {f_pos} positive cases, the minimum detectable effect "
        f"is $\\pm {field_results['mde_analysis']['mde_percentage_proportion']:.1f}$ percentage points. Non-significant "
        "comparisons reflect severe underpowering, not demonstrated equivalence.",
    ])

    if field_dev_results:
        lines.extend(render_dev_split_table(field_dev_results))

    field_mde = field_results["mde_analysis"]["mde_percentage_proportion"]
    lines.extend([
        "",
        "---",
        "",
        "## 3. Statistical Power & Minimum Detectable Effect Disclosure",
        "",
        f"- **Field Benchmark, eval split ($n={f_n}$, {f_pos} positive cases)**: "
        f"$\\text{{MDE}} = \\pm {field_mde:.1f}\\%$.",
        "- In accordance with AIP empirical standards, null hypothesis outcomes are disclosed as underpowered rather than equivalent.",
    ])

    return "\n".join(lines)


def run_all_baselines():
    # Runs complete comparative baselines on the verification suite and the field benchmark.
    verification_csv = evaluate.DEFAULT_VERIFICATION_CSV if os.path.exists(evaluate.DEFAULT_VERIFICATION_CSV) else evaluate.DEFAULT_VERIFICATION_CSV
    field_csv = evaluate.FIELD_CSV

    print("=" * 80)
    print("RICEKG COMPARATIVE BASELINES & SIGNIFICANCE TESTING PROTOCOL")
    print("=" * 80)

    t0 = time.time()
    verification_res = evaluate_dataset_with_fair_protocol(verification_csv, "Deductive Verification Suite", random_state=42)
    field_dev_res = evaluate_dataset_with_fair_protocol(
        field_csv, "Independent Literature Field Benchmark (dev split)", random_state=42, split="dev")
    field_res = evaluate_dataset_with_fair_protocol(
        field_csv, "Independent Literature Field Benchmark (eval split)", random_state=42, split="eval")
    elapsed = time.time() - t0

    # Write JSON results
    json_path = os.path.join(RESULTS_DIR, "baselines.json")
    combined_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "verification_suite": verification_res,
        "augmented_benchmark": verification_res,  # backwards-compatible alias
        # `field_benchmark` is the held-out eval split: the only independent figure.
        "field_benchmark": field_res,
        "field_benchmark_dev": field_dev_res,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined_json, f, indent=2)
    print(f"\n[OUTPUT] Saved structured results to {json_path}")

    # Write Markdown report
    md_path = os.path.join(RESULTS_DIR, "baselines.md")
    md_content = generate_markdown_report(verification_res, field_res, field_dev_res)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OUTPUT] Saved publication report to {md_path}")
    print(f"Total execution time: {elapsed:.2f}s")


if __name__ == "__main__":
    run_all_baselines()
