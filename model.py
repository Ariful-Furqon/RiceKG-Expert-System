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


def predict_diseases(symptoms):
    """
    Infers rice pests and diseases using SWRL reasoning.

    Creates a temporary Rice individual, attaches observed symptoms,
    executes Pellet DL forward-chaining inference, extracts inferred
    hasPest/hasDisease properties, and cleans up all temporary entities.

    :param symptoms: List of symptom identifier strings (English).
    :return: List of diagnosed pest and disease names.
    """
    plant_id = f"RiceSample_{uuid.uuid4().hex[:8]}"
    new_plant = Rice(plant_id, namespace=onto)
    created_symptoms = []

    try:
        for symptom_name in symptoms:
            symptom_name = str(symptom_name).strip()
            if not symptom_name:
                continue
            
            symptom_obj = onto.search_one(iri=f"*{symptom_name}")
            if symptom_obj is None:
                symptom_obj = Symptom(symptom_name, namespace=onto)
                created_symptoms.append(symptom_obj)
            new_plant.hasSymptom.append(symptom_obj)

        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

        predicted_diagnoses = list(new_plant.hasPest) + list(new_plant.hasDisease)
        predicted_names = [d.name for d in predicted_diagnoses]
        return predicted_names
    finally:
        destroy_entity(new_plant)
        for sym in created_symptoms:
            try:
                destroy_entity(sym)
            except Exception:
                pass


# =========================================================================
# Explainable AI (XAI): Formal SWRL Rule Knowledge Representation
# =========================================================================

