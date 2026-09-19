import csv
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analysis import report
from ricekg import model, evaluate
from analysis import graded_evaluation as ge

RESULTS_DIR = os.path.join(BASE_DIR, "results")
VERIFICATION_CSV = os.path.join(BASE_DIR, "data", "verification_suite.csv")
FIELD_GROUPS = {
    "eval": ["eval"],
    "dev+eval": ["dev", "eval"],
    "holdout (development-exposed)": ["holdout"],
}
OCCLUSION_SWEEP = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
N_CASES = 500
N_SEEDS = 20
BASE_SEED = 42

VARIANTS = {
    "full": ("RiceKG v2.4.0 (full)", lambda r: True, True),
    "no_diagnostic_signs": ("Without diagnostic-sign rules (R21–R26)",
                            lambda r: r.get("form") != "diagnostic_sign", True),
    "tier1_only": ("Tier-1 rules only", lambda r: r["tier"] == "tier1", True),
    "no_scope_gates": ("Without out-of-scope gates", lambda r: True, False),
}


# -------------------------------------------------------------------------
# Set-matching implementation of the graded reasoner
# -------------------------------------------------------------------------

def predict_set_matching(symptoms, rules=None, gates=True, include_possible=True):
    # Graded output [(threat, grade)] of `rules` by set containment, mirroring
    # model.predict_diseases: confirmed (Tier 1), suspected (any Tier-2 rule), then the
    # out-of-scope gates, then `possible` (primary composite Tier-2 rule coverage).
    rules = model.RULE_REGISTRY if rules is None else rules
    s = {str(x).strip() for x in symptoms if str(x).strip()}
    confirmed = {r["threat"] for r in rules if r["tier"] == "tier1" and set(r["antecedents"]) <= s}
    suspected = {r["threat"] for r in rules if r["tier"] == "tier2" and set(r["antecedents"]) <= s} - confirmed
    out = [(t, "confirmed") for t in sorted(confirmed)] + [(t, "suspected") for t in sorted(suspected)]
    if not out and gates:
        if model.insect_damage_evidence(s):
            out = [(model.INSECT_OUT_OF_SCOPE_TARGET, "out_of_scope")]
        elif model.negative_control_evidence(s):
            out = [(model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET, "out_of_scope")]
    if not out and include_possible:
        for t, meta in model.SWRL_RULES_METADATA.items():
            ants = meta.get("tier2", {}).get("antecedents", [])
            matched = [a for a in ants if a in s]
            if ants and matched and len(matched) / len(ants) >= model.POSSIBLE_COVERAGE_THRESHOLD:
                out.append((t, "possible"))
    return out


def predict_no_reasoner(symptoms):
    # Committed threats (flat list) from set matching; kept for tests/test_p0_2_ablation.py.
    return sorted(t for t, g in predict_set_matching(symptoms, include_possible=False)
                  if g in ("confirmed", "suspected"))


def variant_rules(key):
    keep = VARIANTS[key][1]
    return [r for r in model.RULE_REGISTRY if keep(r)]


# -------------------------------------------------------------------------
# A. Reasoner equivalence and latency
# -------------------------------------------------------------------------

def _latency(values):
    v = sorted(values)
    return {"mean_ms": round(float(np.mean(v)), 3),
            "p95_ms": round(v[max(0, int(math.ceil(0.95 * len(v))) - 1)], 3)}


def load_verification_inputs():
    with open(VERIFICATION_CSV, encoding="utf-8", newline="") as f:
        return [[r[f"symptom_{i}"] for i in range(1, 7) if r[f"symptom_{i}"]] for r in csv.DictReader(f)]


def reasoner_equivalence():
    inputs = [("field", c["case_id"], c["symptoms"])
              for c in evaluate.load_data(evaluate.FIELD_CSV)]
    inputs += [("verification_suite", f"VS_{i + 1:02d}", s) for i, s in enumerate(load_verification_inputs())]
    pellet_ms, set_ms, disagreements = [], [], []
    for source, cid, syms in inputs:
        t0 = time.perf_counter()
        pel = {(r["threat"], r["grade"]) for r in model.predict_diseases(syms, include_possible=True)}
        pellet_ms.append((time.perf_counter() - t0) * 1000)
        t0 = time.perf_counter()
        sm = set(predict_set_matching(syms))
        set_ms.append((time.perf_counter() - t0) * 1000)
        if pel != sm:
            disagreements.append({"source": source, "case_id": cid, "pellet": sorted(pel), "set_matching": sorted(sm)})
    return {
        "n_cases": len(inputs),
        "n_field": sum(1 for x in inputs if x[0] == "field"),
        "n_verification_suite": sum(1 for x in inputs if x[0] == "verification_suite"),
        "identical_graded_output": len(inputs) - len(disagreements),
        "disagreements": disagreements,
        "latency": {"pellet": _latency(pellet_ms), "set_matching": _latency(set_ms)},
    }


