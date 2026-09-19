import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
BASELINES_JSON = os.path.join(BASE_DIR, "results", "baselines.json")
ABLATION_JSON = os.path.join(BASE_DIR, "results", "ablation.json")
GRADED_JSON = os.path.join(BASE_DIR, "results", "graded_evaluation.json")
LEARNING_CURVE_JSON = os.path.join(BASE_DIR, "results", "learning_curve.json")
README = os.path.join(BASE_DIR, "README.md")
LIMITATIONS = os.path.join(BASE_DIR, "docs", "LIMITATIONS.md")
POSITIONING = os.path.join(BASE_DIR, "docs", "POSITIONING.md")


def required_figures():
    # Build the (label, rendered value, documents that must quote it) checklist.
    with open(BASELINES_JSON, encoding="utf-8") as fh:
        base = json.load(fh)
    with open(ABLATION_JSON, encoding="utf-8") as fh:
        abl = json.load(fh)

    field = base["field_benchmark"]
    rk_field = field["system_summaries"]["RiceKG (Full Proposed)"]
    # Support verification_suite key, falling back to the historical names
    synth = base.get("verification_suite",
                    base.get("synthetic_benchmark",
                             base.get("augmented_benchmark")))

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
    ]
    de = abl["field"]["groups"]["dev+eval"]["summary"]
    eq = abl["reasoner_equivalence"]
    checks += [
        ("ablation reasoner equivalence", f"{eq['identical_graded_output']}/{eq['n_cases']}", [README]),
        ("ablation dev+eval recall without diagnostic-sign rules",
         f"{de['no_diagnostic_signs']['committed_recall']['k']}/{de['no_diagnostic_signs']['committed_recall']['n']}",
         [README]),
    ]
    checks += graded_figures()
    return checks


def graded_figures():
    # Headline single-run figures from results/graded_evaluation.json.
    with open(GRADED_JSON, encoding="utf-8") as fh:
        graded = json.load(fh)["groups"]

    def count(r):
        return f"{r['k']}/{r['n']}"

    def ci(r):
        return f"[{r['ci95'][0]:.1f}, {r['ci95'][1]:.1f}]"

    checks = []
    for group, label in (("eval", "eval"), ("dev+eval", "dev+eval")):
        strict = graded[group]["RiceKG strict"]
        loose = graded[group]["RiceKG + possible"]
        alarms = loose["control_outcomes"]["possible_alarm"]
        checks += [
            (f"{label} committed recall", count(strict["committed_recall"]), [README]),
            (f"{label} committed recall CI", ci(strict["committed_recall"]), [README]),
            (f"{label} recall incl. possible", count(loose["recall_incl_possible"]), [README]),
            (f"{label} recall incl. possible CI", ci(loose["recall_incl_possible"]), [README]),
            (f"{label} misfire", count(strict["misfire_rate"]), [README]),
            (f"{label} false-alarm CI", ci(strict["false_alarm_rate"]), [README]),
            (f"{label} possible-grade alarms", f"{alarms}/{loose['n_control']}", [README]),
        ]
    ev = graded["eval"]["RiceKG strict"]
    checks.append(("eval committed recall", f"**{count(ev['committed_recall'])}**", [POSITIONING]))
    return checks


def scan_for_stale_metrics(text: str, filename: str) -> list:
    # Detects stale pre-P0-5 figures quoted as current RiceKG performance.
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

    # 4. Pre-Part-5 scope claims: the system no longer diagnoses insect pests
    for pattern in STALE_SCOPE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            failures.append(f"  {filename}: quotes pre-Part-5 scope claim matching /{pattern}/")

    return failures


STALE_SCOPE_PATTERNS = [
    r"Four Threat Classes Have No Field Case",
    r"10 major biotic threats",
    r"5 pests and 5 diseases",
    r"Rice Pest (and|&) Disease Diagnosis",
]



def negative_control_false_positives() -> tuple[int, int]:
    # Read (false positives, negative controls) from the generated failure analysis.
    import re
    from analysis import report
    text = report.read_section("field-failure-analysis")
    m = re.search(r"(\d+) of (\d+) negative controls produced a false positive", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"None of the (\d+) out-of-scope negative controls produced a false positive", text)
    if m:
        return 0, int(m.group(1))
    raise ValueError("results/REPORT.md#field-failure-analysis has no negative-control summary line")


def check_false_positive_claim(readme_text: str) -> list[str]:
    # README's 'False alarm on negative controls' row must match the failure analysis
    # (dev + eval controls, quoted as '**k of n**').
    import re
    fp, n = negative_control_false_positives()
    m = re.search(r"False alarm on negative controls\*\*\s*\|.*?\*\*(\d+) of (\d+)\*\*", readme_text)
    if not m:
        return ["  README.md: 'False alarm on negative controls' row not found"]
    if (int(m.group(1)), int(m.group(2))) != (fp, n):
        return [f"  README.md: quotes {m.group(1)} of {m.group(2)} negative-control false positives; "
                f"results/REPORT.md#field-failure-analysis reports {fp} of {n}"]
    return []


_GENERATED_MARKER = "<!-- GENERATED FILE — DO NOT EDIT BY HAND -->"


def check_results_index() -> list[str]:
    # Fail if the results-index section of results/REPORT.md is missing or was hand-edited.
    from analysis import report
    errs = []
    section = report.read_section("results-index")
    if not section:
        errs.append(
            "  results/REPORT.md has no results-index section; run `python analysis/build_results_index.py`"
        )
        return errs
    content = section + "\n"
    if _GENERATED_MARKER not in content.splitlines()[0]:
        errs.append(
            "  the results index does not contain the generated-file header on line 1; "
            "it may have been hand-edited or regenerated incorrectly. "
            "Run `python analysis/build_results_index.py` to regenerate."
        )
        return errs
    # The header carries a sha256 over the rest of the file, so any hand edit
    # anywhere in the document is detected, not just removal of the header.
    sys.path.insert(0, os.path.join(BASE_DIR, "analysis"))
    import build_results_index

    if not build_results_index.verify_hash(content):
        errs.append(
            "  the results index content does not match its embedded content-sha256; "
            "it was hand-edited or is stale. "
            "Run `python analysis/build_results_index.py` to regenerate."
        )
    return errs


def main():
    for path in (BASELINES_JSON, ABLATION_JSON, GRADED_JSON):
        if not os.path.exists(path):
            print(f"FAIL: missing {os.path.relpath(path, BASE_DIR)}; run `make baselines` and `make ablate`")
            return 1

    contents = {}
    failures = []

    for label, value, docs in required_figures():
        for doc in docs:
            if not os.path.exists(doc):
                continue  # docs/ is local only (git-ignored); README is always checked
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

    fp_errs = check_false_positive_claim(contents[README])
    if fp_errs:
        failures.extend(fp_errs)
    else:
        print("  OK  README.md: negative-control false positives match field failure analysis")

    # Check RESULTS_INDEX freshness
    index_errs = check_results_index()
    if index_errs:
        failures.extend(index_errs)
    else:
        print("  OK  results/REPORT.md#results-index: generated and unedited")

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