SWRL_RULES_METADATA = {
    "Grasshopper": {
        "tier1": {
            "rule_id": "SWRL-R01",
            "name": "Canonical Grasshopper Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant", "Broad_Leaf_Damage", "Severed_Panicles", "Leaf_Chewing_Damage"],
            "formula": "hasSymptom(?Rice, Brown_Nymphs) ∧ hasSymptom(?Rice, Yellow_Nymphs) ∧ hasSymptom(?Rice, Eggs_On_Plant) ∧ hasSymptom(?Rice, Broad_Leaf_Damage) ∧ hasSymptom(?Rice, Severed_Panicles) ∧ hasSymptom(?Rice, Leaf_Chewing_Damage) → hasPest(?Rice, Grasshopper)",
            "rationale": "Comprehensive detection of nymph stages, egg deposition, and foliar defoliation."
        },
        "tier2": {
            "rule_id": "SWRL-R11",
            "name": "Relaxed Grasshopper Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Severed_Panicles", "Leaf_Chewing_Damage"],
            "formula": "hasSymptom(?Rice, Severed_Panicles) ∧ hasSymptom(?Rice, Leaf_Chewing_Damage) → hasPest(?Rice, Grasshopper)",
            "rationale": "Sufficient mechanical chewing damage and severed panicle heads observed under partial field scouting."
        }
    },
    "Rice_Root_Nematode": {
        "tier1": {
            "rule_id": "SWRL-R02",
            "name": "Canonical Rice Root Nematode Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Hook_Like_Root_Swelling", "Root_Knot_Swelling", "Deformed_Roots", "Necrotic_Spots", "Yellowing_Leaves", "Stunted_Growth"],
            "formula": "hasSymptom(?Rice, Hook_Like_Root_Swelling) ∧ hasSymptom(?Rice, Root_Knot_Swelling) ∧ hasSymptom(?Rice, Deformed_Roots) ∧ hasSymptom(?Rice, Necrotic_Spots) ∧ hasSymptom(?Rice, Yellowing_Leaves) ∧ hasSymptom(?Rice, Stunted_Growth) → hasPest(?Rice, Rice_Root_Nematode)",
            "rationale": "Full root galling morphology, cortical necrosis, and secondary vegetative stunting."
        },
        "tier2": {
            "rule_id": "SWRL-R12",
            "name": "Relaxed Root Nematode Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Hook_Like_Root_Swelling", "Root_Knot_Swelling"],
            "formula": "hasSymptom(?Rice, Hook_Like_Root_Swelling) ∧ hasSymptom(?Rice, Root_Knot_Swelling) → hasPest(?Rice, Rice_Root_Nematode)",
            "rationale": "Characteristic hook-like terminal root galling pathognomonic for Hirschmanniella oryzae."
        }
    },
    "Rice_Stem_Borer": {
        "tier1": {
            "rule_id": "SWRL-R03",
            "name": "Canonical Rice Stem Borer Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Frass_In_Stem", "Bore_Holes_In_Stem", "Deadheart_Seedling", "Easily_Pulled_Tillers", "Whitehead_Empty_Panicles"],
            "formula": "hasSymptom(?Rice, Frass_In_Stem) ∧ hasSymptom(?Rice, Bore_Holes_In_Stem) ∧ hasSymptom(?Rice, Deadheart_Seedling) ∧ hasSymptom(?Rice, Easily_Pulled_Tillers) ∧ hasSymptom(?Rice, Whitehead_Empty_Panicles) → hasPest(?Rice, Rice_Stem_Borer)",
            "rationale": "Vegetative deadhearts and generative whiteheads accompanied by larval culm boring and frass."
        },
        "tier2": {
            "rule_id": "SWRL-R13",
            "name": "Relaxed Stem Borer Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Frass_In_Stem", "Bore_Holes_In_Stem"],
            "formula": "hasSymptom(?Rice, Frass_In_Stem) ∧ hasSymptom(?Rice, Bore_Holes_In_Stem) → hasPest(?Rice, Rice_Stem_Borer)",
            "rationale": "Direct morphological evidence of stem bore entrance holes and internal larval frass."
        }
    },
    "Rice_Bug": {
        "tier1": {
            "rule_id": "SWRL-R04",
            "name": "Canonical Rice Bug Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Leaf_Margin_Sap_Sucking", "Rotten_Panicles", "Random_Feeding_Pattern", "Localized_Leaf_Yellowing", "Empty_Grains"],
            "formula": "hasSymptom(?Rice, Nymphs_Present) ∧ hasSymptom(?Rice, Adult_Insects_Present) ∧ hasSymptom(?Rice, Leaf_Margin_Sap_Sucking) ∧ hasSymptom(?Rice, Rotten_Panicles) ∧ hasSymptom(?Rice, Random_Feeding_Pattern) ∧ hasSymptom(?Rice, Localized_Leaf_Yellowing) ∧ hasSymptom(?Rice, Empty_Grains) → hasPest(?Rice, Rice_Bug)",
            "rationale": "Simultaneous observation of feeding puncture marks, empty chalky grains, and active insect stages."
        },
        "tier2": {
            "rule_id": "SWRL-R14",
            "name": "Relaxed Rice Bug Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Empty_Grains"],
            "formula": "hasSymptom(?Rice, Nymphs_Present) ∧ hasSymptom(?Rice, Adult_Insects_Present) ∧ hasSymptom(?Rice, Empty_Grains) → hasPest(?Rice, Rice_Bug)",
            "rationale": "High population density of Leptocorisa oratorius active during grain filling stage causing empty grains."
        }
    },
    "Brown_Planthopper": {
        "tier1": {
            "rule_id": "SWRL-R05",
            "name": "Canonical Brown Planthopper Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Plant_Yellowing", "Hopperburn_Drying", "Circular_Hopperburn_Patches", "Blackened_Feeding_Punctures", "Empty_Grains"],
            "formula": "hasSymptom(?Rice, Nymphs_Present) ∧ hasSymptom(?Rice, Adult_Insects_Present) ∧ hasSymptom(?Rice, Plant_Yellowing) ∧ hasSymptom(?Rice, Hopperburn_Drying) ∧ hasSymptom(?Rice, Circular_Hopperburn_Patches) ∧ hasSymptom(?Rice, Blackened_Feeding_Punctures) ∧ hasSymptom(?Rice, Empty_Grains) → hasPest(?Rice, Brown_Planthopper)",
            "rationale": "Classic circular hopperburn dying patches and dense colonies on basal tillers."
        },
        "tier2": {
            "rule_id": "SWRL-R15",
            "name": "Relaxed Brown Planthopper Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Hopperburn_Drying", "Circular_Hopperburn_Patches"],
            "formula": "hasSymptom(?Rice, Hopperburn_Drying) ∧ hasSymptom(?Rice, Circular_Hopperburn_Patches) → hasPest(?Rice, Brown_Planthopper)",
            "rationale": "Rapid circular desiccation patches in field caused by intensive sap extraction."
        }
    },
    "Bacterial_Leaf_Blight": {
        "tier1": {
            "rule_id": "SWRL-R06",
            "name": "Canonical Bacterial Leaf Blight Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow", "Yellowing_Leaf_Tips", "Uniform_Field_Infection", "Rapid_Disease_Spread"],
            "formula": "hasSymptom(?Rice, Yellowing_Leaf_Veins) ∧ hasSymptom(?Rice, Leaf_Discoloration_Yellow) ∧ hasSymptom(?Rice, Yellowing_Leaf_Tips) ∧ hasSymptom(?Rice, Uniform_Field_Infection) ∧ hasSymptom(?Rice, Rapid_Disease_Spread) → hasDisease(?Rice, Bacterial_Leaf_Blight)",
            "rationale": "Systemic vascular yellowing along vein ridges with rapid epidemiological transmission across field."
        },
        "tier2": {
            "rule_id": "SWRL-R16",
            "name": "Relaxed Bacterial Leaf Blight Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Yellowing_Leaf_Veins", "Uniform_Field_Infection"],
            "formula": "hasSymptom(?Rice, Yellowing_Leaf_Veins) ∧ hasSymptom(?Rice, Uniform_Field_Infection) → hasDisease(?Rice, Bacterial_Leaf_Blight)",
            "rationale": "Diagnostic yellow vein discoloration with uniform field-level dispersion pattern."
        }
    },
    "False_Smut": {
        "tier1": {
            "rule_id": "SWRL-R07",
            "name": "Canonical False Smut Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection", "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability"],
            "formula": "hasSymptom(?Rice, Rusty_Grain_Balls) ∧ hasSymptom(?Rice, Blackened_Grain_Balls) ∧ hasSymptom(?Rice, Uniform_Field_Infection) ∧ hasSymptom(?Rice, Rainy_Season_Outbreak) ∧ hasSymptom(?Rice, Slight_Panicle_Infection) ∧ hasSymptom(?Rice, Milky_Stage_Vulnerability) → hasDisease(?Rice, False_Smut)",
            "rationale": "Transformation of individual spikelets into yellow-orange velvety spore balls turning greenish-black."
        },
        "tier2": {
            "rule_id": "SWRL-R17",
            "name": "Relaxed False Smut Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Rusty_Grain_Balls", "Blackened_Grain_Balls"],
            "formula": "hasSymptom(?Rice, Rusty_Grain_Balls) ∧ hasSymptom(?Rice, Blackened_Grain_Balls) → hasDisease(?Rice, False_Smut)",
            "rationale": "Presence of mature and immature chlamydospore smut balls replacing grain kernels."
        }
    },
    "Rice_Blast": {
        "tier1": {
            "rule_id": "SWRL-R08",
            "name": "Canonical Rice Blast Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions", "Uniform_Field_Infection", "Infected_Seedlings"],
            "formula": "hasSymptom(?Rice, Panicle_Neck_Rot) ∧ hasSymptom(?Rice, Diamond_Shaped_Lesions) ∧ hasSymptom(?Rice, Uniform_Field_Infection) ∧ hasSymptom(?Rice, Infected_Seedlings) → hasDisease(?Rice, Rice_Blast)",
            "rationale": "Elliptical spindle/diamond lesions with necrotic panicle neck rot caused by Magnaporthe oryzae."
        },
        "tier2": {
            "rule_id": "SWRL-R18",
            "name": "Relaxed Rice Blast Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions"],
            "formula": "hasSymptom(?Rice, Panicle_Neck_Rot) ∧ hasSymptom(?Rice, Diamond_Shaped_Lesions) → hasDisease(?Rice, Rice_Blast)",
            "rationale": "Key pathognomonic foliar spindle lesions and panicle node rot."
        }
    },
    "Rice_Grassy_Stunt": {
        "tier1": {
            "rule_id": "SWRL-R09",
            "name": "Canonical Rice Grassy Stunt Virus Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Brown_Planthopper_Present", "Necrotic_Spots", "Severe_Stunting", "No_Panicle_Formation"],
            "formula": "hasSymptom(?Rice, Brown_Planthopper_Present) ∧ hasSymptom(?Rice, Necrotic_Spots) ∧ hasSymptom(?Rice, Severe_Stunting) ∧ hasSymptom(?Rice, No_Panicle_Formation) → hasDisease(?Rice, Rice_Grassy_Stunt)",
            "rationale": "Excessive profuse tillering, severe dwarfing, heading suppression, and confirmed BPH vector presence."
        },
        "tier2": {
            "rule_id": "SWRL-R19",
            "name": "Relaxed Rice Grassy Stunt Virus Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Brown_Planthopper_Present", "Severe_Stunting"],
            "formula": "hasSymptom(?Rice, Brown_Planthopper_Present) ∧ hasSymptom(?Rice, Severe_Stunting) → hasDisease(?Rice, Rice_Grassy_Stunt)",
            "rationale": "Vector Nilaparvata lugens co-occurring with pronounced plant dwarfing."
        }
    },
    "Rice_Tungro_Virus": {
        "tier1": {
            "rule_id": "SWRL-R10",
            "name": "Canonical Rice Tungro Virus Diagnosis",
            "tier": "Tier 1: Canonical Pathognomonic",
            "tier_badge": "tier-canonical",
            "antecedents": ["Green_Leafhopper_Present", "Necrotic_Spots", "Yellowing_Leaves", "Whitehead_Empty_Panicles"],
            "formula": "hasSymptom(?Rice, Green_Leafhopper_Present) ∧ hasSymptom(?Rice, Necrotic_Spots) ∧ hasSymptom(?Rice, Yellowing_Leaves) ∧ hasSymptom(?Rice, Whitehead_Empty_Panicles) → hasDisease(?Rice, Rice_Tungro_Virus)",
            "rationale": "Foliar yellow-orange discoloration, delayed flowering, empty panicles, and active Nephotettix virescens."
        },
        "tier2": {
            "rule_id": "SWRL-R20",
            "name": "Relaxed Rice Tungro Virus Diagnosis",
            "tier": "Tier 2: Relaxed Composite (Partial Observation)",
            "tier_badge": "tier-relaxed",
            "antecedents": ["Green_Leafhopper_Present", "Yellowing_Leaves"],
            "formula": "hasSymptom(?Rice, Green_Leafhopper_Present) ∧ hasSymptom(?Rice, Yellowing_Leaves) → hasDisease(?Rice, Rice_Tungro_Virus)",
            "rationale": "Diagnostic yellowing of leaf blades combined with active green leafhopper transmission vector."
        }
    }
}


