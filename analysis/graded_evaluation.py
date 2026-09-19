import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scipy.stats import beta, binomtest

from ricekg import model, evaluate
from baselines import rule_baselines

RESULTS_DIR = os.path.join(BASE_DIR, "results")
SPLITS = ["dev", "eval", "holdout"]
COMMITTED = {"confirmed", "suspected", "committed"}
POSITIVE_OUTCOMES = ["correct", "misfire", "possible_hit", "possible_miss", "rejected", "abstain"]
CONTROL_OUTCOMES = ["false_alarm", "possible_alarm", "explicit_rejection", "silent_abstention"]


def clopper_pearson(k, n, alpha=0.05):
    # Exact two-sided binomial confidence interval, in percent.
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return [round(100 * lo, 1), round(100 * hi, 1)]


def rate(k, n):
    return {"k": k, "n": n, "pct": round(100 * k / n, 2) if n else None, "ci95": clopper_pearson(k, n)}


def classify(outputs, truth):
    # outputs: list of (threat, grade); truth: set of true threats (empty for controls).
    committed = {t for t, g in outputs if g in COMMITTED}
    possible = {t for t, g in outputs if g == "possible"}
    rejected = any(g == "out_of_scope" for _, g in outputs)
    if truth:
        if truth <= committed:
            return "correct"
        if committed:
            return "misfire"
        if truth & possible:
            return "possible_hit"
        if possible:
            return "possible_miss"
        return "rejected" if rejected else "abstain"
    if committed:
        return "false_alarm"
    if possible:
        return "possible_alarm"
    return "explicit_rejection" if rejected else "silent_abstention"


# -------------------------------------------------------------------------
# Systems: each maps a symptom list to [(threat, grade), ...]
# -------------------------------------------------------------------------

def ricekg_outputs(symptoms):
    res = model.predict_diseases(symptoms, include_possible=True)
    return [(r["threat"], r["grade"]) for r in res]


def ricekg_strict(outputs):
    return [(t, g) for t, g in outputs if g != "possible"]


def prototype_outputs(symptoms):
    return [(t, "committed") for t in rule_baselines.predict_nearest_prototype(symptoms)]


def flat_outputs(symptoms):
    return [(t, "committed") for t in rule_baselines.predict_flat_rules(symptoms)]


def summarize(case_rows, system):
    pos = [c for c in case_rows if c["truth"]]
    ctl = [c for c in case_rows if not c["truth"]]
    po = Counter(c["outcome"][system] for c in pos)
    co = Counter(c["outcome"][system] for c in ctl)

    # Precision of committed assertions, pooled over every case, and per grade.
    graded = Counter()
    graded_true = Counter()
    for c in case_rows:
        for t, g in c["outputs"][system]:
            if g == "out_of_scope":
                continue
            graded[g] += 1
            graded_true[g] += int(t in c["truth"])
    committed_n = sum(graded[g] for g in COMMITTED)
    committed_true = sum(graded_true[g] for g in COMMITTED)

    return {
        "n_positive": len(pos),
        "n_control": len(ctl),
        "positive_outcomes": {k: po.get(k, 0) for k in POSITIVE_OUTCOMES},
        "control_outcomes": {k: co.get(k, 0) for k in CONTROL_OUTCOMES},
        "committed_recall": rate(po["correct"], len(pos)),
        "recall_incl_possible": rate(po["correct"] + po["possible_hit"], len(pos)),
        "misfire_rate": rate(po["misfire"], len(pos)),
        "safe_failure_rate": rate(po["abstain"] + po["rejected"] + po["possible_miss"] + po["possible_hit"], len(pos)),
        "committed_precision": rate(committed_true, committed_n),
        "grade_precision": {g: rate(graded_true[g], graded[g]) for g in ("confirmed", "suspected", "possible", "committed") if graded[g]},
        "false_alarm_rate": rate(co["false_alarm"], len(ctl)),
        "false_alarm_incl_possible": rate(co["false_alarm"] + co["possible_alarm"], len(ctl)),
        "explicit_rejection_rate": rate(co["explicit_rejection"], len(ctl)),
    }


def paired_test(case_rows, a, b):
    # Exact McNemar on per-case success (positive: correct; control: no committed alarm).
    def ok(c, s):
        return c["outcome"][s] == "correct" if c["truth"] else c["outcome"][s] != "false_alarm"
    only_a = sum(1 for c in case_rows if ok(c, a) and not ok(c, b))
    only_b = sum(1 for c in case_rows if ok(c, b) and not ok(c, a))
    n = only_a + only_b
    p = binomtest(only_a, n, 0.5).pvalue if n else 1.0
    return {"only_first_correct": only_a, "only_second_correct": only_b, "exact_mcnemar_p": round(p, 4)}


