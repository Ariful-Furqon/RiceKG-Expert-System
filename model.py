"""
Rice Pest and Disease Diagnostic Model based on Ontology and SWRL Rules.
"""

import os
import uuid
from owlready2 import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY_PATH = os.path.join(BASE_DIR, "rice_ontology.owl")

# Initialize Ontology
onto = get_ontology("http://www.semanticweb.org/ontologies/rice_pest_disease.owl")

with onto:
    # Classes
    class Rice(Thing):
        namespace = onto

    class Symptom(Thing):
        namespace = onto

    class Disease(Thing):
        namespace = onto

    class Pest(Thing):
        namespace = onto

    class ControlTreatment(Thing):
        namespace = onto

    # Object Properties
    class hasSymptom(Rice >> Symptom):
        domain = [Rice]
        range = [Symptom]

    class hasDisease(Rice >> Disease):
        domain = [Rice]
        range = [Disease]

    class hasPest(Rice >> Pest):
        domain = [Rice]
        range = [Pest]

# Individual Symptoms Definition
symptoms_map = {
    # Grasshopper symptoms
    "Brown_Nymphs": Symptom("Brown_Nymphs", namespace=onto),
    "Yellow_Nymphs": Symptom("Yellow_Nymphs", namespace=onto),
    "Eggs_On_Plant": Symptom("Eggs_On_Plant", namespace=onto),
    "Broad_Leaf_Damage": Symptom("Broad_Leaf_Damage", namespace=onto),
    "Severed_Panicles": Symptom("Severed_Panicles", namespace=onto),
    "Leaf_Chewing_Damage": Symptom("Leaf_Chewing_Damage", namespace=onto),

    # Rice Root Nematode symptoms
    "Hook_Like_Root_Swelling": Symptom("Hook_Like_Root_Swelling", namespace=onto),
    "Root_Knot_Swelling": Symptom("Root_Knot_Swelling", namespace=onto),
    "Deformed_Roots": Symptom("Deformed_Roots", namespace=onto),
    "Necrotic_Spots": Symptom("Necrotic_Spots", namespace=onto),
    "Yellowing_Leaves": Symptom("Yellowing_Leaves", namespace=onto),
    "Stunted_Growth": Symptom("Stunted_Growth", namespace=onto),

    # Rice Stem Borer symptoms
    "Frass_In_Stem": Symptom("Frass_In_Stem", namespace=onto),
    "Bore_Holes_In_Stem": Symptom("Bore_Holes_In_Stem", namespace=onto),
    "Deadheart_Seedling": Symptom("Deadheart_Seedling", namespace=onto),
    "Easily_Pulled_Tillers": Symptom("Easily_Pulled_Tillers", namespace=onto),
    "Whitehead_Empty_Panicles": Symptom("Whitehead_Empty_Panicles", namespace=onto),

    # Rice Bug symptoms
    "Nymphs_Present": Symptom("Nymphs_Present", namespace=onto),
    "Adult_Insects_Present": Symptom("Adult_Insects_Present", namespace=onto),
    "Leaf_Margin_Sap_Sucking": Symptom("Leaf_Margin_Sap_Sucking", namespace=onto),
    "Rotten_Panicles": Symptom("Rotten_Panicles", namespace=onto),
    "Random_Feeding_Pattern": Symptom("Random_Feeding_Pattern", namespace=onto),
    "Localized_Leaf_Yellowing": Symptom("Localized_Leaf_Yellowing", namespace=onto),
    "Empty_Grains": Symptom("Empty_Grains", namespace=onto),

    # Brown Planthopper symptoms
    "Plant_Yellowing": Symptom("Plant_Yellowing", namespace=onto),
    "Hopperburn_Drying": Symptom("Hopperburn_Drying", namespace=onto),
    "Circular_Hopperburn_Patches": Symptom("Circular_Hopperburn_Patches", namespace=onto),
    "Blackened_Feeding_Punctures": Symptom("Blackened_Feeding_Punctures", namespace=onto),

    # Bacterial Leaf Blight symptoms
    "Yellowing_Leaf_Veins": Symptom("Yellowing_Leaf_Veins", namespace=onto),
    "Leaf_Discoloration_Yellow": Symptom("Leaf_Discoloration_Yellow", namespace=onto),
    "Yellowing_Leaf_Tips": Symptom("Yellowing_Leaf_Tips", namespace=onto),
    "Rapid_Disease_Spread": Symptom("Rapid_Disease_Spread", namespace=onto),

    # False Smut symptoms
    "Rusty_Grain_Balls": Symptom("Rusty_Grain_Balls", namespace=onto),
    "Blackened_Grain_Balls": Symptom("Blackened_Grain_Balls", namespace=onto),
    "Rainy_Season_Outbreak": Symptom("Rainy_Season_Outbreak", namespace=onto),
    "Uniform_Field_Infection": Symptom("Uniform_Field_Infection", namespace=onto),
    "Slight_Panicle_Infection": Symptom("Slight_Panicle_Infection", namespace=onto),
    "Milky_Stage_Vulnerability": Symptom("Milky_Stage_Vulnerability", namespace=onto),

    # Rice Blast symptoms
    "Panicle_Neck_Rot": Symptom("Panicle_Neck_Rot", namespace=onto),
    "Diamond_Shaped_Lesions": Symptom("Diamond_Shaped_Lesions", namespace=onto),
    "Infected_Seedlings": Symptom("Infected_Seedlings", namespace=onto),

    # Rice Grassy Stunt symptoms
    "Brown_Planthopper_Present": Symptom("Brown_Planthopper_Present", namespace=onto),
    "Severe_Stunting": Symptom("Severe_Stunting", namespace=onto),
    "No_Panicle_Formation": Symptom("No_Panicle_Formation", namespace=onto),

    # Rice Tungro Virus symptoms
    "Green_Leafhopper_Present": Symptom("Green_Leafhopper_Present", namespace=onto),
}

