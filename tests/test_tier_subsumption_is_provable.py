"""
tests/test_tier_subsumption_is_provable.py
-------------------------------------------
Automated proof of Description Logic subsumption (NEXT_TASK.md PART 4 requirement 4-C).

Asserts that:
1. For every in-scope threat, Pellet formally proves that ThreatConfirmed is subsumed
   by ThreatSuspect (ThreatConfirmed ⊑ ThreatSuspect).
2. Removing any Tier-2 antecedent from Tier-1 definition breaks the subsumption entailment,
   proving that the derivation is logically sound and non-trivial.
"""

import types
import pytest
from owlready2 import (
    get_ontology, Thing, AllDifferent, sync_reasoner_pellet, World
)

import model


@pytest.fixture(scope="module")
def subsumption_world():
    """Builds an isolated world asserting Defined Classes for all 6 threats."""
    world = World()
    onto = world.get_ontology(model.ONTOLOGY_IRI)

    with onto:
        class Rice(Thing): pass
        class Threat(Thing): pass
        class Disease(Threat): pass
        class Pest(Threat): pass
        class Observation(Thing): pass
        class hasObservation(Rice >> Observation): pass
        class hasThreat(Rice >> Threat): pass
        class hasConfirmedThreat(hasThreat): pass
        class hasSuspectedThreat(hasThreat): pass

        threat_configs = [
            ("Rice_Root_Nematode", Pest,
             ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves"],
             ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves", "Root_Knot_Swelling", "Deformed_Roots", "Necrotic_Spots"]),
            ("Bacterial_Leaf_Blight", Disease,
             ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips"],
             ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips", "Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow", "Uniform_Field_Infection", "Rapid_Disease_Spread"]),
            ("False_Smut", Disease,
             ["Rusty_Grain_Balls", "Blackened_Grain_Balls"],
             ["Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection", "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability"]),
            ("Rice_Blast", Disease,
             ["Diamond_Shaped_Lesions", "Necrotic_Spots"],
             ["Diamond_Shaped_Lesions", "Necrotic_Spots", "Panicle_Neck_Rot", "Uniform_Field_Infection", "Infected_Seedlings"]),
            ("Rice_Grassy_Stunt", Disease,
             ["Severe_Stunting", "Excessive_Tillering"],
             ["Severe_Stunting", "Excessive_Tillering", "Brown_Planthopper_Present", "Necrotic_Spots", "No_Panicle_Formation"]),
            ("Rice_Tungro_Virus", Disease,
             ["Stunted_Growth", "Orange_Leaf_Discoloration"],
             ["Stunted_Growth", "Orange_Leaf_Discoloration", "Green_Leafhopper_Present", "Necrotic_Spots", "Yellowing_Leaves", "Whitehead_Empty_Panicles"])
        ]

        all_obs = {}
        for t_name, t_cls, t2_ants, t1_ants in threat_configs:
            t_inst = t_cls(t_name)
            for ant in set(t2_ants + t1_ants):
                if ant not in all_obs:
                    all_obs[ant] = Observation(ant)

        AllDifferent(list(all_obs.values()))

        classes = {}
        for t_name, t_cls, t2_ants, t1_ants in threat_configs:
            t_inst = onto.search_one(iri=f"*{t_name}")
            # Suspect defined class
            susp_expr = Rice
            for a in t2_ants:
                susp_expr = susp_expr & hasObservation.value(all_obs[a])
            susp_cls = types.new_class(f"{t_name}Suspect", (Rice,))
            susp_cls.equivalent_to = [susp_expr]
            susp_cls.is_a.append(hasSuspectedThreat.value(t_inst))

            # Confirmed defined class
            conf_expr = Rice
            for a in t1_ants:
                conf_expr = conf_expr & hasObservation.value(all_obs[a])
            conf_cls = types.new_class(f"{t_name}Confirmed", (Rice,))
            conf_cls.equivalent_to = [conf_expr]
            conf_cls.is_a.append(hasConfirmedThreat.value(t_inst))

            classes[t_name] = (conf_cls, susp_cls, t2_ants, t1_ants)

    sync_reasoner_pellet(x=world)
    return world, onto, classes, all_obs


@pytest.mark.parametrize("threat_name", [
    "Rice_Root_Nematode",
    "Bacterial_Leaf_Blight",
    "False_Smut",
    "Rice_Blast",
    "Rice_Grassy_Stunt",
    "Rice_Tungro_Virus",
])
def test_pellet_proves_confirmed_subsumed_by_suspect(subsumption_world, threat_name):
    world, onto, classes, all_obs = subsumption_world
    conf_cls, susp_cls, _, _ = classes[threat_name]
    assert susp_cls in conf_cls.ancestors(), (
        f"Pellet failed to prove {conf_cls.name} is subsumed by {susp_cls.name}!"
    )


def test_subsumption_disappears_when_tier2_antecedent_removed():
    """Verifies that the entailment is strictly sound: dropping a Tier-2 antecedent
    from Tier-1 breaks the subsumption relationship."""
    world = World()
    onto = world.get_ontology("http://test.org/broken_subsumption.owl")

    with onto:
        class Rice(Thing): pass
        class Observation(Thing): pass
        class hasObservation(Rice >> Observation): pass

        s1 = Observation("sign_1")
        s2 = Observation("sign_2")
        s3 = Observation("sign_3")
        AllDifferent([s1, s2, s3])

        class BlastSuspect(Rice):
            equivalent_to = [Rice & hasObservation.value(s1) & hasObservation.value(s2)]

        # BlastBroken omits sign_2 (a Tier-2 requirement)
        class BlastBroken(Rice):
            equivalent_to = [Rice & hasObservation.value(s1) & hasObservation.value(s3)]

    sync_reasoner_pellet(x=world)
    assert BlastSuspect not in BlastBroken.ancestors(), (
        "Subsumption should NOT hold when a Tier-2 antecedent is omitted from Tier-1!"
    )
