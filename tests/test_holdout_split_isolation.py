"""
tests/test_holdout_split_isolation.py
-------------------------------------
Regression test suite asserting strict split isolation and integrity
of the merged holdout partition in data/benchmark_field.csv (NEXT_TASK.md 6-H.5).

Guarantees:
1. Holdout cases (split='holdout') never enter dev or eval splits in any loader.
2. The merged holdout partition reproduces the exact locked SHA-256 hash.
3. Tiers A, B, and C integrity constraints are strictly enforced.
"""

import os
import csv
import io
import hashlib
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELD_CSV = os.path.join(BASE_DIR, "data", "benchmark_field.csv")

LOCKED_HOLDOUT_SHA256 = "8616419d0781ae2f9c62ba80f3bee8581d0f10798a6d1598ec837e7f29aa9aaa"


def _read_field_csv():
    assert os.path.exists(FIELD_CSV), f"Missing {FIELD_CSV}"
    with open(FIELD_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_field_benchmark_split_counts():
    rows = _read_field_csv()
    splits = {r["case_id"]: r["split"] for r in rows}

    dev_cases = [cid for cid, s in splits.items() if s == "dev"]
    eval_cases = [cid for cid, s in splits.items() if s == "eval"]
    holdout_cases = [cid for cid, s in splits.items() if s == "holdout"]

    assert len(dev_cases) == 16, f"Expected 16 dev cases, found {len(dev_cases)}"
    assert len(eval_cases) == 23, f"Expected 23 eval cases, found {len(eval_cases)}"
    assert len(holdout_cases) == 18, f"Expected 18 holdout cases, found {len(holdout_cases)}"
    assert len(rows) == 57, f"Expected 57 total cases, found {len(rows)}"

    # Mutual disjointness
    assert not (set(dev_cases) & set(eval_cases))
    assert not (set(dev_cases) & set(holdout_cases))
    assert not (set(eval_cases) & set(holdout_cases))


def test_evaluate_load_data_split_isolation():
    import evaluate

    # 1. Dev split only
    dev_data = evaluate.load_data(FIELD_CSV, split="dev")
    assert len(dev_data) == 16
    assert all(c["split"] == "dev" for c in dev_data)
    assert not any(c["split"] == "holdout" for c in dev_data)

    # 2. Eval split only
    eval_data = evaluate.load_data(FIELD_CSV, split="eval")
    assert len(eval_data) == 23
    assert all(c["split"] == "eval" for c in eval_data)
    assert not any(c["split"] == "holdout" for c in eval_data)

    # 3. Benchmark tuple split
    bench_data = evaluate.load_data(FIELD_CSV, split=("dev", "eval"))
    assert len(bench_data) == 39
    assert all(c["split"] in ("dev", "eval") for c in bench_data)
    assert not any(c["split"] == "holdout" for c in bench_data)

    # 4. Holdout split only
    holdout_data = evaluate.load_data(FIELD_CSV, split="holdout")
    assert len(holdout_data) == 18
    assert all(c["split"] == "holdout" for c in holdout_data)


def test_baselines_loader_split_isolation():
    from baselines import ml_baselines

    # Dev split
    _, _, dev_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="dev")
    assert len(dev_cases) == 16
    assert not any(c["split"] == "holdout" for c in dev_cases)

    # Eval split
    _, _, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")
    assert len(eval_cases) == 23
    assert not any(c["split"] == "holdout" for c in eval_cases)


def test_field_failure_analysis_split_isolation():
    from analysis import field_failure_analysis

    bench_cases = field_failure_analysis.load_cases(split="benchmark")
    assert len(bench_cases) == 39
    assert not any(c.get("split") == "holdout" for c in bench_cases)


def test_merged_holdout_byte_identity_hash():
    with open(FIELD_CSV, "r", encoding="utf-8", newline="") as f:
        reader = list(csv.reader(f))

    header = reader[0]
    holdout_rows = [header] + [r for r in reader[1:] if r[17] == "holdout"]
    assert len(holdout_rows) == 19  # 1 header + 18 rows

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    for r in holdout_rows:
        w.writerow(r)

    serialized_bytes = buf.getvalue().encode("utf-8")
    computed_hash = hashlib.sha256(serialized_bytes).hexdigest()
    assert computed_hash == LOCKED_HOLDOUT_SHA256, (
        f"Merged holdout partition SHA-256 mismatch! Expected {LOCKED_HOLDOUT_SHA256}, got {computed_hash}"
    )


def test_tier_constraints_across_all_field_cases():
    rows = _read_field_csv()
    for r in rows:
        tier = r.get("evidence_tier", "").strip()
        assert tier in ("A", "B", "C"), f"Case {r['case_id']} invalid tier '{tier}'"

        if tier in ("A", "B"):
            assert r["doi"].strip().startswith("10."), f"Case {r['case_id']} must have valid DOI"
        elif tier == "C":
            assert r["source_url"].strip(), f"Case {r['case_id']} must have source_url"
            assert r["archive_url"].strip(), f"Case {r['case_id']} must have archive_url"
            assert r["accessed"].strip(), f"Case {r['case_id']} must have accessed date"

        if tier in ("B", "C"):
            assert r["tier_note"].strip(), f"Case {r['case_id']} (Tier {tier}) must have tier_note"

        assert r["raw_symptom_text"].strip(), f"Case {r['case_id']} missing raw_symptom_text"
        assert r["citation"].strip(), f"Case {r['case_id']} missing citation"