def run():
    systems = ["RiceKG strict", "RiceKG + possible", "Flat single-tier rules", "Nearest prototype"]
    cases = []
    for split in SPLITS:
        for case in evaluate.load_data(evaluate.FIELD_CSV, split=split):
            syms = case["symptoms"]
            rk = ricekg_outputs(syms)
            outputs = {
                "RiceKG strict": ricekg_strict(rk),
                "RiceKG + possible": rk,
                "Flat single-tier rules": flat_outputs(syms),
                "Nearest prototype": prototype_outputs(syms),
            }
            truth = set(case["expected"])
            cases.append({
                "case_id": case["case_id"], "split": split, "truth": sorted(truth),
                "symptoms": syms, "outputs": outputs,
                "outcome": {s: classify(o, truth) for s, o in outputs.items()},
            })

    for c in cases:
        c["truth"] = set(c["truth"])
    groups = {
        "eval": [c for c in cases if c["split"] == "eval"],
        "dev": [c for c in cases if c["split"] == "dev"],
        "dev+eval": [c for c in cases if c["split"] in ("dev", "eval")],
        "holdout (development-exposed)": [c for c in cases if c["split"] == "holdout"],
    }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "single deterministic run per case; exact Clopper-Pearson 95% intervals; no cross-validation",
        "systems": systems,
        "groups": {g: {s: summarize(rows, s) for s in systems} for g, rows in groups.items()},
        "paired_vs_ricekg_strict": {
            g: {s: paired_test(rows, "RiceKG strict", s) for s in systems[1:]}
            for g, rows in groups.items()
        },
        "cases": [{**c, "truth": sorted(c["truth"])} for c in cases],
    }
    return report


def fmt(r):
    if r["n"] == 0:
        return "—"
    lo, hi = r["ci95"]
    return f"{r['k']}/{r['n']} ({r['pct']:.1f}%) [{lo:.1f}, {hi:.1f}]"


def write_markdown(rep, path):
    L = [
        "# Graded Case-Level Evaluation (Field Benchmark)",
        "",
        f"> **Generated by**: `analysis/graded_evaluation.py` on {rep['generated_at'][:19]} UTC.  ",
        "> **Protocol**: every system runs once on every case; no training and no cross-validation. "
        "Figures are counts over cases with exact Clopper–Pearson 95% intervals.  ",
        "> **Independence**: `eval` is development-informed and `holdout` is development-exposed "
        "(see `docs/LIMITATIONS.md` Section 2); neither is a strictly held-out estimate.",
        "",
        "Outcome categories are defined in the script docstring. *Committed* means graded confirmed or "
        "suspected; a **misfire** names the wrong disease and is the harmful error, while abstaining or "
        "rejecting as out of scope is a safe failure.",
    ]
    for g, per_sys in rep["groups"].items():
        any_sys = next(iter(per_sys.values()))
        L += ["", f"## {g} ({any_sys['n_positive']} positive cases, {any_sys['n_control']} negative controls)", ""]
        L += ["| System | Committed recall | Recall incl. `possible` | Misfire | Committed precision | False alarm (controls) | Explicit rejection (controls) |",
              "|:---|:---:|:---:|:---:|:---:|:---:|:---:|"]
        for s, m in per_sys.items():
            L.append(f"| {s} | {fmt(m['committed_recall'])} | {fmt(m['recall_incl_possible'])} | {fmt(m['misfire_rate'])} | "
                     f"{fmt(m['committed_precision'])} | {fmt(m['false_alarm_rate'])} | {fmt(m['explicit_rejection_rate'])} |")
        L += ["", "Positive-case outcomes:", "",
              "| System | " + " | ".join(POSITIVE_OUTCOMES) + " |", "|:---|" + ":---:|" * len(POSITIVE_OUTCOMES)]
        L += [f"| {s} | " + " | ".join(str(m["positive_outcomes"][k]) for k in POSITIVE_OUTCOMES) + " |" for s, m in per_sys.items()]
        if any_sys["n_control"]:
            L += ["", "Negative-control outcomes:", "",
                  "| System | " + " | ".join(CONTROL_OUTCOMES) + " |", "|:---|" + ":---:|" * len(CONTROL_OUTCOMES)]
            L += [f"| {s} | " + " | ".join(str(m["control_outcomes"][k]) for k in CONTROL_OUTCOMES) + " |" for s, m in per_sys.items()]
        gp = per_sys["RiceKG + possible"]["grade_precision"]
        L += ["", "RiceKG precision by confidence grade (grades are valid if precision falls as the grade weakens): "
              + "; ".join(f"`{k}` {fmt(v)}" for k, v in gp.items()) + "."]
        pt = rep["paired_vs_ricekg_strict"][g]
        L += ["", "Paired exact McNemar against RiceKG strict (per-case success):", "",
              "| Comparator | Only RiceKG strict correct | Only comparator correct | p |", "|:---|:---:|:---:|:---:|"]
        L += [f"| {s} | {t['only_first_correct']} | {t['only_second_correct']} | {t['exact_mcnemar_p']:.4f} |" for s, t in pt.items()]
    L += ["", "## Per-case outcomes", "", "| Case | Split | Truth | RiceKG | RiceKG output |", "|:---|:---|:---|:---|:---|"]
    for c in rep["cases"]:
        out = ", ".join(f"{t} ({g})" for t, g in c["outputs"]["RiceKG + possible"]) or "—"
        L.append(f"| {c['case_id']} | {c['split']} | {', '.join(c['truth']) or 'No_Diagnosis'} | "
                 f"{c['outcome']['RiceKG + possible']} | {out} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    rep = run()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "graded_evaluation.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    write_markdown(rep, os.path.join(RESULTS_DIR, "graded_evaluation.md"))
    print("Written: results/graded_evaluation.json, results/graded_evaluation.md")
