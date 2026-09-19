import argparse
import csv
import itertools
import json
import os
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analysis.agreement import compute_cohens_kappa, compute_fleiss_kappa

DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
GRADED_JSON = os.path.join(RESULTS_DIR, "graded_evaluation.json")
FIELD_CSV = os.path.join(DATA_DIR, "benchmark_field.csv")
N_BOOT = 2000
SEED = 42


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def system_label(outputs):
    # RiceKG strict output -> one categorical label comparable with a rater's answer.
    committed = sorted(t for t, g in outputs if g in ("confirmed", "suspected"))
    if committed:
        return committed[0] if len(committed) == 1 else "Multiple"
    if any(g == "out_of_scope" for _, g in outputs):
        return "Other"
    return "Undetermined"


def truth_label(diagnosis):
    return "Other" if diagnosis == "No_Diagnosis" else diagnosis


def _kappa(a, b):
    return compute_cohens_kappa(a, b, sorted(set(a) | set(b)))[0]


def _boot(n, stat, rng):
    vals = []
    for _ in range(N_BOOT):
        idx = rng.choice(n, size=n, replace=True)
        v = stat(idx)
        if v is not None and not np.isnan(v):
            vals.append(v)
    return [round(float(np.percentile(vals, 2.5)), 3), round(float(np.percentile(vals, 97.5)), 3)] if vals else [None, None]


# ---------------------------------------------------------------------------
# A2: diagnosis
# ---------------------------------------------------------------------------

def diagnosis_agreement(diag_rows, system, truth, rng):
    raters = sorted({r["annotator"] for r in diag_rows})
    answers = defaultdict(dict)
    for r in diag_rows:
        answers[r["case_id"]][r["annotator"]] = r["diagnosis"]
    cases = sorted(c for c, a in answers.items() if all(x in a for x in raters) and c in system)
    R = {r: [answers[c][r] for c in cases] for r in raters}
    S = [system[c] for c in cases]
    T = [truth[c] for c in cases]
    n = len(cases)

    out = {"raters": raters, "n_cases": n}
    if len(raters) >= 2:
        cats = sorted({v for vs in R.values() for v in vs})
        matrix = [[R[r][i] for r in raters] for i in range(n)]
        out["fleiss_kappa"] = round(compute_fleiss_kappa(matrix, cats)[0], 3) if len(raters) >= 3 else None
        pairs = list(itertools.combinations(raters, 2))
        out["pairwise_rater_kappa"] = {f"{a}-{b}": round(_kappa(R[a], R[b]), 3) for a, b in pairs}
        out["system_rater_kappa"] = {r: round(_kappa(S, R[r]), 3) for r in raters}
        mean_rr = statistics.mean(out["pairwise_rater_kappa"].values())
        mean_sr = statistics.mean(out["system_rater_kappa"].values())
        out["mean_rater_rater_kappa"] = round(mean_rr, 3)
        out["mean_system_rater_kappa"] = round(mean_sr, 3)

        def diff(idx):
            rr = statistics.mean(_kappa([R[a][i] for i in idx], [R[b][i] for i in idx]) for a, b in pairs)
            sr = statistics.mean(_kappa([S[i] for i in idx], [R[r][i] for i in idx]) for r in raters)
            return sr - rr

        out["system_minus_rater_kappa"] = round(mean_sr - mean_rr, 3)
        out["system_minus_rater_kappa_ci95"] = _boot(n, diff, rng)
        # A range needs at least two rater pairs (three raters); with two raters the criterion is
        # whether the bootstrap CI of the RiceKG-minus-rater difference includes zero.
        out["system_within_rater_range"] = (
            min(out["pairwise_rater_kappa"].values()) <= mean_sr <= max(out["pairwise_rater_kappa"].values())
            if len(pairs) > 1 else None)

    majority = []
    for i in range(n):
        top = Counter(R[r][i] for r in raters).most_common()
        majority.append(top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else "NoMajority")
    pos = [i for i in range(n) if T[i] != "Other"]

    def acc(labels, idx):
        return {"k": sum(labels[i] == T[i] for i in idx), "n": len(idx)}

    out["vs_published_label"] = {
        who: {"all": acc(labels, range(n)), "positive_cases": acc(labels, pos)}
        for who, labels in [*((r, R[r]) for r in raters), ("rater majority", majority), ("RiceKG strict", S)]
    }
    out["label_distribution"] = {who: dict(Counter(labels)) for who, labels in [*R.items(), ("RiceKG strict", S)]}
    return out


# ---------------------------------------------------------------------------
# A2: symptom encoding
# ---------------------------------------------------------------------------