# -------------------------------------------------------------------------
# B. Rule-component ablation on the field benchmark
# -------------------------------------------------------------------------

def field_ablation():
    rules = {k: variant_rules(k) for k in VARIANTS}
    cases = []
    for split in ("dev", "eval", "holdout"):
        for c in evaluate.load_data(evaluate.FIELD_CSV, split=split):
            truth = set(c["expected"])
            outputs = {}
            for k, (_, _, gates) in VARIANTS.items():
                full_out = predict_set_matching(c["symptoms"], rules[k], gates=gates)
                outputs[k] = full_out
            outcome = {k: ge.classify(ge.ricekg_strict(o), truth) for k, o in outputs.items()}
            outcome.update({f"{k}+possible": ge.classify(o, truth) for k, o in outputs.items()})
            cases.append({"case_id": c["case_id"], "split": split, "truth": truth,
                          "outputs": {**{k: ge.ricekg_strict(o) for k, o in outputs.items()},
                                      **{f"{k}+possible": o for k, o in outputs.items()}},
                          "outcome": outcome})
    groups = {}
    for g, splits in FIELD_GROUPS.items():
        rows = [c for c in cases if c["split"] in splits]
        groups[g] = {
            "summary": {k: ge.summarize(rows, k) for k in VARIANTS},
            "summary_incl_possible": {k: ge.summarize(rows, f"{k}+possible") for k in VARIANTS},
            "paired_vs_full": {k: ge.paired_test(rows, "full", k) for k in VARIANTS if k != "full"},
        }
    changed = [
        {"case_id": c["case_id"], "split": c["split"], "truth": sorted(c["truth"]) or ["No_Diagnosis"],
         **{k: c["outcome"][k] for k in VARIANTS}}
        for c in cases if len({c["outcome"][k] for k in VARIANTS}) > 1
    ]
    return {"groups": groups, "cases_with_differing_outcomes": changed}


# -------------------------------------------------------------------------
# C. Occlusion sweep
# -------------------------------------------------------------------------

def occlusion_ablation(n_cases=N_CASES, n_seeds=N_SEEDS):
    from data.generator import generate_benchmark
    from baselines import ml_baselines

    rules = {k: variant_rules(k) for k in ("full", "no_diagnostic_signs", "tier1_only")}
    out = {k: {} for k in rules}
    for occ in OCCLUSION_SWEEP:
        runs = {k: [] for k in rules}
        for s in range(n_seeds):
            cases = generate_benchmark(n_cases=n_cases, occlusion_rate=occ, distractor_rate=0.10,
                                       coinfection_rate=0.10, out_of_vocab_rate=0.20, seed=BASE_SEED + s)
            Y = np.array([ml_baselines.encode_labels(c["raw_target"]) for c in cases])
            for k, rs in rules.items():
                P = np.array([ml_baselines.encode_labels(
                    [t for t, g in predict_set_matching(c["symptoms"], rs, include_possible=False)
                     if g != "out_of_scope"])
                    for c in cases])
                runs[k].append(ml_baselines.compute_multilabel_metrics(Y, P))
        for k in rules:
            rec = [m["positive_case_recall"] for m in runs[k]]
            prec = [m["micro_precision"] for m in runs[k]]
            out[k][str(occ)] = {"positive_recall_mean": round(float(np.mean(rec)), 2),
                                "positive_recall_std": round(float(np.std(rec, ddof=1)), 2),
                                "micro_precision_mean": round(float(np.mean(prec)), 2)}
    return {"occlusion_sweep": OCCLUSION_SWEEP, "n_cases": n_cases, "n_seeds": n_seeds, "systems": out}


# -------------------------------------------------------------------------
# Report
# -------------------------------------------------------------------------

