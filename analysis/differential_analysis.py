"""
analysis/differential_analysis.py
---------------------------------
Top-k Differential Diagnosis & Ranking Evaluation (PART 7).

Evaluates RiceKG and comparative baselines under a top-k ranking protocol:
- Metrics: Hit@1, Hit@2, Hit@3, MRR, Mean List Length, and Negative-Control False Alarm Rate (FAR@k).
- Evaluates:
    1. RiceKG Full Proposed (graded DL / Defined Classes)
    2. Rule: Nearest Prototype (ranked via Jaccard/overlap scores)
    3. Rule: Flat Single-Tier (unranked; reported as top-1 only per Part 7-C)
    4. Decision Tree (ranked via predict_proba)
    5. Random Forest (ranked via predict_proba)
    6. Multinomial Naive Bayes (ranked via predict_proba)
    7. k-NN (ranked via predict_proba)
    8. Logistic Regression (OvR) (ranked via decision_function / predict_proba)
- Datasets:
    - Independent Field Benchmark (dev, eval, holdout)
    - Deductive Verification Suite (n=73)

Generates:
    results/top_k.json
    results/top_k.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import model
from ricekg import evaluate
from baselines import ml_baselines, rule_baselines

RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

ALL_THREATS = model.ALL_DIAGNOSES


# ---------------------------------------------------------------------------
# Ranking Extractors for Baselines
# ---------------------------------------------------------------------------

def rank_nearest_prototype(symptoms: List[str], k: int = 3) -> List[str]:
    """Rank in-scope threats using Nearest Prototype similarity scores."""
    obs_set = set(symptoms)
    if not obs_set:
        return []

    scores = []
    for threat, proto_set in rule_baselines.THREAT_PROTOTYPES.items():
        overlap = len(obs_set & proto_set)
        union = len(obs_set | proto_set)
        jaccard = overlap / union if union > 0 else 0.0
        if overlap > 0:
            scores.append({"threat": threat, "overlap": overlap, "jaccard": jaccard})

    scores.sort(key=lambda x: (-x["overlap"], -x["jaccard"], x["threat"]))
    return [s["threat"] for s in scores[:k]]


def rank_ml_predictions(probs: np.ndarray, k: int = 3, threshold: float = 0.05) -> List[str]:
    """Rank in-scope threats from ML classifier probability estimates."""
    ranked_indices = np.argsort(-probs)
    candidates = []
    for idx in ranked_indices:
        if probs[idx] >= threshold:
            candidates.append(ALL_THREATS[idx])
        if len(candidates) >= k:
            break
    return candidates


# ---------------------------------------------------------------------------
# Metric Evaluation Functions
# ---------------------------------------------------------------------------

def compute_top_k_metrics_for_system(
    cases: List[Dict[str, Any]],
    ranked_predictions: List[List[str]],
    system_name: str,
    k_vals: Tuple[int, ...] = (1, 2, 3),
) -> Dict[str, Any]:
    """Computes Hit@k, MRR, Mean List Length, and Negative-Control False Alarm Rate at k."""
    pos_cases = []
    neg_cases = []

    for c, preds in zip(cases, ranked_predictions):
        exp = set(c["expected"])
        is_pos = (c.get("raw_target") != "No_Diagnosis") and (len(exp) > 0)
        if is_pos:
            pos_cases.append({"expected": exp, "preds": preds})
        else:
            neg_cases.append({"expected": set(), "preds": preds})

    n_pos = len(pos_cases)
    n_neg = len(neg_cases)
    total_cases = len(cases)

    # 1. Positive case metrics: Hit@k (any & all), MRR
    hit_any = {k: 0 for k in k_vals}
    hit_all = {k: 0 for k in k_vals}
    rr_sum = 0.0

    for item in pos_cases:
        exp = item["expected"]
        preds = item["preds"]

        for k in k_vals:
            sub_preds = set(preds[:k])
            if any(p in exp for p in sub_preds):
                hit_any[k] += 1
            if exp.issubset(sub_preds):
                hit_all[k] += 1

        # Reciprocal Rank of first true positive
        rr = 0.0
        for rank_idx, p in enumerate(preds[:max(k_vals)], 1):
            if p in exp:
                rr = 1.0 / rank_idx
                break
        rr_sum += rr

    # 2. Negative control metrics: False Alarm Rate at k, Specificity at k
    far_k = {k: 0 for k in k_vals}
    for item in neg_cases:
        preds = item["preds"]
        for k in k_vals:
            sub_preds = [p for p in preds[:k] if p in ALL_THREATS]
            if len(sub_preds) > 0:
                far_k[k] += 1

    # 3. List length
    total_len = sum(min(len(p), max(k_vals)) for p in ranked_predictions)
    mean_len = total_len / total_cases if total_cases > 0 else 0.0

    results = {
        "system": system_name,
        "n_total": total_cases,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "mean_list_length": round(mean_len, 2),
        "mrr": round(rr_sum / n_pos, 4) if n_pos > 0 else 0.0,
    }

    for k in k_vals:
        hit_any_pct = (hit_any[k] / n_pos * 100.0) if n_pos > 0 else 0.0
        hit_all_pct = (hit_all[k] / n_pos * 100.0) if n_pos > 0 else 0.0

        results[f"hit_at_{k}_any"] = round(hit_any_pct, 2)
        results[f"hit_at_{k}_all"] = round(hit_all_pct, 2)
        # Without negative controls the false-alarm rate is undefined, not zero.
        if n_neg > 0:
            far_pct = far_k[k] / n_neg * 100.0
            results[f"far_at_{k}"] = round(far_pct, 2)
            results[f"specificity_at_{k}"] = round(100.0 - far_pct, 2)
        else:
            results[f"far_at_{k}"] = None
            results[f"specificity_at_{k}"] = None

    return results


def _positive_class_probs(probs) -> np.ndarray:
    """Stack per-label positive-class probabilities from a multi-output predict_proba."""
    if isinstance(probs, list):
        return np.column_stack([p[:, 1] if p.shape[1] > 1 else p[:, 0] for p in probs])
    return probs


def knn_tie_sensitivity(
    X: np.ndarray,
    Y: np.ndarray,
    cases: List[Dict[str, Any]],
    train_idx,
    test_idx,
    n_orders: int = 20,
    seed: int = 0,
) -> Dict[str, Any]:
    """Quantify how much the k-NN top-k metrics depend on neighbour tie-breaking.

    Binary symptom vectors yield many equidistant neighbours, and sklearn resolves ties by
    training-row order. The same 2-fold split is re-run with `n_orders` permutations of the
    training rows; the returned spans show the range of metrics attributable to tie-breaking
    alone. `tie_at_k_boundary` counts held-out predictions whose 3rd and 4th nearest training
    rows are equally distant.
    """
    tr, te = np.asarray(train_idx), np.asarray(test_idx)
    k = ml_baselines.get_ml_models()["k-NN"].n_neighbors

    ties = 0
    for a, b in [(tr, te), (te, tr)]:
        dists = np.sqrt(((X[b][:, None, :] - X[a][None, :, :]) ** 2).sum(-1))
        for row in dists:
            s = np.sort(row)
            if len(s) > k and np.isclose(s[k - 1], s[k]):
                ties += 1

    rng = np.random.RandomState(seed)
    outcomes = []
    for _ in range(n_orders):
        ranked: List[List[str]] = [[] for _ in cases]
        for a, b in [(tr, te), (te, tr)]:
            a = rng.permutation(a)
            clf = ml_baselines.get_ml_models()["k-NN"]
            clf.fit(X[a], Y[a])
            prob_matrix = _positive_class_probs(clf.predict_proba(X[b]))
            for local_i, global_i in enumerate(b):
                ranked[global_i] = rank_ml_predictions(prob_matrix[local_i], k=3)
        outcomes.append(compute_top_k_metrics_for_system(cases, ranked, "k-NN"))

    def span(key):
        vals = [o[key] for o in outcomes if o[key] is not None]
        return [min(vals), max(vals)] if vals else None

    return {
        "n_orders": n_orders,
        "tie_at_k_boundary": ties,
        "n_held_out_predictions": int(len(tr) + len(te)),
        "hit_at_1_any": span("hit_at_1_any"),
        "hit_at_3_any": span("hit_at_3_any"),
        "mrr": span("mrr"),
        "far_at_3": span("far_at_3"),
    }


# ---------------------------------------------------------------------------
# Dataset Evaluator
# ---------------------------------------------------------------------------

def evaluate_dataset_differential(
    csv_path: str,
    dataset_label: str,
    split: str = None,
    tier: str = None,
    onto=None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Evaluates top-k differential diagnosis for all systems across a dataset."""
    cases = evaluate.load_data(csv_path, split=split, tier=tier)
    if verbose:
        print(f"\nEvaluating Top-k Differential on {dataset_label} (n={len(cases)})...")

    # 1. RiceKG Full Proposed (Defined classes + ranking)
    rk_ranked: List[List[str]] = []
    for c in cases:
        top_cands = model.predict_top_k(c["symptoms"], k=3, onto=onto, include_possible=True)
        rk_ranked.append([cand["threat"] for cand in top_cands])

    # 2. Rule: Nearest Prototype
    proto_ranked: List[List[str]] = []
    for c in cases:
        proto_ranked.append(rank_nearest_prototype(c["symptoms"], k=3))

    # 3. Rule: Flat Single-Tier (unranked; reported as top-1 only per Part 7-C)
    flat_onto = rule_baselines.get_flat_ontology()
    flat_ranked: List[List[str]] = []
    for c in cases:
        flat_preds = rule_baselines.predict_flat_rules(c["symptoms"], onto=flat_onto)
        # Flat unranked rules return at most 1 item or unranked firing
        flat_ranked.append(flat_preds[:1])

    # 4. Supervised ML Classifiers
    # Feature matrices
    X = np.zeros((len(cases), len(ml_baselines.SYMPTOM_ORDER)), dtype=int)
    Y = np.zeros((len(cases), len(ALL_THREATS)), dtype=int)
    for i, c in enumerate(cases):
        X[i] = ml_baselines.encode_symptoms(c["symptoms"])
        Y[i] = ml_baselines.encode_labels(c.get("raw_target", ""))

    # ML models evaluated via leave-one-out or 2-fold CV depending on sample size
    ml_models = ml_baselines.get_ml_models()
    ml_ranked: Dict[str, List[List[str]]] = {m_name: [[] for _ in cases] for m_name in ml_models}

    n_samples = len(cases)
    n_splits = 2 if n_samples >= 10 else 1
    tie_sensitivity = None

    if n_splits > 1:
        splits = ml_baselines.get_5x2_splits(X, Y, random_state=42)
        # Use first split pair for clean point-ranking evaluation
        sp = splits[0]
        train_idx, test_idx = sp["train_indices"], sp["test_indices"]

        for m_name, clf in ml_models.items():
            for tr_idx, te_idx in [(train_idx, test_idx), (test_idx, train_idx)]:
                try:
                    clf.fit(X[tr_idx], Y[tr_idx])
                    if hasattr(clf, "predict_proba"):
                        probs = clf.predict_proba(X[te_idx])
                        if isinstance(probs, list):  # OneVsRestClassifier list of 2-col arrays
                            prob_matrix = np.column_stack([p[:, 1] if p.shape[1] > 1 else p[:, 0] for p in probs])
                        else:
                            prob_matrix = probs
                    else:
                        prob_matrix = clf.predict(X[te_idx])

                    for local_i, global_i in enumerate(te_idx):
                        ml_ranked[m_name][global_i] = rank_ml_predictions(prob_matrix[local_i], k=3)
                except Exception:
                    pass

        tie_sensitivity = knn_tie_sensitivity(X, Y, cases, train_idx, test_idx)
    else:
        # Train on full set if < 10 cases
        for m_name, clf in ml_models.items():
            try:
                clf.fit(X, Y)
                probs = clf.predict_proba(X)
                if isinstance(probs, list):
                    prob_matrix = np.column_stack([p[:, 1] if p.shape[1] > 1 else p[:, 0] for p in probs])
                else:
                    prob_matrix = probs
                for i in range(n_samples):
                    ml_ranked[m_name][i] = rank_ml_predictions(prob_matrix[i], k=3)
            except Exception:
                pass

    # Compute metrics for each system
    system_metrics = {}
    system_metrics["RiceKG (Full Proposed)"] = compute_top_k_metrics_for_system(
        cases, rk_ranked, "RiceKG (Full Proposed)"
    )
    system_metrics["Rule: Nearest Prototype"] = compute_top_k_metrics_for_system(
        cases, proto_ranked, "Rule: Nearest Prototype"
    )
    system_metrics["Rule: Flat Single-Tier"] = compute_top_k_metrics_for_system(
        cases, flat_ranked, "Rule: Flat Single-Tier (Top-1 Only)"
    )

    for m_name in ml_models:
        system_metrics[m_name] = compute_top_k_metrics_for_system(
            cases, ml_ranked[m_name], m_name
        )

    return {
        "dataset": dataset_label,
        "csv_path": os.path.relpath(csv_path, BASE_DIR).replace(os.sep, "/"),
        "split": split,
        "n_cases": len(cases),
        "systems": system_metrics,
        "knn_tie_sensitivity": tie_sensitivity,
    }


