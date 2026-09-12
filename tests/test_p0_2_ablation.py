"""
tests/test_p0_2_ablation.py
---------------------------
Unit test suite verifying P0-2 implementation:
1. Declarative RULE_REGISTRY in model.py.
2. build_ontology(enabled_tiers=...) produces exact requested Imp() instances in isolated worlds.
3. Pellet DL reasoning across isolated ontology worlds.
4. Ablation variant execution and latency/accuracy output differences.
"""

import pytest
import owlready2
import model
import ablation


class TestP02AblationArchitecture:
    """Verifies that the SWRL rule set is dynamically configurable via

    build_ontology() and exercises isolated Pellet DL inference.
    """

    def test_build_ontology_tier1_only_rule_count(self):
        """P0-2 Acceptance Criterion:

        A test asserts that build_ontology(enabled_tiers={'tier1'})
        contains exactly 10 Imp() instances.
        """
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        rules = list(onto_t1.rules())
        assert len(rules) == 10
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_build_ontology_tier2_only_rule_count(self):
        onto_t2 = model.build_ontology(enabled_tiers={"tier2"})
        rules = list(onto_t2.rules())
        assert len(rules) == 10
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_build_ontology_full_rule_count(self):
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})
        rules = list(onto_full.rules())
        assert len(rules) == 20
        assert all(isinstance(r, owlready2.swrl.Imp) for r in rules)

    def test_isolated_world_no_cross_contamination(self):
        """Ensures that ontologies built in different calls reside in distinct

        owlready2.World instances and do not mutate or leak rules.
        """
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})

        assert onto_t1.world is not onto_full.world
        assert len(list(onto_t1.rules())) == 10
        assert len(list(onto_full.rules())) == 20

    def test_no_reasoner_set_matching_baseline(self):
        """Tests the pure-Python set-matching control baseline."""
        canonical_symptoms = [
            "Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant",
            "Broad_Leaf_Damage", "Severed_Panicles", "Leaf_Chewing_Damage"
        ]
        relaxed_symptoms = [
            "Severed_Panicles", "Leaf_Chewing_Damage"
        ]

        preds_canon = ablation.predict_no_reasoner(canonical_symptoms)
        preds_relax = ablation.predict_no_reasoner(relaxed_symptoms)

        assert "Grasshopper" in preds_canon
        assert "Grasshopper" in preds_relax

    def test_pellet_inference_on_ablated_ontology(self):
        """Tests that Pellet DL reasoning executes correctly on an ablated ontology world."""
        onto_t1 = model.build_ontology(enabled_tiers={"tier1"})
        relaxed_symptoms = ["Severed_Panicles", "Leaf_Chewing_Damage"]

        # In Tier 1 only, relaxed symptoms must NOT trigger Grasshopper diagnosis
        preds_t1 = model.predict_diseases_flat(relaxed_symptoms, onto=onto_t1)
        assert "Grasshopper" not in preds_t1

        # In Full model, relaxed symptoms DO trigger Grasshopper diagnosis
        onto_full = model.build_ontology(enabled_tiers={"tier1", "tier2"})
        preds_full = model.predict_diseases_flat(relaxed_symptoms, onto=onto_full)
        assert "Grasshopper" in preds_full

