#!/usr/bin/env python3
"""
Generate docs/RESULTS_INDEX.md from every file in results/*.json.

THIS FILE IS GENERATED. DO NOT EDIT BY HAND.
Edit analysis/build_results_index.py to change what is indexed.

Usage:
    python analysis/build_results_index.py

The generated file docs/RESULTS_INDEX.md is registered with
analysis/check_readme_consistency.py so a stale index fails the CI build.
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
import textwrap
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
OUTPUT = BASE_DIR / "docs" / "RESULTS_INDEX.md"


# ---------------------------------------------------------------------------
# Extractors — one function per results/*.json file
# ---------------------------------------------------------------------------

def _fmt(value: object, decimals: int = 2) -> str:
    """Format a float/int/str for the table."""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def _ricekg_field(base: dict) -> list[dict]:
    """Rows from field_benchmark.system_summaries['RiceKG (Full Proposed)']."""
    fb = base.get("field_benchmark", {})
    rk = fb.get("system_summaries", {}).get("RiceKG (Full Proposed)", {})
    if not rk:
        return []
    ci = rk.get("micro_f1_ci_95", ["?", "?"])
    return [
        {
            "claim": "RiceKG field positive-case recall",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(rk['mean_positive_recall'])}%",
        },
        {
            "claim": "RiceKG field exact match",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(rk['mean_exact_match'])}%",
        },
        {
            "claim": "RiceKG field micro-F1 [95% CI]",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(rk['mean_micro_f1'])} [{_fmt(ci[0], 1)}, {_fmt(ci[1], 1)}]",
        },
    ]


def _nearest_prototype_field(base: dict) -> list[dict]:
    fb = base.get("field_benchmark", {})
    np_ = fb.get("system_summaries", {}).get("Rule: Nearest Prototype", {})
    if not np_:
        return []
    return [
        {
            "claim": "Nearest Prototype field positive-case recall",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(np_['mean_positive_recall'])}%",
        },
        {
            "claim": "Nearest Prototype field exact match",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(np_['mean_exact_match'])}%",
        },
        {
            "claim": "Nearest Prototype field micro-F1",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(np_['mean_micro_f1'])}",
        },
    ]


def _ricekg_verification(base: dict) -> list[dict]:
    synth = base.get("verification_suite",
                     base.get("synthetic_benchmark",
                              base.get("augmented_benchmark", {})))
    rk = synth.get("system_summaries", {}).get("RiceKG (Full Proposed)", {})
    if not rk:
        return []
    return [
        {
            "claim": "RiceKG verification-suite exact match",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(rk['mean_exact_match'])}%",
        },
    ]


def _field_counts(base: dict) -> list[dict]:
    fb = base.get("field_benchmark", {})
    rows = []
    if "n_positive" in fb:
        rows.append({
            "claim": "Field benchmark positive case count",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": str(fb["n_positive"]),
        })
    if "n_negative" in fb:
        rows.append({
            "claim": "Field benchmark negative control count",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": str(fb["n_negative"]),
        })
    return rows


def _extract_baselines(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        base = json.load(fh)
    rows = []
    rows.extend(_ricekg_field(base))
    rows.extend(_nearest_prototype_field(base))
    rows.extend(_ricekg_verification(base))
    rows.extend(_field_counts(base))

    # Per-ML-model positive recall on field benchmark
    fb = base.get("field_benchmark", {})
    for model_name, summary in fb.get("system_summaries", {}).items():
        if model_name.startswith("Rule:") or model_name.startswith("RiceKG"):
            continue
        rows.append({
            "claim": f"{model_name} field positive-recall (5×2-fold CV)",
            "command": "python baselines/run_baselines.py",
            "artifact": "results/baselines.json",
            "value": f"{_fmt(summary.get('mean_positive_recall', 0.0))}%",
        })
    return rows


def _extract_ablation(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        abl = json.load(fh)
    rows = []
    for r in abl.get("results", []):
        # ablation.json uses "exact_acc"; fall back to "exact_match" for future compat
        exact = r.get("exact_acc", r.get("exact_match", 0.0))
        rows.append({
            "claim": f"Ablation: {r['variant']} exact match (verification suite)",
            "command": "python ablation.py",
            "artifact": "results/ablation.json",
            "value": f"{_fmt(exact)}%",
        })
        rows.append({
            "claim": f"Ablation: {r['variant']} multi-label accuracy (verification suite)",
            "command": "python ablation.py",
            "artifact": "results/ablation.json",
            "value": f"{_fmt(r.get('multi_acc', 0.0))}%",
        })
        if "recall" in r:
            rows.append({
                "claim": f"Ablation: {r['variant']} positive recall (verification suite)",
                "command": "python ablation.py",
                "artifact": "results/ablation.json",
                "value": f"{_fmt(r['recall'])}%",
            })
    return rows


def _extract_learning_curve(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        lc = json.load(fh)
    rows: list[dict] = []

    # Gather crossover budgets per pool per model
    for pool_key in ("pool_a", "pool_b"):
        pool_data = lc.get(pool_key, {})
        pool_label = "Pool A (verification suite)" if pool_key == "pool_a" else "Pool B (field dev)"
        crossovers_found = False
        for model_name, model_data in pool_data.items():
            if not isinstance(model_data, dict):
                continue
            for budget_str, budget_data in model_data.items():
                if not isinstance(budget_data, dict):
                    continue
                if budget_data.get("is_crossover"):
                    crossovers_found = True
                    rows.append({
                        "claim": (
                            f"LC crossover: {model_name} exceeds RiceKG at N={budget_str} "
                            f"({pool_label})"
                        ),
                        "command": "python analysis/learning_curve.py",
                        "artifact": "results/learning_curve.json",
                        "value": "Yes (test-set CI excludes zero)",
                    })
        if not crossovers_found:
            rows.append({
                "claim": f"Learning-curve crossover detected ({pool_label})",
                "command": "python analysis/learning_curve.py",
                "artifact": "results/learning_curve.json",
                "value": "None (all test-set CIs include zero)",
            })

    # Zero-shot references from learning curve JSON
    refs = lc.get("zero_shot_references", {})
    for system_name, ref_data in refs.items():
        if isinstance(ref_data, dict) and "cv_positive_recall" in ref_data:
            rows.append({
                "claim": f"LC zero-shot reference: {system_name} positive recall",
                "command": "python analysis/learning_curve.py",
                "artifact": "results/learning_curve.json",
                "value": f"{_fmt(ref_data['cv_positive_recall'])}%",
            })

    return rows


def _extract_degradation_curve(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        deg = json.load(fh)
    rows: list[dict] = []
    systems = deg.get("systems", {})
    rk = systems.get("RiceKG (Full Proposed)", {})
    if "0.0" in rk:
        rows.append({
            "claim": "RiceKG degradation positive recall at 0.0 occlusion",
            "command": "python analysis/degradation_curve.py",
            "artifact": "results/degradation_curve.json",
            "value": f"{_fmt(rk['0.0']['positive_recall_mean'])}%",
        })
    if "0.4" in rk:
        rows.append({
            "claim": "RiceKG degradation positive recall at 0.4 occlusion",
            "command": "python analysis/degradation_curve.py",
            "artifact": "results/degradation_curve.json",
            "value": f"{_fmt(rk['0.4']['positive_recall_mean'])}%",
        })
    if "0.8" in rk:
        rows.append({
            "claim": "RiceKG degradation positive recall at 0.8 occlusion",
            "command": "python analysis/degradation_curve.py",
            "artifact": "results/degradation_curve.json",
            "value": f"{_fmt(rk['0.8']['positive_recall_mean'])}%",
        })
    return rows


def _extract_top_k(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    rows: list[dict] = []
    evals = data.get("evaluations", [])
    eval_split = next((e for e in evals if e.get("split") == "eval"), None)
    if eval_split:
        systems = eval_split.get("systems", {})
        rk = systems.get("RiceKG (Full Proposed)", {})
        if rk:
            rows.append({
                "claim": "RiceKG Top-1 differential hit on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(rk.get('hit_at_1_any'))}%",
            })
            rows.append({
                "claim": "RiceKG Top-3 differential hit on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(rk.get('hit_at_3_any'))}%",
            })
            rows.append({
                "claim": "RiceKG Top-k MRR on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(rk.get('mrr'), 3)}",
            })
            rows.append({
                "claim": "RiceKG Top-3 negative-control specificity on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(rk.get('specificity_at_3'))}%",
            })
        np_ = systems.get("Rule: Nearest Prototype", {})
        if np_:
            rows.append({
                "claim": "Nearest Prototype Top-3 differential hit on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(np_.get('hit_at_3_any'))}%",
            })
        flat = systems.get("Rule: Flat Single-Tier", {})
        if flat:
            rows.append({
                "claim": "Flat Single-Tier Top-1 differential hit on field eval",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(flat.get('hit_at_1_any'))}%",
            })

    holdout_split = next((e for e in evals if e.get("split") == "holdout"), None)
    if holdout_split:
        rk_h = holdout_split.get("systems", {}).get("RiceKG (Full Proposed)", {})
        if rk_h:
            rows.append({
                "claim": "RiceKG Top-3 differential hit on holdout (tiers A-C)",
                "command": "python analysis/differential_analysis.py",
                "artifact": "results/top_k.json",
                "value": f"{_fmt(rk_h.get('hit_at_3_any'))}%",
            })
    return rows


# ---------------------------------------------------------------------------
# Dispatch table: filename → extractor function
# ---------------------------------------------------------------------------

EXTRACTORS: dict[str, object] = {
    "baselines.json": _extract_baselines,
    "ablation.json": _extract_ablation,
    "learning_curve.json": _extract_learning_curve,
    "degradation_curve.json": _extract_degradation_curve,
    "top_k.json": _extract_top_k,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_index() -> str:
    """Return the full Markdown content for docs/RESULTS_INDEX.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    header = textwrap.dedent(f"""\
        <!-- GENERATED FILE — DO NOT EDIT BY HAND -->
        <!-- Regenerate with: python analysis/build_results_index.py -->
        <!-- Wired into: make reproduce, CI (check_readme_consistency.py) -->

        # Results Index

        Auto-generated on {now} from `results/*.json`.
        Each row maps a manuscript claim to the command that produces it and the
        source artifact that stores the value. Edit
        `analysis/build_results_index.py` to change what is indexed.

        | Manuscript claim | Command | Source artifact | Value |
        |---|---|---|---|
    """)

    rows: list[dict] = []
    missing: list[str] = []

    for filename, extractor in EXTRACTORS.items():
        path = RESULTS_DIR / filename
        if not path.exists():
            missing.append(filename)
            continue
        try:
            rows.extend(extractor(path))  # type: ignore[operator]
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not parse {filename}: {exc}", file=sys.stderr)

    table_lines = []
    for row in rows:
        claim = row["claim"].replace("|", "\\|")
        cmd = f"`{row['command']}`"
        artifact = f"`{row['artifact']}`"
        value = str(row["value"]).replace("|", "\\|")
        table_lines.append(f"| {claim} | {cmd} | {artifact} | {value} |")

    body = "\n".join(table_lines)

    footer_parts = [""]
    if missing:
        footer_parts.append(
            "> [!WARNING]"
        )
        footer_parts.append(
            "> The following results files were **not found** when this index was generated; "
            "their rows are absent:"
        )
        for f in missing:
            footer_parts.append(f"> - `results/{f}`")
        footer_parts.append(
            ">\n> Run `make reproduce` to regenerate them."
        )

    footer_parts.append(
        "\n---\n"
        "_This file is produced by `analysis/build_results_index.py` "
        "and validated by `analysis/check_readme_consistency.py`. "
        "A stale or missing index fails the CI build._"
    )

    return header + body + "\n".join(footer_parts) + "\n"


HASH_PREFIX = "<!-- content-sha256: "


def strip_hash_line(content: str) -> str:
    """Return `content` with the content-sha256 comment removed."""
    return "".join(
        line for line in content.splitlines(keepends=True)
        if not line.startswith(HASH_PREFIX)
    )


def stamp_hash(content: str) -> str:
    """Insert a content-sha256 comment computed over the unstamped content."""
    body = strip_hash_line(content)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    lines = body.splitlines(keepends=True)
    lines.insert(1, HASH_PREFIX + digest + " -->\n")
    return "".join(lines)


def verify_hash(content: str) -> bool:
    """True when the embedded content-sha256 matches the rest of the file."""
    stamped = [l for l in content.splitlines() if l.startswith(HASH_PREFIX)]
    if len(stamped) != 1:
        return False
    recorded = stamped[0][len(HASH_PREFIX):].rstrip(" ->").strip()
    actual = hashlib.sha256(strip_hash_line(content).encode("utf-8")).hexdigest()
    return recorded == actual


def main() -> int:
    content = stamp_hash(build_index())
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Written: {OUTPUT.relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