def run(n_seeds=N_SEEDS):
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ruleset": {"rules": len(model.RULE_REGISTRY),
                    "diagnostic_sign_rules": [r["id"] for r in model.RULE_REGISTRY if r.get("form") == "diagnostic_sign"]},
        "variants": {k: v[0] for k, v in VARIANTS.items()},
        "reasoner_equivalence": reasoner_equivalence(),
        "field": field_ablation(),
        "occlusion": occlusion_ablation(n_seeds=n_seeds),
    }


def _findings(rep):
    eq = rep["reasoner_equivalence"]
    lat = eq["latency"]
    de = rep["field"]["groups"]["dev+eval"]
    full, nods = de["summary"]["full"], de["summary"]["no_diagnostic_signs"]
    t1 = de["summary"]["tier1_only"]
    nog = de["summary"]["no_scope_gates"]
    pt = de["paired_vs_full"]["no_diagnostic_signs"]
    occ = rep["occlusion"]["systems"]
    mid = "0.3"
    L = [
        f"1. **The reasoner does not change any diagnosis.** Pellet and set matching gave identical graded "
        f"output on {eq['identical_graded_output']}/{eq['n_cases']} inputs, at {lat['pellet']['mean_ms']:.0f} ms "
        f"against {lat['set_matching']['mean_ms']:.3f} ms per case. What the DL layer adds is not accuracy but "
        f"what set matching cannot give: Pellet's proof of `ThreatConfirmed ⊑ ThreatSuspect`, the consistency "
        f"check of the rule base, and the property hierarchy behind the derivation trace.",
        f"2. **The diagnostic-sign rules add committed recall without adding errors on field cases.** On dev+eval, "
        f"committed recall is {full['committed_recall']['k']}/{full['committed_recall']['n']} with them and "
        f"{nods['committed_recall']['k']}/{nods['committed_recall']['n']} without; misfires "
        f"{full['misfire_rate']['k']} vs {nods['misfire_rate']['k']}, false alarms "
        f"{full['false_alarm_rate']['k']} vs {nods['false_alarm_rate']['k']} of {full['n_control']} controls "
        f"(exact McNemar p = {pt['exact_mcnemar_p']:.4f}; the sample is too small for significance).",
        f"3. **Tier-1 rules alone diagnose nothing in the field**: committed recall "
        f"{t1['committed_recall']['k']}/{t1['committed_recall']['n']} on dev+eval. No field report lists a full "
        f"canonical sign set, so the tiers grade confidence but Tier 2 does all the diagnosing.",
        f"4. **The out-of-scope gates change how controls fail, not whether they alarm**: explicit rejections "
        f"{full['explicit_rejection_rate']['k']}/{full['n_control']} with the gates and "
        f"{nog['explicit_rejection_rate']['k']}/{nog['n_control']} without; committed false alarms "
        f"{full['false_alarm_rate']['k']} vs {nog['false_alarm_rate']['k']}.",
        f"5. **Under occlusion the diagnostic-sign rules slow the collapse.** Positive recall at occlusion {mid} is "
        f"{occ['full'][mid]['positive_recall_mean']:.1f}% with them and "
        f"{occ['no_diagnostic_signs'][mid]['positive_recall_mean']:.1f}% without "
        f"(0.8: {occ['full']['0.8']['positive_recall_mean']:.1f}% vs "
        f"{occ['no_diagnostic_signs']['0.8']['positive_recall_mean']:.1f}%). The full ruleset's lowest "
        f"micro-precision over the sweep is {min(v['micro_precision_mean'] for v in occ['full'].values()):.1f}%.",
    ]
    return L