# ---------------------------------------------------------------------------
# Report Formatting
# ---------------------------------------------------------------------------

RULE_SYSTEMS = ("RiceKG (Full Proposed)", "Rule: Nearest Prototype", "Rule: Flat Single-Tier")


def _pct(value) -> str:
    return "n/a" if value is None else f"{value:.1f}%"


def _key_findings(all_evals: List[Dict[str, Any]]) -> List[str]:
    """Derive the findings from the eval-split metrics; no figure is typed by hand."""
    ev = next((e for e in all_evals if e.get("split") == "eval"), None)
    if ev is None:
        return ["No `eval` split was evaluated."]
    s = ev["systems"]
    rk, proto, flat = s["RiceKG (Full Proposed)"], s["Rule: Nearest Prototype"], s["Rule: Flat Single-Tier"]
    ml = [m for name, m in s.items() if name not in RULE_SYSTEMS]
    n_pos, n_neg = rk["n_positive"], rk["n_negative"]

    findings = [
        f"1. **Top-k raises hits and false alarms together.** On the field `eval` split ({n_pos} positives, "
        f"{n_neg} negative controls), RiceKG moves from Hit@1 = {_pct(rk['hit_at_1_any'])} to Hit@3 = "
        f"{_pct(rk['hit_at_3_any'])} (MRR {rk['mrr']:.3f}), with a negative-control false-alarm rate of "
        f"{_pct(rk['far_at_3'])} at k=3 (specificity {_pct(rk['specificity_at_3'])}). The additional candidates are "
        f"`possible`-grade threats, which are also raised on negative controls, so the list is a screening aid "
        f"rather than a diagnosis. The set-based rules without partial evidence (Flat Single-Tier) stay at "
        f"Hit@3 = {_pct(flat['hit_at_3_any'])} with FAR@3 = {_pct(flat['far_at_3'])}.",
        f"2. **Nearest Prototype** reaches Hit@3 = {_pct(proto['hit_at_3_any'])} with FAR@3 = {_pct(proto['far_at_3'])}.",
    ]
    if ml:
        hits = [m["hit_at_3_any"] for m in ml]
        fars = [m["far_at_3"] for m in ml if m["far_at_3"] is not None]
        findings.append(
            f"3. **Supervised baselines** ({len(ml)} models, trained on one 2-fold split of the same field cases) "
            f"range over Hit@3 = {min(hits):.1f}–{max(hits):.1f}% and FAR@3 = "
            + (f"{min(fars):.1f}–{max(fars):.1f}%." if fars else "n/a.")
        )
    if n_pos:
        findings.append(
            f"{len(findings) + 1}. **Resolution.** With {n_pos} positives, one case moves Hit@k by "
            f"{100.0 / n_pos:.1f} points; none of the differences above is statistically established."
        )
    return findings


