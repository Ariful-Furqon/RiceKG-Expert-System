"""
tests/test_p0_5_field.py
------------------------
Integrity gates for the independent field benchmark (P0-5).

These tests fix *structural* requirements — the case-report gate, split hygiene, and
source-level separation — not a desired level of coverage. Coverage that the peer-reviewed
literature does not supply must be disclosed in `docs/LIMITATIONS.md`, never asserted into
existence here.

1. `split` column exists with values strictly in {"dev", "eval"}, disjoint by case id.
2. No source publication (DOI) straddles the dev/eval boundary.
3. Every retained row is a case report (`case_type`), the P0-3 extraction gate.
4. Rejected candidates are preserved with a stated reason and excluded from the benchmark.
5. Both splits contain positives and negatives.
6. Threat classes with no positive case are disclosed in docs/LIMITATIONS.md.
7. Authentic DOIs and citations for all rows.
"""

import csv
import os

from ricekg import evaluate

FIELD_CSV = os.path.join(evaluate.BASE_DIR, "data", "benchmark_field.csv")
REJECTED_CSV = os.path.join(evaluate.BASE_DIR, "data", "rejected_field_candidates.csv")
LIMITATIONS = os.path.join(evaluate.BASE_DIR, "docs", "LIMITATIONS.md")


def _rows(path=FIELD_CSV):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_split_column_present_and_disjoint():
    rows = _rows()
    assert rows, "Field benchmark must not be empty"
    assert "split" in rows[0], "data/benchmark_field.csv must carry a 'split' column"

    values = {r["split"] for r in rows}
    assert values <= {"dev", "eval", "holdout"}, f"Unexpected split values: {values - {'dev', 'eval', 'holdout'}}"

    dev = {r["case_id"] for r in rows if r["split"] == "dev"}
    ev = {r["case_id"] for r in rows if r["split"] == "eval"}
    hold = {r["case_id"] for r in rows if r["split"] == "holdout"}
    assert not (dev & ev), f"Cases appear in both dev and eval: {sorted(dev & ev)}"
    assert not (dev & hold), f"Cases appear in both dev and holdout: {sorted(dev & hold)}"
    assert not (ev & hold), f"Cases appear in both eval and holdout: {sorted(ev & hold)}"


def test_no_source_publication_straddles_the_split():
    """Two cases drawn from one paper leak development information into the held-out set.

    Case-id disjointness does not catch this: FIELD_42 and FIELD_43 were sourced from a
    single DOI and assigned to different splits during P0-5 Step 1.
    """
    rows = _rows()
    by_doi = {}
    for r in rows:
        doi = r["doi"].strip().lower()
        if doi:
            by_doi.setdefault(doi, set()).add(r["split"])

    straddling = {doi: splits for doi, splits in by_doi.items() if len(splits) > 1}
    assert not straddling, (
        "These source publications appear in both dev and eval, leaking development "
        f"information into the held-out set: {sorted(straddling)}"
    )


def test_every_retained_case_is_a_case_report():
    """The P0-3 gate admits observed-case reports only, not reviews or trials."""
    rows = _rows()
    assert "case_type" in rows[0], "data/benchmark_field.csv must carry a 'case_type' column"

    offenders = [r["case_id"] for r in rows if r["case_type"] != "case_report"]
    assert not offenders, (
        "Non-case-report sources must be moved to data/rejected_field_candidates.csv, "
        f"not retained in the benchmark: {offenders}"
    )


def test_rejected_candidates_are_preserved_with_reasons():
    assert os.path.exists(REJECTED_CSV), (
        "Rejected sourcing candidates must be preserved for audit, not deleted"
    )
    rejected = _rows(REJECTED_CSV)
    assert rejected, "Rejected candidate file must not be empty while rejections exist"

    for r in rejected:
        assert r.get("rejection_reason", "").strip(), (
            f"{r['case_id']} must state why it failed the case-report gate"
        )

    retained_ids = {r["case_id"] for r in _rows()}
    leaked = retained_ids & {r["case_id"] for r in rejected}
    assert not leaked, f"Rejected candidates still present in the benchmark: {sorted(leaked)}"


def test_both_splits_contain_positives_and_negatives():
    rows = _rows()
    for split in ("dev", "eval"):
        subset = [r for r in rows if r["split"] == split]
        positives = [r for r in subset if r["diagnosis"] != "No_Diagnosis"]
        negatives = [r for r in subset if r["diagnosis"] == "No_Diagnosis"]
        assert positives, f"{split} split must contain positive cases"
        assert negatives, f"{split} split must contain negative controls"


def test_uncovered_threat_classes_are_disclosed():
    """Classes with no positive case are a real sourcing limitation, not a test failure.

    The requirement is that the gap is stated in the limitations document, so a reader
    never infers coverage the benchmark does not have.
    """
    rows = _rows()
    covered = set()
    for r in rows:
        if r["diagnosis"] != "No_Diagnosis":
            covered.update(t.strip() for t in r["diagnosis"].split(" and ") if t.strip())

    uncovered = sorted(set(evaluate.ALL_DIAGNOSES) - covered)
    if not uncovered:
        return

    with open(LIMITATIONS, encoding="utf-8") as f:
        text = f.read()

    undisclosed = [t for t in uncovered if t not in text]
    assert not undisclosed, (
        "These threat classes have no positive field case and are not disclosed in "
        f"docs/LIMITATIONS.md: {undisclosed}"
    )


def test_doi_and_citation_integrity():
    for r in _rows():
        tier = r.get("evidence_tier", "").strip()
        if tier in ("A", "B"):
            assert r["doi"].strip().startswith("10."), f"{r['case_id']} has no usable DOI"
        elif tier == "C":
            assert r.get("source_url", "").strip(), f"{r['case_id']} has no source_url"
            assert r.get("archive_url", "").strip(), f"{r['case_id']} has no archive_url"
        else:
            assert r["doi"].strip().startswith("10."), f"{r['case_id']} has no usable DOI"
        assert r["citation"].strip(), f"{r['case_id']} has an empty citation"
