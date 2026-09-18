"""
tests/test_negative_control_out_of_scope.py
-------------------------------------------
Unit tests verifying PART 4 requirement 4-J:
When a negative control's signs map but match none of the six in-scope disease
classes, the output is an explicit "signs recorded, not consistent with any disease in scope"
response, distinct from both a positive diagnosis and the insect out-of-scope response.
"""

import pytest
from ricekg import model


def test_unmodeled_pathogen_signs_yield_negative_control_response():
    """Negative control with mapped disease signs (e.g. Sheath Blight, Rhizoctonia solani)
    yields the explicit non-modeled disease out-of-scope response."""
    symptoms = ["Leaf_Sheath_Lesions", "Rotten_Panicles"]
    results = model.predict_diseases(symptoms)

    assert len(results) == 1, f"Expected 1 response, got {len(results)}"
    res = results[0]
    assert res["grade"] == "out_of_scope"
    assert res["threat"] == model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET
    assert res["threat"] not in model.ALL_DIAGNOSES, "Negative control response must not be an in-scope diagnosis"
    assert model.NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE in res["message"]
    assert "Leaf_Sheath_Lesions" in res["matched_symptoms"]


def test_bacterial_panicle_blight_control_yields_out_of_scope():
    """Burkholderia glumae negative control symptoms (Grain_Discoloration + Empty_Grains)
    yields the explicit out-of-scope response."""
    symptoms = ["Grain_Discoloration", "Empty_Grains"]
    results = model.predict_diseases(symptoms)

    assert len(results) == 1
    res = results[0]
    assert res["threat"] == model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET
    assert res["grade"] == "out_of_scope"


def test_newly_mapped_signs_yield_out_of_scope_for_negative_controls():
    """Newly mapped signs from 4-J (e.g. Chlorotic_Streaks for Bacterial Leaf Streak)
    yield the explicit out-of-scope response when presented alone."""
    symptoms = ["Chlorotic_Streaks"]
    results = model.predict_diseases(symptoms)

    assert len(results) == 1
    res = results[0]
    assert res["threat"] == model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET


def test_distinct_from_insect_out_of_scope():
    """Asserts that negative control out-of-scope is distinct from insect out-of-scope."""
    assert model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET != model.INSECT_OUT_OF_SCOPE_TARGET
    assert model.NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE != model.INSECT_OUT_OF_SCOPE_RESPONSE