def format_markdown_report(all_evals: List[Dict[str, Any]], output_md: str) -> None:
    """Formats top-k differential evaluation findings into Markdown."""
    lines = [
        "# Top-k Differential Diagnosis & Ranking Analysis (PART 7)",
        "",
        f"> **Generated**: {datetime.now(timezone.utc).isoformat()}  ",
        "> **Evaluation Protocol**: Pre-fixed deterministic ordering key (Part 7-A), fair comparative baselines (Part 7-C), secondary diagnostic utility analysis.",
        "",
        "---",
        "",
        "## 1. Experimental Overview & Agronomic Purpose",
        "",
        "In field pathology, scouting reports often document partial symptom combinations that do not satisfy",
        "strict canonical pathognomonic thresholds. The **Top-k Differential Diagnosis** surfaces a prioritized",
        "list of diagnostic hypotheses ranked strictly by evidence strength:",
        "",
        "1. **Pre-fixed Ordering Key**: Grade ordinal (`confirmed` > `suspected` > `possible` > `weak`) → `antecedent_coverage` desc → `confidence` desc → `threat` name alphabetical asc.",
        "2. **Safety & Specificity Safeguard**: Top-k naturally inflates sensitivity by construction. Therefore, every **Hit@k** figure is presented alongside its corresponding **Negative-Control False Alarm Rate (FAR@k)**.",
        "",
        "---",
    ]

    for ev in all_evals:
        d_name = ev["dataset"]
        systems = ev["systems"]
        n_pos = next(iter(systems.values()))["n_positive"]
        n_neg = next(iter(systems.values()))["n_negative"]

        lines.extend([
            f"## 2. Dataset: {d_name} ($n={ev['n_cases']}$, {n_pos} positives, {n_neg} negative controls)",
            "",
            "| System / Architecture | Hit@1 (%) | Hit@2 (%) | Hit@3 (%) | MRR | FAR@1 (%) | FAR@3 (%) | Spec@3 (%) | Mean Length |",
            "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
        ])

        for s_name, m in systems.items():
            lines.append(
                f"| **{s_name}** | {_pct(m['hit_at_1_any'])} | {_pct(m['hit_at_2_any'])} | {_pct(m['hit_at_3_any'])} "
                f"| {m['mrr']:.3f} | {_pct(m['far_at_1'])} | {_pct(m['far_at_3'])} | {_pct(m['specificity_at_3'])} "
                f"| {m['mean_list_length']:.2f} |"
            )

        if n_neg == 0:
            lines.extend(["", "_No negative controls in this split: false-alarm rate and specificity are undefined (n/a)._"])

        ts = ev.get("knn_tie_sensitivity")
        if ts:
            span = lambda key: "n/a" if ts[key] is None else f"{ts[key][0]:.1f}–{ts[key][1]:.1f}%"
            lines.extend([
                "",
                f"_k-NN tie sensitivity: {ts['tie_at_k_boundary']} of {ts['n_held_out_predictions']} held-out "
                f"predictions have a distance tie at the 3rd-neighbour boundary. Over {ts['n_orders']} "
                f"training-row orders, k-NN spans Hit@1 {span('hit_at_1_any')}, Hit@3 {span('hit_at_3_any')} "
                f"and FAR@3 {span('far_at_3')}. The table row uses `algorithm=\"brute\"` with the original row "
                f"order; k-NN figures are not comparable with other systems more finely than this span._",
            ])
        lines.extend(["", "---", ""])

    lines.extend(["## 3. Key Findings", ""])
    lines.extend(_key_findings(all_evals))
    lines.append("")

    with open(output_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Run top-k differential diagnosis evaluation.")
    parser.add_argument("--output-json", default=os.path.join(RESULTS_DIR, "top_k.json"))
    parser.add_argument("--output-md", default=os.path.join(RESULTS_DIR, "top_k.md"))
    args = parser.parse_args()

    onto = model.build_ontology()

    field_csv = os.path.join(BASE_DIR, "data", "benchmark_field.csv")
    synth_csv = os.path.join(BASE_DIR, "data", "verification_suite.csv")

    evaluations = []

    # 1. Field dev split
    evaluations.append(
        evaluate_dataset_differential(field_csv, "Field Benchmark (Dev Split)", split="dev", onto=onto)
    )

    # 2. Field eval split (held-out)
    evaluations.append(
        evaluate_dataset_differential(field_csv, "Field Benchmark (Eval Split, Held-Out)", split="eval", onto=onto)
    )

    # 3. Field holdout split (evidence tiers A, B and C)
    evaluations.append(
        evaluate_dataset_differential(field_csv, "Field Benchmark (Holdout Split, Tiers A-C)", split="holdout", onto=onto)
    )

    # 4. Deductive verification suite
    evaluations.append(
        evaluate_dataset_differential(synth_csv, "Deductive Verification Suite", onto=onto)
    )

    # Save outputs
    with open(args.output_json, "w", encoding="utf-8") as fh:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "evaluations": evaluations
        }, fh, indent=2)
    print(f"Saved: {args.output_json}")

    format_markdown_report(evaluations, args.output_md)
    print(f"Saved: {args.output_md}")


if __name__ == "__main__":
    main()