def encoding_agreement(sym_rows, raters, authors, cases):
    enc = defaultdict(lambda: defaultdict(set))
    for r in sym_rows:
        enc[r["case_id"]][r["annotator"]].add(r["term"])
    cases = [c for c in cases if c in authors]
    used = sorted({t for c in cases for r in raters for t in enc[c][r]})

    per_term = {}
    for term in used:
        matrix = [["1" if term in enc[c][r] else "0" for r in raters] for c in cases]
        if len(raters) >= 3:
            per_term[term] = round(compute_fleiss_kappa(matrix, ["0", "1"])[0], 3)
        else:
            per_term[term] = round(_kappa([m[0] for m in matrix], [m[1] for m in matrix]), 3)

    def jacc(a, b):
        return 1.0 if not a and not b else len(a & b) / len(a | b)

    pair_j = [jacc(enc[c][a], enc[c][b]) for c in cases for a, b in itertools.combinations(raters, 2)]
    majority = {c: {t for t in used if sum(t in enc[c][r] for r in raters) * 2 > len(raters)} for c in cases}
    author_j = [jacc(set(authors[c]), majority[c]) for c in cases]
    return {
        "terms_used": len(used),
        "per_term_kappa": dict(sorted(per_term.items(), key=lambda kv: kv[1])),
        "mean_pairwise_jaccard": round(statistics.mean(pair_j), 3) if pair_j else None,
        "author_vs_majority_jaccard": round(statistics.mean(author_j), 3) if author_j else None,
        "cases_author_equals_majority": sum(set(authors[c]) == majority[c] for c in cases),
        "n_cases": len(cases),
        "majority_encoding": {c: sorted(v) for c, v in majority.items()},
    }


def rerun_on_majority(majority, truth):
    from ricekg import model
    from analysis.graded_evaluation import classify
    outcomes = {}
    for c, syms in majority.items():
        res = model.predict_diseases(syms, include_possible=False)
        t = {truth[c]} if truth[c] != "Other" else set()
        outcomes[c] = classify([(r["threat"], r["grade"]) for r in res], t)
    return dict(Counter(outcomes.values())), outcomes


# ---------------------------------------------------------------------------
# A3: explanations and definitions
# ---------------------------------------------------------------------------

def explanation_ratings(expl_rows, outcome):
    if not expl_rows:
        return None

    def summarize(rows):
        s = {"n": len(rows), "accept": dict(Counter(r["accept"] for r in rows if r["accept"]))}
        for k in ("reasoning", "completeness", "usefulness"):
            vals = [int(r[k]) for r in rows if r[k]]
            s[k] = {"mean": round(statistics.mean(vals), 2), "median": statistics.median(vals), "n": len(vals)} if vals else None
        return s

    # Group by the output the rater actually saw; older imports without that column fall back to
    # the current RiceKG outcome.
    by_outcome = defaultdict(list)
    for r in expl_rows:
        by_outcome[r.get("shown_output") or outcome.get(r["case_id"], "unknown")].append(r)
    return {"overall": summarize(expl_rows), "by_shown_output": {k: summarize(v) for k, v in sorted(by_outcome.items())}}


def definition_review(rows):
    if not rows:
        return None
    # Aggregate only: raters were told their answers would not be reported individually, so the
    # public report counts ratings and flagged terms; the wording of suggestions stays local.
    counts = dict(Counter(r["rating"] for r in rows if r["rating"]))
    flagged = Counter(r["term"] for r in rows
                      if r["rating"] in ("needs_revision", "inadequate") or r["suggestion"])
    return {"counts": counts, "n_reviewers": len({r["annotator"] for r in rows}),
            "flagged_terms": dict(sorted(flagged.items()))}


# ---------------------------------------------------------------------------

def run(data_dir=DATA_DIR, graded_json=GRADED_JSON, rerun=False):
    diag = _read(os.path.join(data_dir, "annotations_diagnosis.csv"))
    if not diag:
        return None
    with open(graded_json, encoding="utf-8") as f:
        graded = json.load(f)
    system = {c["case_id"]: system_label(c["outputs"]["RiceKG strict"]) for c in graded["cases"]}
    outcome = {c["case_id"]: c["outcome"]["RiceKG strict"] for c in graded["cases"]}
    with open(FIELD_CSV, encoding="utf-8-sig", newline="") as f:
        field = list(csv.DictReader(f))
    truth = {r["case_id"]: truth_label(r["diagnosis"]) for r in field}
    authors = {r["case_id"]: [r[f"symptom_{i}"] for i in range(1, 7) if r[f"symptom_{i}"]] for r in field}

    rng = np.random.RandomState(SEED)
    dx = diagnosis_agreement(diag, system, truth, rng)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diagnosis": dx,
        "encoding": None,
        "explanations": explanation_ratings(_read(os.path.join(data_dir, "annotations_explanations.csv")), outcome),
        "explanations_v24": explanation_ratings(_read(os.path.join(data_dir, "annotations_explanations_v24.csv")), outcome),
        "definitions": definition_review(_read(os.path.join(data_dir, "definition_review.csv"))),
    }
    sym = _read(os.path.join(data_dir, "annotations_symptoms.csv"))
    if sym:
        enc = encoding_agreement(sym, dx["raters"], authors, sorted(truth))
        if rerun:
            enc["rerun_on_majority_outcomes"], _ = rerun_on_majority(enc["majority_encoding"], truth)
        report["encoding"] = enc
    return report


def _pct(d):
    return f"{d['k']}/{d['n']}" + (f" ({100 * d['k'] / d['n']:.1f}%)" if d["n"] else "")


