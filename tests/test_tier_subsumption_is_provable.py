import copy

import pytest
from owlready2 import sync_reasoner_pellet

from ricekg import model


def _classify(onto):
    sync_reasoner_pellet(x=onto.world)
    return onto


@pytest.fixture(scope="module")
def production_onto():
    return _classify(model.build_ontology())


@pytest.mark.parametrize("threat_name", model.ALL_DIAGNOSES)
def test_pellet_proves_confirmed_subsumed_by_suspect(production_onto, threat_name):
    conf_cls = getattr(production_onto, f"{threat_name}Confirmed")
    susp_cls = getattr(production_onto, f"{threat_name}Suspect")
    assert susp_cls in conf_cls.ancestors(), (
        f"Pellet failed to prove {conf_cls.name} ⊑ {susp_cls.name}"
    )
    assert conf_cls not in susp_cls.ancestors(), (
        f"{susp_cls.name} ⊑ {conf_cls.name} would make the two tiers equivalent"
    )


@pytest.mark.parametrize("threat_name", model.ALL_DIAGNOSES)
def test_subsumption_disappears_when_tier2_antecedent_removed(monkeypatch, threat_name):
    metadata = copy.deepcopy(model.SWRL_RULES_METADATA)
    tier1 = metadata[threat_name]["tier1"]["antecedents"]
    dropped = {rule["antecedents"][0] for rule in metadata[threat_name]["tier2_rules"]}
    assert dropped <= set(tier1), "precondition: Tier-2 antecedents are contained in Tier-1"
    metadata[threat_name]["tier1"]["antecedents"] = [a for a in tier1 if a not in dropped]
    monkeypatch.setattr(model, "SWRL_RULES_METADATA", metadata)

    onto = _classify(model.build_ontology())

    broken_conf = getattr(onto, f"{threat_name}Confirmed")
    broken_susp = getattr(onto, f"{threat_name}Suspect")
    assert broken_susp not in broken_conf.ancestors(), (
        f"{threat_name}: subsumption must not hold once {dropped} is removed from Tier 1"
    )
    for other in model.ALL_DIAGNOSES:
        if other != threat_name:
            assert getattr(onto, f"{other}Suspect") in getattr(onto, f"{other}Confirmed").ancestors()