# Individual Pests and Diseases Definition
Grasshopper = Pest("Grasshopper", namespace=onto)
Rice_Root_Nematode = Pest("Rice_Root_Nematode", namespace=onto)
Rice_Stem_Borer = Pest("Rice_Stem_Borer", namespace=onto)
Rice_Bug = Pest("Rice_Bug", namespace=onto)
Brown_Planthopper = Pest("Brown_Planthopper", namespace=onto)

Bacterial_Leaf_Blight = Disease("Bacterial_Leaf_Blight", namespace=onto)
False_Smut = Disease("False_Smut", namespace=onto)
Rice_Blast = Disease("Rice_Blast", namespace=onto)
Rice_Grassy_Stunt = Disease("Rice_Grassy_Stunt", namespace=onto)
Rice_Tungro_Virus = Disease("Rice_Tungro_Virus", namespace=onto)

# Define SWRL Rules
with onto:
    # Rule 1 & 11: Grasshopper
    rule1 = Imp()
    rule1.set_as_rule("""hasSymptom(?Rice, Brown_Nymphs) ^ hasSymptom(?Rice, Yellow_Nymphs) ^ hasSymptom(?Rice, Eggs_On_Plant) ^ hasSymptom(?Rice, Broad_Leaf_Damage) ^ hasSymptom(?Rice, Severed_Panicles) ^ hasSymptom(?Rice, Leaf_Chewing_Damage) -> hasPest(?Rice, Grasshopper)""")

    rule2 = Imp()
    rule2.set_as_rule("""hasSymptom(?Rice, Hook_Like_Root_Swelling) ^ hasSymptom(?Rice, Root_Knot_Swelling) ^ hasSymptom(?Rice, Deformed_Roots) ^ hasSymptom(?Rice, Necrotic_Spots) ^ hasSymptom(?Rice, Yellowing_Leaves) ^ hasSymptom(?Rice, Stunted_Growth) -> hasPest(?Rice, Rice_Root_Nematode)""")

    rule3 = Imp()
    rule3.set_as_rule("""hasSymptom(?Rice, Frass_In_Stem) ^ hasSymptom(?Rice, Bore_Holes_In_Stem) ^ hasSymptom(?Rice, Deadheart_Seedling) ^ hasSymptom(?Rice, Easily_Pulled_Tillers) ^ hasSymptom(?Rice, Whitehead_Empty_Panicles) -> hasPest(?Rice, Rice_Stem_Borer)""")

    rule4 = Imp()
    rule4.set_as_rule("""hasSymptom(?Rice, Nymphs_Present) ^ hasSymptom(?Rice, Adult_Insects_Present) ^ hasSymptom(?Rice, Leaf_Margin_Sap_Sucking) ^ hasSymptom(?Rice, Rotten_Panicles) ^ hasSymptom(?Rice, Random_Feeding_Pattern) ^ hasSymptom(?Rice, Localized_Leaf_Yellowing) ^ hasSymptom(?Rice, Empty_Grains) -> hasPest(?Rice, Rice_Bug)""")

    rule5 = Imp()
    rule5.set_as_rule("""hasSymptom(?Rice, Nymphs_Present) ^ hasSymptom(?Rice, Adult_Insects_Present) ^ hasSymptom(?Rice, Plant_Yellowing) ^ hasSymptom(?Rice, Hopperburn_Drying) ^ hasSymptom(?Rice, Circular_Hopperburn_Patches) ^ hasSymptom(?Rice, Blackened_Feeding_Punctures) ^ hasSymptom(?Rice, Empty_Grains) -> hasPest(?Rice, Brown_Planthopper)""")

    rule6 = Imp()
    rule6.set_as_rule("""hasSymptom(?Rice, Yellowing_Leaf_Veins) ^ hasSymptom(?Rice, Leaf_Discoloration_Yellow) ^ hasSymptom(?Rice, Yellowing_Leaf_Tips) ^ hasSymptom(?Rice, Uniform_Field_Infection) ^ hasSymptom(?Rice, Rapid_Disease_Spread) -> hasDisease(?Rice, Bacterial_Leaf_Blight)""")

    rule7 = Imp()
    rule7.set_as_rule("""hasSymptom(?Rice, Rusty_Grain_Balls) ^ hasSymptom(?Rice, Blackened_Grain_Balls) ^ hasSymptom(?Rice, Uniform_Field_Infection) ^ hasSymptom(?Rice, Rainy_Season_Outbreak) ^ hasSymptom(?Rice, Slight_Panicle_Infection) ^ hasSymptom(?Rice, Milky_Stage_Vulnerability) -> hasDisease(?Rice, False_Smut)""")

    rule8 = Imp()
    rule8.set_as_rule("""hasSymptom(?Rice, Panicle_Neck_Rot) ^ hasSymptom(?Rice, Diamond_Shaped_Lesions) ^ hasSymptom(?Rice, Uniform_Field_Infection) ^ hasSymptom(?Rice, Infected_Seedlings) -> hasDisease(?Rice, Rice_Blast)""")

    rule9 = Imp()
    rule9.set_as_rule("""hasSymptom(?Rice, Brown_Planthopper_Present) ^ hasSymptom(?Rice, Necrotic_Spots) ^ hasSymptom(?Rice, Severe_Stunting) ^ hasSymptom(?Rice, No_Panicle_Formation) -> hasDisease(?Rice, Rice_Grassy_Stunt)""")

    rule10 = Imp()
    rule10.set_as_rule("""hasSymptom(?Rice, Green_Leafhopper_Present) ^ hasSymptom(?Rice, Necrotic_Spots) ^ hasSymptom(?Rice, Yellowing_Leaves) ^ hasSymptom(?Rice, Whitehead_Empty_Panicles) -> hasDisease(?Rice, Rice_Tungro_Virus)""")

    # Relaxed / Partial Rules
    rule11 = Imp()
    rule11.set_as_rule("""hasSymptom(?Rice, Severed_Panicles) ^ hasSymptom(?Rice, Leaf_Chewing_Damage) -> hasPest(?Rice, Grasshopper)""")

    rule12 = Imp()
    rule12.set_as_rule("""hasSymptom(?Rice, Hook_Like_Root_Swelling) ^ hasSymptom(?Rice, Root_Knot_Swelling) -> hasPest(?Rice, Rice_Root_Nematode)""")

    rule13 = Imp()
    rule13.set_as_rule("""hasSymptom(?Rice, Frass_In_Stem) ^ hasSymptom(?Rice, Bore_Holes_In_Stem) -> hasPest(?Rice, Rice_Stem_Borer)""")

    rule14 = Imp()
    rule14.set_as_rule("""hasSymptom(?Rice, Nymphs_Present) ^ hasSymptom(?Rice, Adult_Insects_Present) ^ hasSymptom(?Rice, Empty_Grains) -> hasPest(?Rice, Rice_Bug)""")

    rule15 = Imp()
    rule15.set_as_rule("""hasSymptom(?Rice, Hopperburn_Drying) ^ hasSymptom(?Rice, Circular_Hopperburn_Patches) -> hasPest(?Rice, Brown_Planthopper)""")

    rule16 = Imp()
    rule16.set_as_rule("""hasSymptom(?Rice, Yellowing_Leaf_Veins) ^ hasSymptom(?Rice, Uniform_Field_Infection) -> hasDisease(?Rice, Bacterial_Leaf_Blight)""")

    rule17 = Imp()
    rule17.set_as_rule("""hasSymptom(?Rice, Rusty_Grain_Balls) ^ hasSymptom(?Rice, Blackened_Grain_Balls) -> hasDisease(?Rice, False_Smut)""")

    rule18 = Imp()
    rule18.set_as_rule("""hasSymptom(?Rice, Panicle_Neck_Rot) ^ hasSymptom(?Rice, Diamond_Shaped_Lesions) -> hasDisease(?Rice, Rice_Blast)""")

    rule19 = Imp()
    rule19.set_as_rule("""hasSymptom(?Rice, Brown_Planthopper_Present) ^ hasSymptom(?Rice, Severe_Stunting) -> hasDisease(?Rice, Rice_Grassy_Stunt)""")

    rule20 = Imp()
    rule20.set_as_rule("""hasSymptom(?Rice, Green_Leafhopper_Present) ^ hasSymptom(?Rice, Yellowing_Leaves) -> hasDisease(?Rice, Rice_Tungro_Virus)""")


# Save English ontology file
onto.save(file=ONTOLOGY_PATH, format="rdfxml")


def predict_diseases(symptoms):
    """
    Infers rice pests and diseases using SWRL reasoning.
    :param symptoms: List of symptom identifier strings (English).
    :return: List of diagnosed pest and disease names.
    """
    plant_id = f"RiceSample_{uuid.uuid4().hex[:8]}"
    new_plant = Rice(plant_id, namespace=onto)

    try:
        for symptom_name in symptoms:
            symptom_name = str(symptom_name).strip()
            if not symptom_name:
                continue
            
            symptom_obj = onto.search_one(iri=f"*{symptom_name}")
            if symptom_obj is None:
                symptom_obj = Symptom(symptom_name, namespace=onto)
            new_plant.hasSymptom.append(symptom_obj)

        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

        predicted_diagnoses = list(new_plant.hasPest) + list(new_plant.hasDisease)
        predicted_names = [d.name for d in predicted_diagnoses]
        return predicted_names
    finally:
        destroy_entity(new_plant)
