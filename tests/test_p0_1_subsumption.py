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
from ricekg import model


class TestP01SubsumptionResolution:
    """Proves Tier 1 and Tier 2 yield distinguishable outputs for inputs
    where they previously yielded identical output.
    """

    def test_rice_root_nematode_canonical_vs_relaxed_distinguishable(self):
        canonical = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R02")
        relaxed = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R12")
        canonical_symptoms = list(canonical["antecedents"])
        relaxed_symptoms = list(relaxed["antecedents"])

        out_canonical = model.predict_diseases(canonical_symptoms)
        out_relaxed = model.predict_diseases(relaxed_symptoms)

        assert out_canonical != out_relaxed, "Tier 1 and Tier 2 outputs must not be identical"

        rrn_canon = next((d for d in out_canonical if d["threat"] == "Rice_Root_Nematode"), None)
        assert rrn_canon is not None
        assert rrn_canon["grade"] == "confirmed"
        assert rrn_canon["confidence"] == 1.0
        assert "SWRL-R02" in rrn_canon["fired_rules"]
        assert rrn_canon["missing_symptoms"] == []
        assert len(rrn_canon["matched_symptoms"]) == len(canonical_symptoms)

        rrn_relax = next((d for d in out_relaxed if d["threat"] == "Rice_Root_Nematode"), None)
        assert rrn_relax is not None
        assert rrn_relax["grade"] == "suspected"
        assert rrn_relax["confidence"] == 0.9714
        assert "SWRL-R02" not in rrn_relax["fired_rules"]
        assert "SWRL-R12" in rrn_relax["fired_rules"]
        assert len(rrn_relax["missing_symptoms"]) > 0

    def test_rice_blast_canonical_vs_relaxed_distinguishable(self):
        """Tier-1 and Tier-2 must yield distinguishable output for Rice_Blast.

        The antecedent sets are read from RULE_REGISTRY rather than hardcoded, so a
        literature-justified rule revision does not read as a regression of P0-1.
        """
        canonical = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R08")
        relaxed = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R18")

        canonical_symptoms = list(canonical["antecedents"])
        relaxed_symptoms = list(relaxed["antecedents"])
        assert set(relaxed_symptoms) != set(canonical_symptoms)

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
        assert "SWRL-R08" not in rb_relax["fired_rules"], (
            "The canonical rule must not fire on the relaxed antecedent set alone"
        )
        assert "SWRL-R18" in rb_relax["fired_rules"]
        assert rb_relax["confidence"] < rb_canon["confidence"]
        assert rb_relax["missing_symptoms"], "A relaxed diagnosis must report unmet antecedents"

    def test_ranking_confirmed_before_suspected(self):
        # Provide full symptoms for False_Smut (canonical) + partial for Rice Blast (relaxed)
        composite_symptoms = [
            # False Smut full
            "Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection",
            "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability",
            # Rice Blast partial
            "Diamond_Shaped_Lesions", "Necrotic_Spots"
        ]

        out = model.predict_diseases(composite_symptoms)
        threat_names = [d["threat"] for d in out]
        assert "False_Smut" in threat_names
        assert "Rice_Blast" in threat_names

        # Confirmed threat must rank ahead of suspected threat
        smut_idx = threat_names.index("False_Smut")
        blast_idx = threat_names.index("Rice_Blast")
        assert smut_idx < blast_idx, "Confirmed diagnosis must rank ahead of suspected diagnosis"

        smut_diag = out[smut_idx]
        blast_diag = out[blast_idx]
        assert smut_diag["grade"] == "confirmed"
        assert blast_diag["grade"] == "suspected"

    def test_flat_wrapper_backward_compatibility(self):
        symptoms = ["Rusty_Grain_Balls", "Blackened_Grain_Balls"]
        flat_out = model.predict_diseases_flat(symptoms)

        assert isinstance(flat_out, list)
        assert all(isinstance(x, str) for x in flat_out)
        assert "False_Smut" in flat_out

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

