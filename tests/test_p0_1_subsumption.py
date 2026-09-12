"""
tests/test_p0_1_subsumption.py
------------------------------
Unit test suite verifying P0-1 fix:
Eliminate the Tier-1 / Tier-2 subsumption defect in model.py.

Verifies:
1. Canonical inputs yield distinguishable output from relaxed inputs (confirmed vs suspected).
2. Diagnostic confidence property (1.0 vs 0.7).
3. Rule firing traceability (both T1+T2 vs T2 only).
4. Missing symptoms identification in suspected diagnoses.
5. Backwards-compatible predict_diseases_flat returning List[str].
6. Object property hierarchy: hasConfirmedThreat and hasSuspectedThreat inherit to hasPest/hasDisease/hasThreat.
"""

import pytest
import model


class TestP01SubsumptionResolution:
    """Proves Tier 1 and Tier 2 yield distinguishable outputs for inputs
    where they previously yielded identical output.
    """

    def test_grasshopper_canonical_vs_relaxed_distinguishable(self):
        canonical_symptoms = [
            "Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant",
            "Broad_Leaf_Damage", "Severed_Panicles", "Leaf_Chewing_Damage"
        ]
        relaxed_symptoms = [
            "Severed_Panicles", "Leaf_Chewing_Damage"
        ]

        out_canonical = model.predict_diseases(canonical_symptoms)
        out_relaxed = model.predict_diseases(relaxed_symptoms)

        # 1. Previously both yielded ['Grasshopper'] identically.
        # Now their outputs MUST differ in grade, confidence, and fired rules.
        assert out_canonical != out_relaxed, "Tier 1 and Tier 2 outputs must not be identical"

        # 2. Canonical assertion verification
        gh_canon = next((d for d in out_canonical if d["threat"] == "Grasshopper"), None)
        assert gh_canon is not None
        assert gh_canon["grade"] == "confirmed"
        assert gh_canon["confidence"] == 1.0
        assert "SWRL-R01" in gh_canon["fired_rules"]
        assert "SWRL-R11" in gh_canon["fired_rules"]
        assert gh_canon["missing_symptoms"] == []
        assert len(gh_canon["matched_symptoms"]) == 6

        # 3. Relaxed assertion verification
        gh_relax = next((d for d in out_relaxed if d["threat"] == "Grasshopper"), None)
        assert gh_relax is not None
        assert gh_relax["grade"] == "suspected"
        assert gh_relax["confidence"] == 0.7
        assert "SWRL-R01" not in gh_relax["fired_rules"]
        assert "SWRL-R11" in gh_relax["fired_rules"]
        assert len(gh_relax["missing_symptoms"]) == 4
        assert "Brown_Nymphs" in gh_relax["missing_symptoms"]
        assert gh_relax["matched_symptoms"] == ["Severed_Panicles", "Leaf_Chewing_Damage"]

    def test_rice_blast_canonical_vs_relaxed_distinguishable(self):
        canonical_symptoms = [
            "Panicle_Neck_Rot", "Diamond_Shaped_Lesions",
            "Uniform_Field_Infection", "Infected_Seedlings"
        ]
        relaxed_symptoms = [
            "Panicle_Neck_Rot", "Diamond_Shaped_Lesions"
        ]

        out_canonical = model.predict_diseases(canonical_symptoms)
        out_relaxed = model.predict_diseases(relaxed_symptoms)

        assert out_canonical != out_relaxed

        rb_canon = next((d for d in out_canonical if d["threat"] == "Rice_Blast"), None)
        assert rb_canon is not None
        assert rb_canon["grade"] == "confirmed"
        assert rb_canon["confidence"] == 1.0
        assert "SWRL-R08" in rb_canon["fired_rules"]

        rb_relax = next((d for d in out_relaxed if d["threat"] == "Rice_Blast"), None)
        assert rb_relax is not None
        assert rb_relax["grade"] == "suspected"
        assert rb_relax["confidence"] == 0.7
        assert "SWRL-R08" not in rb_relax["fired_rules"]
        assert "SWRL-R18" in rb_relax["fired_rules"]
        assert "Uniform_Field_Infection" in rb_relax["missing_symptoms"]
        assert "Infected_Seedlings" in rb_relax["missing_symptoms"]

    def test_ranking_confirmed_before_suspected(self):
        # Provide full symptoms for False_Smut (canonical) + partial for Stem Borer (relaxed)
        composite_symptoms = [
            # False Smut full
            "Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection",
            "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability",
            # Stem Borer partial
            "Frass_In_Stem", "Bore_Holes_In_Stem"
        ]

        out = model.predict_diseases(composite_symptoms)
        threat_names = [d["threat"] for d in out]
        assert "False_Smut" in threat_names
        assert "Rice_Stem_Borer" in threat_names

        # Confirmed threat must rank ahead of suspected threat
        smut_idx = threat_names.index("False_Smut")
        borer_idx = threat_names.index("Rice_Stem_Borer")
        assert smut_idx < borer_idx, "Confirmed diagnosis must rank ahead of suspected diagnosis"

        smut_diag = out[smut_idx]
        borer_diag = out[borer_idx]
        assert smut_diag["grade"] == "confirmed"
        assert borer_diag["grade"] == "suspected"

    def test_flat_wrapper_backward_compatibility(self):
        symptoms = ["Severed_Panicles", "Leaf_Chewing_Damage"]
        flat_out = model.predict_diseases_flat(symptoms)

        assert isinstance(flat_out, list)
        assert all(isinstance(x, str) for x in flat_out)
        assert "Grasshopper" in flat_out

    def test_ontology_property_hierarchy(self):
        """Verifies that hasConfirmedPest and hasSuspectedPest properly inherit
        from hasConfirmedThreat/hasSuspectedThreat and hasPest/hasThreat.
        """
        onto = model.onto
        with onto:
            assert issubclass(onto.hasConfirmedPest, onto.hasConfirmedThreat)
            assert issubclass(onto.hasConfirmedPest, onto.hasPest)
            assert issubclass(onto.hasSuspectedPest, onto.hasSuspectedThreat)
            assert issubclass(onto.hasSuspectedPest, onto.hasPest)

            assert issubclass(onto.hasConfirmedDisease, onto.hasConfirmedThreat)
            assert issubclass(onto.hasConfirmedDisease, onto.hasDisease)
            assert issubclass(onto.hasSuspectedDisease, onto.hasSuspectedThreat)
            assert issubclass(onto.hasSuspectedDisease, onto.hasDisease)

            assert issubclass(onto.hasConfirmedThreat, onto.hasThreat)
            assert issubclass(onto.hasSuspectedThreat, onto.hasThreat)
            assert issubclass(onto.hasPest, onto.hasThreat)
            assert issubclass(onto.hasDisease, onto.hasThreat)

