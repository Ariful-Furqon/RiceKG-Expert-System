import pytest
from ricekg import model


def test_purely_insect_damage_yields_out_of_scope_response():
    # 5-B acceptance test: A purely insect-damage symptom set yields the
    # explicit out-of-scope response rather than a silent No_Diagnosis.
    # Former Grasshopper relaxed symptoms
    symptoms = ["Severed_Panicles", "Leaf_Chewing_Damage"]
    results = model.predict_diseases(symptoms)

    assert len(results) == 1, "Expected exactly 1 out-of-scope response"
    res = results[0]
    assert res["grade"] == "out_of_scope"
    assert res["threat"] == model.INSECT_OUT_OF_SCOPE_TARGET
    assert res["threat"] not in model.ALL_DIAGNOSES, "Insect response must NOT be an in-scope diagnosis"
    assert model.INSECT_OUT_OF_SCOPE_RESPONSE in res["message"]
    assert "Severed_Panicles" in res["matched_symptoms"]
    assert "Leaf_Chewing_Damage" in res["matched_symptoms"]


def test_stem_borer_damage_yields_out_of_scope_response():
    # Stem borer symptoms (culm frass and bore holes) return out-of-scope.
    symptoms = ["Frass_In_Stem", "Bore_Holes_In_Stem"]
    results = model.predict_diseases(symptoms)

    assert len(results) == 1
    assert results[0]["grade"] == "out_of_scope"
    assert results[0]["threat"] == model.INSECT_OUT_OF_SCOPE_TARGET


def test_vector_sighting_with_disease_yields_disease_diagnosis():
    # Planthopper/leafhopper sightings remain valid antecedents for viral diseases.
    # Rice Grassy Stunt canonical antecedents include Brown_Planthopper_Present
    r09_ants = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R09")["antecedents"]
    results = model.predict_diseases(r09_ants)

    threats = [r["threat"] for r in results]
    assert "Rice_Grassy_Stunt" in threats
    assert model.INSECT_OUT_OF_SCOPE_TARGET not in threats


def test_nematode_remains_in_scope():
    # Rice_Root_Nematode is retained as an in-scope plant-parasitic threat.
    r02_ants = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R02")["antecedents"]
    results = model.predict_diseases(r02_ants)

    threats = [r["threat"] for r in results]
    assert "Rice_Root_Nematode" in threats
    assert "Rice_Root_Nematode" in model.ALL_DIAGNOSES
    assert "Rice_Root_Nematode" in model.PESTS


def test_specific_signs_are_a_subset_of_the_insect_vocabulary():
    assert set(model.INSECT_SPECIFIC_SIGNS) <= set(model.INSECT_DAMAGE_SIGNS)
    used = {a for r in model.RULE_REGISTRY for a in r["antecedents"]}
    assert not set(model.INSECT_SPECIFIC_SIGNS) & used, "An insect-specific sign must not be an in-scope antecedent"


@pytest.mark.parametrize("symptoms", [
    ["Plant_Yellowing"],                                   # nitrogen deficiency
    ["Plant_Yellowing", "Yellowing_Leaf_Tips"],            # abiotic chlorosis demo scenario
    ["Empty_Grains", "Grain_Discoloration"],               # FIELD_18/22 Burkholderia controls
    ["Necrotic_Spots", "Empty_Grains", "Stem_Rot_Lesions"],  # FIELD_02 Rice_Blast
    ["Plant_Yellowing", "Yellowing_Leaves", "Severe_Stunting", "Stunted_Growth"],  # FIELD_51 Tungro
    ["Plant_Yellowing", "Empty_Grains", "Rotten_Panicles", "Deadheart_Seedling"],  # non-specific only
])
def test_non_specific_signs_never_trigger_out_of_scope(symptoms):
    # Signs shared with pathogens or abiotic stress are not evidence of insect damage.
    threats = [r["threat"] for r in model.predict_diseases(symptoms)]
    assert model.INSECT_OUT_OF_SCOPE_TARGET not in threats


@pytest.mark.parametrize("symptom", ["Severed_Panicles", "Frass_In_Stem"])
def test_single_specific_sign_stays_no_diagnosis(symptom):
    # The verification suite's single-sign negative controls must remain No_Diagnosis.
    assert model.predict_diseases([symptom]) == []


def test_empty_symptoms_yields_silent_no_diagnosis():
    # With no symptoms observed, no out-of-scope response should be triggered.
    results = model.predict_diseases([])
    assert results == []