def write_markdown(rep):
    eq = rep["reasoner_equivalence"]
    L = [
        "# Ablation of the RiceKG Architecture",
        "",
        f"> **Generated by**: `analysis/ablation.py` on {rep['generated_at'][:19]} UTC.  ",
        "> **Data**: field benchmark (`data/benchmark_field.csv`, expert-consensus encoding) and controlled "
        "occlusion cases from `data/generator.py`. `data/verification_suite.csv` was authored from an earlier "
        "rule base and is used only as input to the equivalence check, never scored.  ",
        "> **Independence**: the ruleset was revised after the field results were seen (`docs/ONTOLOGY.md`, "
        "v2.4.0); no split here is held out for it.",
        "",
        "## Findings (computed from the tables below)",
        "",
    ] + _findings(rep)

    L += ["", "## A. Reasoner equivalence", "",
          f"Pellet (`model.predict_diseases`) against set matching of the same rules, compared on the full graded "
          f"output (threat and grade, including `possible` and out-of-scope responses) for "
          f"{eq['n_field']} field cases and {eq['n_verification_suite']} verification-suite inputs.", "",
          "| | Pellet DL | Set matching |", "|:---|:---:|:---:|",
          f"| Identical graded output | {eq['identical_graded_output']}/{eq['n_cases']} | — |",
          f"| Mean latency per case | {eq['latency']['pellet']['mean_ms']:.1f} ms | {eq['latency']['set_matching']['mean_ms']:.3f} ms |",
          f"| P95 latency per case | {eq['latency']['pellet']['p95_ms']:.1f} ms | {eq['latency']['set_matching']['p95_ms']:.3f} ms |"]
    if eq["disagreements"]:
        L += ["", "Disagreements:", ""] + [f"- {d['case_id']}: Pellet {d['pellet']}, set matching {d['set_matching']}"
                                           for d in eq["disagreements"]]

    L += ["", "## B. Rule components on the field benchmark", "",
          "Graded outcomes as in `results/REPORT.md#graded-evaluation`: *committed* means confirmed or suspected; a "
          "misfire names the wrong disease; counts with exact Clopper–Pearson 95% intervals."]
    for g, d in rep["field"]["groups"].items():
        any_s = d["summary"]["full"]
        L += ["", f"### {g} ({any_s['n_positive']} positive cases, {any_s['n_control']} negative controls)", "",
              "| Variant | Committed recall | Recall incl. `possible` | Misfire | False alarm | Alarm incl. `possible` | Explicit rejection | McNemar p vs full |",
              "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"]
        for k, name in rep["variants"].items():
            s, sp = d["summary"][k], d["summary_incl_possible"][k]
            p = "—" if k == "full" else f"{d['paired_vs_full'][k]['exact_mcnemar_p']:.4f}"
            L.append(f"| {name} | {ge.fmt(s['committed_recall'])} | {ge.fmt(sp['recall_incl_possible'])} | "
                     f"{ge.fmt(s['misfire_rate'])} | {ge.fmt(s['false_alarm_rate'])} | "
                     f"{ge.fmt(sp['false_alarm_incl_possible'])} | {ge.fmt(s['explicit_rejection_rate'])} | {p} |")
    ch = rep["field"]["cases_with_differing_outcomes"]
    L += ["", "Cases whose strict outcome differs between variants:", "",
          "| Case | Split | Truth | " + " | ".join(rep["variants"].values()) + " |",
          "|:---|:---|:---|" + ":---:|" * len(rep["variants"])]
    L += [f"| {c['case_id']} | {c['split']} | {', '.join(c['truth'])} | " + " | ".join(c[k] for k in rep["variants"]) + " |"
          for c in ch]

    occ = rep["occlusion"]
    L += ["", "## C. Rule components under observation occlusion", "",
          f"Positive-case recall (%), mean of {occ['n_seeds']} seeds × {occ['n_cases']} generated cases, same "
          "generator settings as `results/REPORT.md#degradation-curve`. Generated cases derive from the Tier-1 "
          "antecedents, so the 0.0 column is 100% by construction.", "",
          "| Variant | " + " | ".join(str(o) for o in occ["occlusion_sweep"]) + " |",
          "|:---|" + ":---:|" * len(occ["occlusion_sweep"])]
    for k, data in occ["systems"].items():
        L.append(f"| {rep['variants'][k]} | " + " | ".join(
            f"{data[str(o)]['positive_recall_mean']:.1f}" for o in occ["occlusion_sweep"]) + " |")
    L += ["", "Micro-precision (%). A seed in which a variant commits nothing scores 0, which is why "
          "Tier-1-only precision drops at high occlusion.", "", "| Variant | " + " | ".join(str(o) for o in occ["occlusion_sweep"]) + " |",
          "|:---|" + ":---:|" * len(occ["occlusion_sweep"])]
    for k, data in occ["systems"].items():
        L.append(f"| {rep['variants'][k]} | " + " | ".join(
            f"{data[str(o)]['micro_precision_mean']:.1f}" for o in occ["occlusion_sweep"]) + " |")
    report.write_section("ablation", "\n".join(L))


def main():
    rep = run()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    serial = json.loads(json.dumps(rep, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))
    with open(os.path.join(RESULTS_DIR, "ablation.json"), "w", encoding="utf-8") as f:
        json.dump(serial, f, indent=2)
    write_markdown(rep)
    print("Written: results/ablation.json and the \"ablation\" section of results/REPORT.md")


if __name__ == "__main__":
    main()
