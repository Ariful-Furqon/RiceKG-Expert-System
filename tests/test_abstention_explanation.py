# Tests for model.explain_abstention (why no diagnosis was reached).

from ricekg import model


def test_nearest_rule_lists_matched_and_missing():
    # One missing sign for both R12 (nematode) and R20 (tungro); R12 has higher coverage.
    ab = model.explain_abstention(["Stunted_Growth", "Yellowing_Leaves"])
    top = ab["nearest_rules"][0]
    assert top["threat"] == "Rice_Root_Nematode" and top["rule_id"] == "SWRL-R12"
    assert top["matched_symptoms"] == ["Stunted_Growth", "Yellowing_Leaves"]
    assert top["missing_symptoms"] == ["Hook_Like_Root_Swelling"]


def test_one_entry_per_threat_and_k_respected():
    ab = model.explain_abstention(["Necrotic_Spots", "Stunted_Growth", "Yellowing_Leaves"], k=2)
    threats = [r["threat"] for r in ab["nearest_rules"]]
    assert len(threats) == len(set(threats)) <= 2


def test_fewest_missing_first():
    ab = model.explain_abstention(["Water_Soaked_Lesions", "Necrotic_Spots"], k=3)
    missing = [len(r["missing_symptoms"]) for r in ab["nearest_rules"]]
    assert missing == sorted(missing)


def test_unused_observations_reported():
    ab = model.explain_abstention(["Leaf_Mottling", "Bacterial_Ooze"])
    assert ab["nearest_rules"] == []
    assert ab["unused_observations"] == ["Bacterial_Ooze", "Leaf_Mottling"]


def test_empty_input():
    assert model.explain_abstention([]) == {"nearest_rules": [], "unused_observations": []}
