# tests/test_p0_2_ablation.py
# ---------------------------
# Unit test suite verifying P0-2 implementation:
# 1. Declarative RULE_REGISTRY in model.py.
# 2. build_ontology(enabled_tiers=...) produces exact requested Imp() instances in isolated worlds.
# 3. Pellet DL reasoning across isolated ontology worlds.
# 4. Ablation variant execution and latency/accuracy output differences.

import pytest
import owlready2
from ricekg import model
from analysis import ablation

# 6 primary composite rules plus the 6 diagnostic-sign rules of ruleset v2.4.0
N_TIER2 = 12
assert N_TIER2 == sum(1 for r in model.RULE_REGISTRY if r["tier"] == "tier2")


class TestP02AblationArchitecture:
    # Verifies that the SWRL rule set is dynamically configurable via
    #
    # build_ontology() and exercises isolated Pellet DL inference.

    def test_build_ontology_tier1_only_rule_count(self):
        # P0-2 Acceptance Criterion:
        #
        # A test asserts that build_ontology(enabled_tiers={'tier1'})
        # contains exactly 6 Imp() instances.
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        rules = list(onto_t1.rules())
        assert len(rules) == 6
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_build_ontology_tier2_only_rule_count(self):
        onto_t2 = model.build_ontology(enabled_tiers={"tier2"})
        rules = list(onto_t2.rules())
        assert len(rules) == N_TIER2
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_build_ontology_full_rule_count(self):
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})
        rules = list(onto_full.rules())
        assert len(rules) == 6 + N_TIER2
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_isolated_world_no_cross_contamination(self):
        # Ensures that ontologies built in different calls reside in distinct
        #
        # owlready2.World instances and do not mutate or leak rules.
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})

        assert onto_t1.world is not onto_full.world
        assert len(list(onto_t1.rules())) == 6
        assert len(list(onto_full.rules())) == 6 + N_TIER2

    def test_no_reasoner_set_matching_baseline(self):
        # Tests the pure-Python set-matching control baseline.
        canonical_symptoms = [
            "Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection",
            "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability"
        ]
        relaxed_symptoms = [
            "Rusty_Grain_Balls", "Blackened_Grain_Balls"
        ]

        preds_canon = ablation.predict_no_reasoner(canonical_symptoms)
        preds_relax = ablation.predict_no_reasoner(relaxed_symptoms)

        assert "False_Smut" in preds_canon
        assert "False_Smut" in preds_relax

    def test_pellet_inference_on_ablated_ontology(self):
        # Tests that Pellet DL reasoning executes correctly on an ablated ontology world.
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        relaxed_symptoms = ["Rusty_Grain_Balls", "Blackened_Grain_Balls"]

        # In Tier 1 only, relaxed symptoms must NOT trigger False_Smut diagnosis
        preds_t1 = model.predict_diseases_flat(relaxed_symptoms, onto=onto_t1)
        assert "False_Smut" not in preds_t1

        # In Full model, relaxed symptoms DO trigger False_Smut diagnosis
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})
        preds_full = model.predict_diseases_flat(relaxed_symptoms, onto=onto_full)
        assert "False_Smut" in preds_full



# ---------------------------------------------------------------------------
# Redesigned ablation (reasoner equivalence and rule-component variants)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("symptoms", [
    ["Diamond_Shaped_Lesions"],                          # diagnostic-sign rule SWRL-R26
    ["Necrotic_Spots"],                                  # `possible` blast only
    ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves"],
    ["Brown_Nymphs", "Hopperburn_Drying"],               # insect out-of-scope gate
    ["Leaf_Sheath_Lesions"],                             # non-modelled pathogen gate
    ["Leaf_Mottling"],                                   # nothing fires
])
def test_set_matching_equals_pellet_graded_output(symptoms):
    pellet = {(r["threat"], r["grade"]) for r in model.predict_diseases(symptoms, include_possible=True)}
    assert set(ablation.predict_set_matching(symptoms)) == pellet


def test_variant_rules_select_expected_subsets():
    full = ablation.variant_rules("full")
    no_signs = ablation.variant_rules("no_diagnostic_signs")
    tier1 = ablation.variant_rules("tier1_only")
    assert len(full) == len(model.RULE_REGISTRY)
    assert len(full) - len(no_signs) == 6
    assert all(r["tier"] == "tier1" for r in tier1) and len(tier1) == 6
    # Without the diagnostic-sign rules a lone diamond lesion no longer commits blast
    assert ablation.predict_set_matching(["Diamond_Shaped_Lesions"], no_signs, include_possible=False) == []