def write_markdown(rep, path):
    dx = rep["diagnosis"]
    L = ["# Expert-Based Validation", "",
         f"> **Generated by**: `analysis/expert_validation.py` on {rep['generated_at'][:19]} UTC from the tables written by "
         "`annotation/import_returns.py`. Protocol: `docs/ANNOTATION_PROTOCOL.md`.", "",
         f"## Diagnosis ({dx['n_cases']} cases, raters {', '.join(dx['raters'])})", ""]
    if dx.get("pairwise_rater_kappa"):
        L += ["| Agreement | Cohen's κ |", "|:---|:---:|"]
        L += [f"| Rater {p} | {k:.3f} |" for p, k in dx["pairwise_rater_kappa"].items()]
        L += [f"| RiceKG – {r} | {k:.3f} |" for r, k in dx["system_rater_kappa"].items()]
        L += ["", f"Fleiss' κ across raters: {dx['fleiss_kappa'] if dx['fleiss_kappa'] is not None else 'n/a (fewer than 3 raters)'}. "
              f"Mean rater–rater κ {dx['mean_rater_rater_kappa']:.3f}; mean RiceKG–rater κ {dx['mean_system_rater_kappa']:.3f}; "
              f"difference {dx['system_minus_rater_kappa']:+.3f} [95% CI {dx['system_minus_rater_kappa_ci95'][0]}, "
              f"{dx['system_minus_rater_kappa_ci95'][1]}]. "
              + ("RiceKG within the rater–rater range: " + f"**{'yes' if dx['system_within_rater_range'] else 'no'}**."
                 if dx["system_within_rater_range"] is not None
                 else "With two raters there is no rater–rater range; the criterion is whether the interval includes zero.")]
    L += ["", "Agreement with the published label (No_Diagnosis counted as Other):", "",
          "| Who | All cases | Positive cases |", "|:---|:---:|:---:|"]
    L += [f"| {who} | {_pct(v['all'])} | {_pct(v['positive_cases'])} |" for who, v in dx["vs_published_label"].items()]
    enc = rep["encoding"]
    if enc:
        L += ["", f"## Symptom encoding ({enc['n_cases']} cases, {enc['terms_used']} terms used)", "",
              f"Mean pairwise Jaccard between raters: {enc['mean_pairwise_jaccard']}. Authors' encoding vs rater majority: "
              f"mean Jaccard {enc['author_vs_majority_jaccard']}, identical in {enc['cases_author_equals_majority']}/{enc['n_cases']} cases.", "",
              "| Term | κ (presence) |", "|:---|:---:|"]
        L += [f"| `{t}` | {k:.3f} |" for t, k in enc["per_term_kappa"].items()]
        if "rerun_on_majority_outcomes" in enc:
            L += ["", f"RiceKG re-run on the rater-majority encoding, outcomes: {enc['rerun_on_majority_outcomes']}."]
    for key, title in (("explanations", "Explanation ratings, first round (RiceKG v2.3 outputs, authors' encoding)"),
                       ("explanations_v24", "Explanation ratings, re-rating (ruleset v2.4.0, expert-consensus encoding)")):
        ex = rep.get(key)
        if not ex:
            continue
        L += ["", f"## {title}", "",
              "Grouped by the output the rater saw (committed diagnosis, `possible` only, out-of-scope rejection, no output).", "",
              "| Output shown | n | Acceptable (yes/partly/no) | Reasoning | Completeness | Usefulness |",
              "|:---|:---:|:---:|:---:|:---:|:---:|"]
        for name, s in [("all", ex["overall"]), *ex["by_shown_output"].items()]:
            a = s["accept"]
            fmt = lambda x: f"{x['mean']:.2f}" if x else "—"
            L.append(f"| {name} | {s['n']} | {a.get('yes', 0)}/{a.get('partly', 0)}/{a.get('no', 0)} | "
                     f"{fmt(s['reasoning'])} | {fmt(s['completeness'])} | {fmt(s['usefulness'])} |")
    dfn = rep["definitions"]
    if dfn:
        L += ["", "## Definition review", "",
              f"Reviewers: {dfn['n_reviewers']}. Ratings: {dfn['counts']}. Terms flagged for revision "
              f"(number of reviewers): " + ", ".join(f"`{t}` ({n})" for t, n in dfn["flagged_terms"].items()) + "."]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Expert-based validation of RiceKG from the imported rater tables.")
    ap.add_argument("--data-dir", default=DATA_DIR)
    ap.add_argument("--rerun", action="store_true", help="Re-run RiceKG on the rater-majority encoding (Pellet).")
    args = ap.parse_args()
    rep = run(args.data_dir, rerun=args.rerun)
    if rep is None:
        print("[NOTICE] No annotation data in data/annotations_diagnosis.csv yet. "
              "Nothing is computed until raters' workbooks are imported (annotation/import_returns.py).")
        sys.exit(0)
    with open(os.path.join(RESULTS_DIR, "expert_validation.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    write_markdown(rep, os.path.join(RESULTS_DIR, "expert_validation.md"))
    print("Written: results/expert_validation.json, results/expert_validation.md")
