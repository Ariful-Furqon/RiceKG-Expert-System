"""Partial-match `possible` grade.

Strict Horn-clause matching returns nothing when a single Tier-2 antecedent is
unobserved, discarding strong partial evidence: on the field benchmark's dev split three
of the seven positive cases failed at one antecedent short of two. The `possible` grade
surfaces those as a weaker, clearly-labelled hypothesis.

These tests fix the behaviour that must not regress: the v1 surface is unchanged, the
grade is opt-in, it respects its threshold, and it stays auditable.
"""
from ricekg import model
import pytest


def _grades(results):
    return {r["threat"]: r["grade"] for r in results}


# One antecedent of the two-antecedent bacterial blight rule (SWRL-R16) is absent, so the
# rule cannot fire; coverage is 1/2, which clears the default threshold.
PARTIAL_BLB = ["Water_Soaked_Lesions", "Bacterial_Ooze", "Yellowing_Leaves"]


class TestBackwardsCompatibility:
    """The v1 API surface must behave exactly as before the grade was introduced."""

    def test_possible_is_off_by_default(self):
        assert model.predict_diseases(PARTIAL_BLB) == []

    def test_flat_helper_never_returns_possible(self):
        assert model.predict_diseases_flat(PARTIAL_BLB) == []

    def test_flat_helper_still_returns_fired_diagnoses(self):
        smut = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R17")["antecedents"]
        assert "False_Smut" in model.predict_diseases_flat(list(smut))


class TestPartialMatching:
    def test_partial_evidence_is_surfaced_as_possible(self):
        results = model.predict_diseases(PARTIAL_BLB, include_possible=True)
        assert _grades(results).get("Bacterial_Leaf_Blight") == "possible"

    def test_threshold_is_respected(self):
        original = model.POSSIBLE_COVERAGE_THRESHOLD
        try:
            model.POSSIBLE_COVERAGE_THRESHOLD = 1.0
            assert model.predict_diseases(PARTIAL_BLB, include_possible=True) == [], (
                "Coverage of 0.5 must not clear a threshold of 1.0"
            )
        finally:
            model.POSSIBLE_COVERAGE_THRESHOLD = original

    def test_a_fired_rule_is_never_downgraded_to_possible(self):
        smut = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R17")["antecedents"]
        grades = _grades(model.predict_diseases(list(smut), include_possible=True))
        assert grades["False_Smut"] in {"confirmed", "suspected", "unstratified"}

    def test_possible_diagnoses_remain_auditable(self):
        results = model.predict_diseases(PARTIAL_BLB, include_possible=True)
        possible = [r for r in results if r["grade"] == "possible"]
        assert possible, "Expected at least one possible diagnosis"
        for r in possible:
            assert r["matched_symptoms"], "A possible diagnosis must name the evidence for it"
            assert r["missing_symptoms"], "A possible diagnosis must name the unmet antecedents"
            assert 0.0 < r["antecedent_coverage"] < 1.0
            assert r["fired_rules"] == [], "No rule fired; the field must say so"

    def test_confidence_ranks_below_a_fired_diagnosis(self):
        smut = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R17")["antecedents"]
        combined = list(smut) + PARTIAL_BLB
        results = model.predict_diseases(combined, include_possible=True)
        by_threat = {r["threat"]: r for r in results}

        assert by_threat["False_Smut"]["grade"] != "possible"
        if "Bacterial_Leaf_Blight" in by_threat:
            possible = by_threat["Bacterial_Leaf_Blight"]
            assert possible["grade"] == "possible"
            assert possible["confidence"] < by_threat["False_Smut"]["confidence"]
            # Ordinal grades drive the ranking, so the fired diagnosis is listed first.
            order = [r["threat"] for r in results]
            assert order.index("False_Smut") < order.index("Bacterial_Leaf_Blight")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
