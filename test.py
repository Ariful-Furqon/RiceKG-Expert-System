"""
Automated Test Suite for RiceKG Diagnostic Expert System.

Verifies SWRL rule inference correctness for all 10 target biotic threats
using the Pellet DL reasoner via owlready2.

Usage:
    python -m pytest test.py -v
"""

import pytest
import model


class TestCanonicalDiagnoses:
    """Tests that canonical (Tier 1) full-symptom profiles produce correct diagnoses."""

    def test_grasshopper(self):
        symptoms = ["Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant",
                     "Broad_Leaf_Damage", "Severed_Panicles", "Leaf_Chewing_Damage"]
        result = model.predict_diseases(symptoms)
        assert "Grasshopper" in result

    def test_rice_root_nematode(self):
        symptoms = ["Hook_Like_Root_Swelling", "Root_Knot_Swelling", "Deformed_Roots",
                     "Necrotic_Spots", "Yellowing_Leaves", "Stunted_Growth"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Root_Nematode" in result

    def test_rice_stem_borer(self):
        symptoms = ["Frass_In_Stem", "Bore_Holes_In_Stem", "Deadheart_Seedling",
                     "Easily_Pulled_Tillers", "Whitehead_Empty_Panicles"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Stem_Borer" in result

    def test_rice_bug(self):
        symptoms = ["Nymphs_Present", "Adult_Insects_Present", "Leaf_Margin_Sap_Sucking",
                     "Rotten_Panicles", "Random_Feeding_Pattern",
                     "Localized_Leaf_Yellowing", "Empty_Grains"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Bug" in result

    def test_brown_planthopper(self):
        symptoms = ["Nymphs_Present", "Adult_Insects_Present", "Plant_Yellowing",
                     "Hopperburn_Drying", "Circular_Hopperburn_Patches",
                     "Blackened_Feeding_Punctures", "Empty_Grains"]
        result = model.predict_diseases(symptoms)
        assert "Brown_Planthopper" in result

    def test_bacterial_leaf_blight(self):
        symptoms = ["Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow",
                     "Yellowing_Leaf_Tips", "Uniform_Field_Infection",
                     "Rapid_Disease_Spread"]
        result = model.predict_diseases(symptoms)
        assert "Bacterial_Leaf_Blight" in result

    def test_false_smut(self):
        symptoms = ["Rusty_Grain_Balls", "Blackened_Grain_Balls",
                     "Uniform_Field_Infection", "Rainy_Season_Outbreak",
                     "Slight_Panicle_Infection", "Milky_Stage_Vulnerability"]
        result = model.predict_diseases(symptoms)
        assert "False_Smut" in result

    def test_rice_blast(self):
        symptoms = ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions",
                     "Uniform_Field_Infection", "Infected_Seedlings"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Blast" in result

    def test_rice_grassy_stunt(self):
        symptoms = ["Brown_Planthopper_Present", "Necrotic_Spots",
                     "Severe_Stunting", "No_Panicle_Formation"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Grassy_Stunt" in result

    def test_rice_tungro_virus(self):
        symptoms = ["Green_Leafhopper_Present", "Necrotic_Spots",
                     "Yellowing_Leaves", "Whitehead_Empty_Panicles"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Tungro_Virus" in result


class TestRelaxedRules:
    """Tests that Tier 2 relaxed (partial-symptom) rules also fire correctly."""

    def test_grasshopper_relaxed(self):
        symptoms = ["Severed_Panicles", "Leaf_Chewing_Damage"]
        result = model.predict_diseases(symptoms)
        assert "Grasshopper" in result

    def test_stem_borer_relaxed(self):
        symptoms = ["Frass_In_Stem", "Bore_Holes_In_Stem"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Stem_Borer" in result

    def test_bacterial_leaf_blight_relaxed(self):
        symptoms = ["Yellowing_Leaf_Veins", "Uniform_Field_Infection"]
        result = model.predict_diseases(symptoms)
        assert "Bacterial_Leaf_Blight" in result

    def test_rice_blast_relaxed(self):
        symptoms = ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Blast" in result

    def test_tungro_virus_relaxed(self):
        symptoms = ["Green_Leafhopper_Present", "Yellowing_Leaves"]
        result = model.predict_diseases(symptoms)
        assert "Rice_Tungro_Virus" in result


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_symptoms(self):
        result = model.predict_diseases([])
        assert result == []

    def test_unknown_symptom_graceful(self):
        result = model.predict_diseases(["Nonexistent_Symptom_XYZ"])
        assert isinstance(result, list)

    def test_whitespace_symptom_ignored(self):
        result = model.predict_diseases(["", "  ", "Frass_In_Stem", "Bore_Holes_In_Stem"])
        assert "Rice_Stem_Borer" in result