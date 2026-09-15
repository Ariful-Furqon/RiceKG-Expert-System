"""
tests/test_holdout_staging.py
-----------------------------
Validation suite for data/field_holdout_staging.csv (PART 6 requirement 6-E.1).

Enforces structural integrity, vocabulary membership, tier constraints,
uniqueness, and cross-dataset separation without executing the OWL reasoner.
"""

import csv
import os
import re
import pytest

import model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING_CSV = os.path.join(BASE_DIR, "data", "field_holdout_staging.csv")
BENCHMARK_FIELD_CSV = os.path.join(BASE_DIR, "data", "benchmark_field.csv")
REJECTED_CSV = os.path.join(BASE_DIR, "data", "rejected_field_candidates.csv")


@pytest.fixture(scope="module")
def staging_data():
    if not os.path.exists(STAGING_CSV):
        pytest.skip(f"{STAGING_CSV} retired per 6-H.5; holdout partition verified in test_holdout_split_isolation.py")
    with open(STAGING_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader if any(field.strip() for field in row)]
    return header, rows


def test_header_and_row_width(staging_data):
    header, rows = staging_data
    expected_width = len(header)
    assert expected_width == 25, f"Expected 25 header columns, found {expected_width}"

    for idx, row in enumerate(rows, 2):
        assert len(row) == expected_width, (
            f"Row {idx} ({row[0] if row else 'empty'}) has {len(row)} columns, "
            f"expected {expected_width}"
        )


def test_unique_identifiers(staging_data):
    header, rows = staging_data
    case_id_idx = header.index("case_id")
    doi_idx = header.index("doi")
    url_idx = header.index("source_url")

    case_ids = set()
    ident_set = set()

    for idx, row in enumerate(rows, 2):
        case_id = row[case_id_idx].strip()
        assert case_id, f"Row {idx} missing case_id"
        assert case_id not in case_ids, f"Duplicate case_id: {case_id}"
        case_ids.add(case_id)

        doi = row[doi_idx].strip()
        source_url = row[url_idx].strip()
        ident = doi if doi else source_url
        assert ident, f"Row {idx} ({case_id}) missing both doi and source_url"
        assert ident not in ident_set, f"Duplicate identifier ({ident}) in row {idx} ({case_id})"
        ident_set.add(ident)


def test_vocabulary_membership(staging_data):
    header, rows = staging_data
    diag_idx = header.index("diagnosis")
    symptom_indices = [header.index(f"symptom_{i}") for i in range(1, 7)]

    valid_symptoms = set(model.ALL_SYMPTOMS)
    valid_diagnoses = set(model.ALL_DIAGNOSES)

    for idx, row in enumerate(rows, 2):
        case_id = row[0]
        diag = row[diag_idx].strip()
        assert diag in valid_diagnoses, (
            f"Row {idx} ({case_id}) has invalid diagnosis '{diag}'. "
            f"Must be one of {valid_diagnoses}"
        )

        observed_symptoms = 0
        for s_idx in symptom_indices:
            s = row[s_idx].strip()
            if s:
                assert s in valid_symptoms, (
                    f"Row {idx} ({case_id}) has invalid symptom '{s}'."
                )
                observed_symptoms += 1
        assert observed_symptoms > 0, f"Row {idx} ({case_id}) has no mapped symptoms"


def test_evidence_tiers_and_constraints(staging_data):
    header, rows = staging_data
    tier_idx = header.index("evidence_tier")
    note_idx = header.index("tier_note")
    doi_idx = header.index("doi")
    url_idx = header.index("source_url")
    accessed_idx = header.index("accessed")
    archive_idx = header.index("archive_url")
    text_idx = header.index("raw_symptom_text")

    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    for idx, row in enumerate(rows, 2):
        case_id = row[0]
        tier = row[tier_idx].strip()
        assert tier in {"A", "B", "C"}, (
            f"Row {idx} ({case_id}) has invalid evidence_tier '{tier}'. Must be A, B, or C."
        )

        raw_text = row[text_idx].strip()
        assert raw_text, f"Row {idx} ({case_id}) missing raw_symptom_text"

        tier_note = row[note_idx].strip()
        doi = row[doi_idx].strip()
        source_url = row[url_idx].strip()
        accessed = row[accessed_idx].strip()
        archive_url = row[archive_idx].strip()

        if tier in {"B", "C"}:
            assert tier_note, f"Row {idx} ({case_id}) in tier {tier} requires a non-empty tier_note"

        if tier in {"A", "B"}:
            assert doi.startswith("10."), (
                f"Row {idx} ({case_id}) in tier {tier} must have a DOI starting with '10.'"
            )
        elif tier == "C":
            assert source_url, f"Row {idx} ({case_id}) in tier C requires source_url"
            assert date_regex.match(accessed), (
                f"Row {idx} ({case_id}) in tier C requires accessed in YYYY-MM-DD format, got '{accessed}'"
            )
            assert archive_url, f"Row {idx} ({case_id}) in tier C requires archive_url"


def test_cross_dataset_separation(staging_data):
    header, rows = staging_data
    doi_idx = header.index("doi")
    url_idx = header.index("source_url")

    staging_dois = {row[doi_idx].strip() for row in rows if row[doi_idx].strip()}
    staging_urls = {row[url_idx].strip() for row in rows if row[url_idx].strip()}

    # Check benchmark_field.csv
    if os.path.exists(BENCHMARK_FIELD_CSV):
        with open(BENCHMARK_FIELD_CSV, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("split") == "holdout":
                    continue
                doi = row.get("doi", "").strip()
                if doi:
                    assert doi not in staging_dois, (
                        f"Staging DOI {doi} already exists in benchmark_field.csv dev/eval"
                    )

    # Check rejected_field_candidates.csv
    if os.path.exists(REJECTED_CSV):
        with open(REJECTED_CSV, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row.get("doi", "").strip()
                cit = row.get("citation", "").strip()
                if doi:
                    assert doi not in staging_dois, (
                        f"Staging DOI {doi} already exists in rejected_field_candidates.csv"
                    )
                for url in staging_urls:
                    assert url not in cit, (
                        f"Staging source_url {url} appears in rejected_field_candidates.csv citation"
                    )

