import pytest
from ricekg import model

def get_rule_antecedents(rule_id: str) -> list:
    # Helper to dynamically fetch antecedents from model.RULE_REGISTRY.
    for r in model.RULE_REGISTRY:
        if r["id"] == rule_id:
            return list(r["antecedents"])
    raise KeyError(f"Rule {rule_id} not found in RULE_REGISTRY")


class TestCanonicalDiagnoses:
    # Tests that canonical (Tier 1) full-symptom profiles produce correct diagnoses.

    def test_rice_root_nematode(self):
        symptoms = get_rule_antecedents("SWRL-R02")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Root_Nematode" in result

    def test_bacterial_leaf_blight(self):
        symptoms = get_rule_antecedents("SWRL-R06")
        result = model.predict_diseases_flat(symptoms)
        assert "Bacterial_Leaf_Blight" in result

    def test_false_smut(self):
        symptoms = get_rule_antecedents("SWRL-R07")
        result = model.predict_diseases_flat(symptoms)
        assert "False_Smut" in result

    def test_rice_blast(self):
        symptoms = get_rule_antecedents("SWRL-R08")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Blast" in result

    def test_rice_grassy_stunt(self):
        symptoms = get_rule_antecedents("SWRL-R09")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Grassy_Stunt" in result

    def test_rice_tungro_virus(self):
        symptoms = get_rule_antecedents("SWRL-R10")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Tungro_Virus" in result


class TestRelaxedRules:
    # Tests that Tier 2 relaxed (partial-symptom) rules also fire correctly.

    def test_rice_root_nematode_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R12")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Root_Nematode" in result

    def test_bacterial_leaf_blight_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R16")
        result = model.predict_diseases_flat(symptoms)
        assert "Bacterial_Leaf_Blight" in result

    def test_false_smut_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R17")
        result = model.predict_diseases_flat(symptoms)
        assert "False_Smut" in result

    def test_rice_blast_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R18")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Blast" in result

    def test_rice_grassy_stunt_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R19")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Grassy_Stunt" in result

    def test_tungro_virus_relaxed(self):
        symptoms = get_rule_antecedents("SWRL-R20")
        result = model.predict_diseases_flat(symptoms)
        assert "Rice_Tungro_Virus" in result


class TestEdgeCases:
    # Tests for edge cases and boundary conditions.

    def test_empty_symptoms(self):
        result = model.predict_diseases_flat([])
        assert result == []

    def test_unknown_symptom_graceful(self):
        result = model.predict_diseases_flat(["Nonexistent_Symptom_XYZ"])
        assert isinstance(result, list)

    def test_whitespace_symptom_ignored(self):
        result = model.predict_diseases_flat(["", "  ", "Rusty_Grain_Balls", "Blackened_Grain_Balls"])
        assert "False_Smut" in result