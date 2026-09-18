"""
Unit tests for Noisy-OR parameter files and leak priors (PART 8-A).
Verifies schema, validity of domain terms, value ranges, qualitative scales,
no duplicates, and 100% coverage of ALL_SYMPTOMS in leak definitions.
"""

import csv
import os
import pytest
from ricekg import model
from analysis.verify_citations import verify_noisy_or_citations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAMS_CSV = os.path.join(BASE_DIR, "data", "noisy_or_parameters.csv")
LEAKS_CSV = os.path.join(BASE_DIR, "data", "noisy_or_leaks.csv")

QUALITATIVE_SCALE = {0.90, 0.70, 0.40, 0.15}


def test_noisy_or_parameters_schema_and_integrity():
    """Verify schema, domain taxonomy validity, and value constraints in parameters.csv."""
    assert os.path.exists(PARAMS_CSV), f"Missing {PARAMS_CSV}"

    with open(PARAMS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_fields = [
            "threat", "observation", "p_sign_given_threat", "elicitation",
            "source_phrase", "citation", "doi", "locator", "note"
        ]
        assert reader.fieldnames == expected_fields, f"Unexpected headers: {reader.fieldnames}"
        rows = list(reader)

    assert len(rows) > 0, "parameters.csv is empty"

    for idx, r in enumerate(rows):
        threat = r["threat"].strip()
        obs = r["observation"].strip()
        p_val = float(r["p_sign_given_threat"])
        elicitation = r["elicitation"].strip()
        source_phrase = r["source_phrase"].strip()
        citation = r["citation"].strip()

        assert threat in model.ALL_DIAGNOSES, f"Row {idx+1}: invalid threat {threat}"
        assert obs in model.ALL_SYMPTOMS, f"Row {idx+1}: invalid observation {obs}"
        assert 0.0 < p_val < 1.0, f"Row {idx+1}: probability out of range (0, 1): {p_val}"
        assert elicitation in {"quantitative", "qualitative"}, f"Row {idx+1}: invalid elicitation {elicitation}"
        assert len(source_phrase) > 0, f"Row {idx+1}: missing source_phrase"
        assert len(citation) > 0, f"Row {idx+1}: missing citation"

        if elicitation == "qualitative":
            assert any(abs(p_val - s) < 1e-6 for s in QUALITATIVE_SCALE), (
                f"Row {idx+1}: qualitative p={p_val} not in fixed scale {QUALITATIVE_SCALE}"
            )


def test_no_duplicate_threat_observation_pairs():
    """Verify that each (threat, observation) link is unique."""
    with open(PARAMS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        pairs = set()
        for idx, r in enumerate(reader):
            pair = (r["threat"].strip(), r["observation"].strip())
            assert pair not in pairs, f"Duplicate (threat, observation) pair at row {idx+1}: {pair}"
            pairs.add(pair)


def test_noisy_or_leaks_schema_and_coverage():
    """Verify schema, leak range, justification, and 100% coverage of ALL_SYMPTOMS."""
    assert os.path.exists(LEAKS_CSV), f"Missing {LEAKS_CSV}"

    with open(LEAKS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_fields = ["observation", "leak", "justification"]
        assert reader.fieldnames == expected_fields, f"Unexpected headers: {reader.fieldnames}"
        rows = list(reader)

    assert len(rows) == len(model.ALL_SYMPTOMS), (
        f"Expected {len(model.ALL_SYMPTOMS)} leak rows, got {len(rows)}"
    )

    leak_obs = set()
    for idx, r in enumerate(rows):
        obs = r["observation"].strip()
        leak = float(r["leak"])
        justification = r["justification"].strip()

        assert obs in model.ALL_SYMPTOMS, f"Row {idx+1}: invalid observation {obs}"
        assert 0.0 < leak < 1.0, f"Row {idx+1}: leak out of range (0, 1): {leak}"
        assert len(justification) > 0, f"Row {idx+1}: missing justification"
        leak_obs.add(obs)

    assert leak_obs == set(model.ALL_SYMPTOMS), (
        f"Missing observations in leaks.csv: {set(model.ALL_SYMPTOMS) - leak_obs}"
    )


def test_noisy_or_citations_verifier_passes():
    """Verify that verify_noisy_or_citations runs without failure."""
    assert verify_noisy_or_citations(PARAMS_CSV) is True