def explain_diagnoses(selected_symptoms, diagnosed_threats):
    """
    Generates explainable deductive proof traces for all inferred diagnoses.
    Identifies whether Tier 1 (canonical) or Tier 2 (relaxed) rule fired,
    and maps observed vs unobserved rule antecedents.

    :param selected_symptoms: List of user-selected symptom ID strings.
    :param diagnosed_threats: List of diagnosed threat key strings.
    :return: Dictionary mapping threat key to proof trace explanation.
    """
    selected_set = set(selected_symptoms)
    explanations = {}

    for threat_key in diagnosed_threats:
        meta = SWRL_RULES_METADATA.get(threat_key)
        if not meta:
            explanations[threat_key] = {
                "rule_id": "SWRL-GENERIC",
                "name": f"Deductive Rule for {threat_key.replace('_', ' ')}",
                "tier": "First-Order Logic Inference",
                "tier_badge": "tier-relaxed",
                "formula": f"hasSymptom(?Rice, ...) → hasThreat(?Rice, {threat_key})",
                "rationale": "Inferred via Pellet description logic tableau algorithm.",
                "antecedents_status": [{"symptom": s, "observed": True} for s in selected_symptoms]
            }
            continue

        # Check if Tier 1 (canonical) rule fully satisfied
        t1 = meta["tier1"]
        t2 = meta["tier2"]

        t1_satisfied = all(ant in selected_set for ant in t1["antecedents"])
        active_rule = t1 if t1_satisfied else t2

        # Build antecedent status list
        ant_status = []
        for ant in active_rule["antecedents"]:
            ant_status.append({
                "symptom": ant,
                "symptom_name": ant.replace("_", " "),
                "observed": ant in selected_set
            })

        explanations[threat_key] = {
            "rule_id": active_rule["rule_id"],
            "name": active_rule["name"],
            "tier": active_rule["tier"],
            "tier_badge": active_rule["tier_badge"],
            "formula": active_rule["formula"],
            "rationale": active_rule["rationale"],
            "antecedents": active_rule["antecedents"],
            "antecedents_status": ant_status,
            "rule_level": "Tier 1 (Canonical)" if t1_satisfied else "Tier 2 (Relaxed Composite)"
        }

    return explanations


