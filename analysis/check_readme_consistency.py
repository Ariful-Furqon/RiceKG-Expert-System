"""
Fail if a headline metric quoted in the documentation has drifted from `results/`.

Every figure reported in `README.md` and `docs/` must be regenerable by a script in this
repository and traceable to a results file. Twice during the P0-4 revision the prose went
stale while the underlying measurements changed — once claiming 0/5 positive-case recall
after the measured value had become 20.83%. This check makes that failure mode a CI error
rather than something a reader has to catch.

Usage:  python analysis/check_readme_consistency.py
Exit:   0 if every required figure is present, 1 otherwise.
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINES_JSON = os.path.join(BASE_DIR, "results", "baselines.json")
ABLATION_JSON = os.path.join(BASE_DIR, "results", "ablation.json")
LEARNING_CURVE_JSON = os.path.join(BASE_DIR, "results", "learning_curve.json")
README = os.path.join(BASE_DIR, "README.md")
LIMITATIONS = os.path.join(BASE_DIR, "docs", "LIMITATIONS.md")
POSITIONING = os.path.join(BASE_DIR, "docs", "POSITIONING.md")


def required_figures():
    """Build the (label, rendered value, documents that must quote it) checklist."""
    with open(BASELINES_JSON, encoding="utf-8") as fh:
        base = json.load(fh)
    with open(ABLATION_JSON, encoding="utf-8") as fh:
        abl = json.load(fh)

    field = base["field_benchmark"]
    rk_field = field["system_summaries"]["RiceKG (Full Proposed)"]
    # Support synthetic_benchmark key with fallback to augmented_benchmark
    synth = base.get("synthetic_benchmark", base.get("augmented_benchmark"))
    aug = synth["system_summaries"]["RiceKG (Full Proposed)"]
    full = next(r for r in abl["results"] if r["variant"] == "full")

    checks = [
        ("field positive-case recall", f"{rk_field['mean_positive_recall']:.2f}",
         [README, LIMITATIONS, POSITIONING]),
        ("field micro-F1", f"{rk_field['mean_micro_f1']:.2f}",
         [README, LIMITATIONS, POSITIONING]),
        ("field micro-F1 CI lower", f"{rk_field['micro_f1_ci_95'][0]:.1f}",
         [README, LIMITATIONS, POSITIONING]),
        ("field micro-F1 CI upper", f"{rk_field['micro_f1_ci_95'][1]:.1f}",
         [README, LIMITATIONS, POSITIONING]),
        ("field aggregate exact match", f"{rk_field['mean_exact_match']:.2f}",
         [README, LIMITATIONS, POSITIONING]),
        ("field positive case count", str(field["n_positive"]),
         [README, LIMITATIONS]),
        ("field negative control count", str(field["n_negative"]),
         [README, LIMITATIONS]),
        ("synthetic exact match", f"{aug['mean_exact_match']:.2f}",
         [README]),
        ("ablation multi-label accuracy", f"{full['multi_acc']:.2f}",
         [README]),
    ]
    return checks


def scan_for_stale_metrics(text: str, filename: str) -> list:
    """Detects stale pre-P0-5 figures quoted as current RiceKG performance."""
    failures = []
    import re
    # 1. Stale claim of 92.50% exact match outperforming baselines
    if re.search(r"RiceKG achieves \*\*?92\.50?%", text, re.IGNORECASE) or re.search(r"RiceKG achieves 92\.50?%", text, re.IGNORECASE):
        failures.append(f"  {filename}: quotes obsolete pre-P0-5 claim 'RiceKG achieves 92.50% exact match'")

    # 2. Stale ablation table row: Full variant at 92.50% / 96.2%
    if re.search(r"RiceKG Full.*\|\s*\*\*?92\.50?%\*\*?\s*\|", text):
        failures.append(f"  {filename}: ablation table contains stale 92.50% exact match for RiceKG Full")

    if re.search(r"RiceKG Full.*\|\s*\*\*?96\.2%\*\*?\s*\|", text):
        failures.append(f"  {filename}: ablation table contains stale 96.2% micro-F1 for RiceKG Full")

    # 3. Stale ceiling claim
    if "99.25% multi-label accuracy, 92.50% exact-match" in text and "guarantees" in text:
        failures.append(f"  {filename}: quotes obsolete pre-P0-5 ceiling claim")

    return failures


def main():
    for path in (BASELINES_JSON, ABLATION_JSON):
        if not os.path.exists(path):
            print(f"FAIL: missing {os.path.relpath(path, BASE_DIR)}; run `make baselines` and `make ablate`")
            return 1

    contents = {}
    failures = []

    for label, value, docs in required_figures():
        for doc in docs:
            if doc not in contents:
                with open(doc, encoding="utf-8") as fh:
                    contents[doc] = fh.read()
            rel = os.path.relpath(doc, BASE_DIR)
            if value not in contents[doc]:
                failures.append(f"  {rel}: {label} = {value} is not quoted")
            else:
                print(f"  OK  {rel}: {label} = {value}")

    # Check for stale claims across docs
    for doc, text in contents.items():
        rel = os.path.relpath(doc, BASE_DIR)
        stale_errs = scan_for_stale_metrics(text, rel)
        if stale_errs:
            failures.extend(stale_errs)

    if failures:
        print("\nFAIL: documentation has drifted from results/\n")
        print("\n".join(failures))
        print("\nRegenerate with `make baselines && make ablate && make failure-analysis`, "
              "then update the prose to match.")
        return 1

    print("\nOK: every checked figure is traceable to results/ and no stale metrics detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
