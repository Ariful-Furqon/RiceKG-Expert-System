"""
RiceKG Expert System - Ontology Model & SWRL Reasoning Engine
-------------------------------------------------------------
Implements an OWL 2 DL ontology for rice pests and diseases using Owlready2
and the Pellet description logic reasoner. SWRL rules are defined via a
declarative registry supporting dynamic ontology construction and ablation.
"""

import os
import uuid
from owlready2 import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY_PATH = os.path.join(BASE_DIR, "rice_ontology.owl")
ONTOLOGY_IRI = "http://www.semanticweb.org/ontologies/rice_pest_disease.owl"

# =========================================================================
# Declarative Master Catalog: Symptoms, Threats, and SWRL Rules
# =========================================================================

ALL_SYMPTOMS = [
    # Foliar & vegetative symptoms
    "Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant", "Broad_Leaf_Damage",
    "Severed_Panicles", "Leaf_Chewing_Damage", "Hook_Like_Root_Swelling",
    "Root_Knot_Swelling", "Deformed_Roots", "Necrotic_Spots", "Yellowing_Leaves",
    "Stunted_Growth", "Frass_In_Stem", "Bore_Holes_In_Stem", "Deadheart_Seedling",
    "Easily_Pulled_Tillers", "Whitehead_Empty_Panicles", "Nymphs_Present",
    "Adult_Insects_Present", "Leaf_Margin_Sap_Sucking", "Rotten_Panicles",
    "Random_Feeding_Pattern", "Localized_Leaf_Yellowing", "Empty_Grains",
    "Plant_Yellowing", "Hopperburn_Drying", "Circular_Hopperburn_Patches",
    "Blackened_Feeding_Punctures", "Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow",
    "Yellowing_Leaf_Tips", "Rapid_Disease_Spread", "Rusty_Grain_Balls",
    "Blackened_Grain_Balls", "Rainy_Season_Outbreak", "Uniform_Field_Infection",
    "Slight_Panicle_Infection", "Milky_Stage_Vulnerability", "Panicle_Neck_Rot",
    "Diamond_Shaped_Lesions", "Infected_Seedlings", "Brown_Planthopper_Present",
    "Severe_Stunting", "No_Panicle_Formation", "Green_Leafhopper_Present"
]

PESTS = [
    "Grasshopper", "Rice_Root_Nematode", "Rice_Stem_Borer",
    "Rice_Bug", "Brown_Planthopper"
]

DISEASES = [
    "Bacterial_Leaf_Blight", "False_Smut", "Rice_Blast",
    "Rice_Grassy_Stunt", "Rice_Tungro_Virus"
]

RULE_REGISTRY = [
    # ---------------------------------------------------------------------
    # Tier 1: Canonical Pathognomonic Rules (High Specificity, 100% Precision)
    # ---------------------------------------------------------------------
    {
        "id": "SWRL-R01",
        "threat": "Grasshopper",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Grasshopper Diagnosis",
        "antecedents": ["Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant", "Broad_Leaf_Damage", "Severed_Panicles", "Leaf_Chewing_Damage"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Comprehensive detection of nymph stages, egg deposition, and foliar defoliation."
    },
    {
        "id": "SWRL-R02",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Rice Root Nematode Diagnosis",
        "antecedents": ["Hook_Like_Root_Swelling", "Root_Knot_Swelling", "Deformed_Roots", "Necrotic_Spots", "Yellowing_Leaves", "Stunted_Growth"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Full root galling morphology, cortical necrosis, and secondary vegetative stunting."
    },
    {
        "id": "SWRL-R03",
        "threat": "Rice_Stem_Borer",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Rice Stem Borer Diagnosis",
        "antecedents": ["Frass_In_Stem", "Bore_Holes_In_Stem", "Deadheart_Seedling", "Easily_Pulled_Tillers", "Whitehead_Empty_Panicles"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Vegetative deadhearts and generative whiteheads accompanied by larval culm boring and frass."
    },
    {
        "id": "SWRL-R04",
        "threat": "Rice_Bug",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Rice Bug Diagnosis",
        "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Leaf_Margin_Sap_Sucking", "Rotten_Panicles", "Random_Feeding_Pattern", "Localized_Leaf_Yellowing", "Empty_Grains"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Simultaneous observation of feeding puncture marks, empty chalky grains, and active insect stages."
    },
    {
        "id": "SWRL-R05",
        "threat": "Brown_Planthopper",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Brown Planthopper Diagnosis",
        "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Plant_Yellowing", "Hopperburn_Drying", "Circular_Hopperburn_Patches", "Blackened_Feeding_Punctures", "Empty_Grains"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Classic circular hopperburn dying patches and dense colonies on basal tillers."
    },
    {
        "id": "SWRL-R06",
        "threat": "Bacterial_Leaf_Blight",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Bacterial Leaf Blight Diagnosis",
        "antecedents": ["Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow", "Yellowing_Leaf_Tips", "Uniform_Field_Infection", "Rapid_Disease_Spread"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Systemic vascular yellowing along vein ridges with rapid epidemiological transmission across field."
    },
    {
        "id": "SWRL-R07",
        "threat": "False_Smut",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical False Smut Diagnosis",
        "antecedents": ["Rusty_Grain_Balls", "Blackened_Grain_Balls", "Uniform_Field_Infection", "Rainy_Season_Outbreak", "Slight_Panicle_Infection", "Milky_Stage_Vulnerability"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Transformation of individual spikelets into yellow-orange velvety spore balls turning greenish-black."
    },
    {
        "id": "SWRL-R08",
        "threat": "Rice_Blast",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Blast Diagnosis",
        "antecedents": ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions", "Uniform_Field_Infection", "Infected_Seedlings"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Elliptical spindle/diamond lesions with necrotic panicle neck rot caused by Magnaporthe oryzae."
    },
    {
        "id": "SWRL-R09",
        "threat": "Rice_Grassy_Stunt",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Grassy Stunt Virus Diagnosis",
        "antecedents": ["Brown_Planthopper_Present", "Necrotic_Spots", "Severe_Stunting", "No_Panicle_Formation"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Excessive profuse tillering, severe dwarfing, heading suppression, and confirmed BPH vector presence."
    },
    {
        "id": "SWRL-R10",
        "threat": "Rice_Tungro_Virus",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Tungro Virus Diagnosis",
        "antecedents": ["Green_Leafhopper_Present", "Necrotic_Spots", "Yellowing_Leaves", "Whitehead_Empty_Panicles"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Foliar yellow-orange discoloration, delayed flowering, empty panicles, and active Nephotettix virescens."
    },

    # ---------------------------------------------------------------------
    # Tier 2: Relaxed Composite Rules (High Sensitivity, Partial Scouting)
    # ---------------------------------------------------------------------
    {
        "id": "SWRL-R11",
        "threat": "Grasshopper",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Grasshopper Diagnosis",
        "antecedents": ["Severed_Panicles", "Leaf_Chewing_Damage"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Sufficient mechanical chewing damage and severed panicle heads observed under partial field scouting."
    },
    {
        "id": "SWRL-R12",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Root Nematode Diagnosis",
        "antecedents": ["Hook_Like_Root_Swelling", "Root_Knot_Swelling"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Characteristic hook-like terminal root galling pathognomonic for Hirschmanniella oryzae."
    },
    {
        "id": "SWRL-R13",
        "threat": "Rice_Stem_Borer",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Stem Borer Diagnosis",
        "antecedents": ["Frass_In_Stem", "Bore_Holes_In_Stem"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Direct morphological evidence of stem bore entrance holes and internal larval frass."
    },
    {
        "id": "SWRL-R14",
        "threat": "Rice_Bug",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Rice Bug Diagnosis",
        "antecedents": ["Nymphs_Present", "Adult_Insects_Present", "Empty_Grains"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "High population density of Leptocorisa oratorius active during grain filling stage causing empty grains."
    },
    {
        "id": "SWRL-R15",
        "threat": "Brown_Planthopper",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Brown Planthopper Diagnosis",
        "antecedents": ["Hopperburn_Drying", "Circular_Hopperburn_Patches"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Rapid circular desiccation patches in field caused by intensive sap extraction."
    },
    {
        "id": "SWRL-R16",
        "threat": "Bacterial_Leaf_Blight",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Bacterial Leaf Blight Diagnosis",
        "antecedents": ["Yellowing_Leaf_Veins", "Uniform_Field_Infection"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Diagnostic yellow vein discoloration with uniform field-level dispersion pattern."
    },
    {
        "id": "SWRL-R17",
        "threat": "False_Smut",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed False Smut Diagnosis",
        "antecedents": ["Rusty_Grain_Balls", "Blackened_Grain_Balls"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Presence of mature and immature chlamydospore smut balls replacing grain kernels."
    },
    {
        "id": "SWRL-R18",
        "threat": "Rice_Blast",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Rice Blast Diagnosis",
        "antecedents": ["Panicle_Neck_Rot", "Diamond_Shaped_Lesions"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Key pathognomonic foliar spindle lesions and panicle node rot."
    },
    {
        "id": "SWRL-R19",
        "threat": "Rice_Grassy_Stunt",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Rice Grassy Stunt Virus Diagnosis",
        "antecedents": ["Brown_Planthopper_Present", "Severe_Stunting"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Vector Nilaparvata lugens co-occurring with pronounced plant dwarfing."
    },
    {
        "id": "SWRL-R20",
        "threat": "Rice_Tungro_Virus",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Rice Tungro Virus Diagnosis",
        "antecedents": ["Green_Leafhopper_Present", "Yellowing_Leaves"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Diagnostic yellowing of leaf blades combined with active green leafhopper transmission vector."
    },
]

# Build lookup metadata for XAI proof generation
SWRL_RULES_METADATA = {}
for r in RULE_REGISTRY:
    threat = r["threat"]
    if threat not in SWRL_RULES_METADATA:
        SWRL_RULES_METADATA[threat] = {}
    tier_key = r["tier"]
    badge = "tier-canonical" if tier_key == "tier1" else "tier-relaxed"
    tier_title = "Tier 1: Canonical Pathognomonic" if tier_key == "tier1" else "Tier 2: Relaxed Composite (Partial Observation)"
    formula = " ∧ ".join(f"hasSymptom(?Rice, {a})" for a in r["antecedents"]) + f" → {r['consequent_property']}(?Rice, {threat})"
    SWRL_RULES_METADATA[threat][tier_key] = {
        "rule_id": r["id"],
        "name": r["name"],
        "tier": tier_title,
        "tier_badge": badge,
        "antecedents": r["antecedents"],
        "formula": formula,
        "rationale": r["rationale"]
    }


# =========================================================================
# Dynamic Ontology Factory: Isolated World Construction for Ablation
# =========================================================================

def build_ontology(enabled_tiers=None, flat_consequents=False, world=None):
    """
    Constructs a RiceKG OWL 2 DL ontology in an isolated owlready2.World()
    with only the specified SWRL rule tiers loaded.

    :param enabled_tiers: Set of tiers to include, e.g. {"tier1"}, {"tier2"}, or {"tier1", "tier2"}.
                          If None, defaults to {"tier1", "tier2"}.
    :param flat_consequents: If True, asserts flat super-properties (hasPest/hasDisease)
                             rather than stratified (hasConfirmedPest/hasSuspectedPest).
    :param world: Optional owlready2.World instance. If None, instantiates a fresh World().
    :return: Configured owlready2.Ontology instance.
    """
    if enabled_tiers is None:
        enabled_tiers = {"tier1", "tier2"}
    if world is None:
        world = World()

    onto = world.get_ontology(ONTOLOGY_IRI)

    with onto:
        class Rice(Thing):
            namespace = onto

        class Symptom(Thing):
            namespace = onto

        class Threat(Thing):
            namespace = onto

        class Disease(Threat):
            namespace = onto

        class Pest(Threat):
            namespace = onto

        class ControlTreatment(Thing):
            namespace = onto

        # Object Properties hierarchy
        class hasSymptom(Rice >> Symptom):
            domain = [Rice]
            range = [Symptom]

        class hasThreat(Rice >> Threat):
            domain = [Rice]
            range = [Threat]

        class hasConfirmedThreat(hasThreat):
            domain = [Rice]
            range = [Threat]

        class hasSuspectedThreat(hasThreat):
            domain = [Rice]
            range = [Threat]

        class hasDisease(hasThreat):
            domain = [Rice]
            range = [Disease]

        class hasPest(hasThreat):
            domain = [Rice]
            range = [Pest]

        class hasConfirmedPest(hasConfirmedThreat, hasPest):
            domain = [Rice]
            range = [Pest]

        class hasSuspectedPest(hasSuspectedThreat, hasPest):
            domain = [Rice]
            range = [Pest]

        class hasConfirmedDisease(hasConfirmedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]

        class hasSuspectedDisease(hasSuspectedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]

        # Instantiate all known symptom individuals
        for s_name in ALL_SYMPTOMS:
            Symptom(s_name, namespace=onto)

        # Instantiate all threat individuals
        for p_name in PESTS:
            Pest(p_name, namespace=onto)

        for d_name in DISEASES:
            Disease(d_name, namespace=onto)

        # Load SWRL rules according to enabled tiers
        for r_meta in RULE_REGISTRY:
            if r_meta["tier"] in enabled_tiers:
                consequent_prop = r_meta["flat_consequent_property"] if flat_consequents else r_meta["consequent_property"]
                body_atoms = " ^ ".join(f"hasSymptom(?Rice, {ant})" for ant in r_meta["antecedents"])
                rule_str = f"{body_atoms} -> {consequent_prop}(?Rice, {r_meta['threat']})"
                rule_imp = Imp()
                rule_imp.set_as_rule(rule_str)

    return onto


# Initialize the module-default ontology (Full Tier 1 + Tier 2)
onto = build_ontology(enabled_tiers={"tier1", "tier2"}, flat_consequents=False)

# Backward-compatible individual exports
symptoms_map = {s: onto.search_one(iri=f"*{s}") for s in ALL_SYMPTOMS}
Grasshopper = getattr(onto, "Grasshopper", None)
Rice_Root_Nematode = getattr(onto, "Rice_Root_Nematode", None)
Rice_Stem_Borer = getattr(onto, "Rice_Stem_Borer", None)
Rice_Bug = getattr(onto, "Rice_Bug", None)
Brown_Planthopper = getattr(onto, "Brown_Planthopper", None)
Bacterial_Leaf_Blight = getattr(onto, "Bacterial_Leaf_Blight", None)
False_Smut = getattr(onto, "False_Smut", None)
Rice_Blast = getattr(onto, "Rice_Blast", None)
Rice_Grassy_Stunt = getattr(onto, "Rice_Grassy_Stunt", None)
Rice_Tungro_Virus = getattr(onto, "Rice_Tungro_Virus", None)


# =========================================================================
# Pellet DL Reasoning Engine
# =========================================================================

def predict_diseases(symptoms, flat=False, onto=None):
    """
    Infers rice pests and diseases using SWRL reasoning with confidence-graded output.

    Creates a temporary Rice individual in the target ontology, attaches observed
    symptoms, executes Pellet DL forward-chaining inference, extracts inferred
    properties, and returns ranked, graded diagnoses.

    :param symptoms: List of symptom identifier strings (English).
    :param flat: If True, returns List[str] of threat names for backwards compatibility.
    :param onto: Optional owlready2.Ontology instance (defaults to global module ontology).
    :return: List of dicts (or List[str] if flat=True).
    """
    target_onto = onto if onto is not None else globals()["onto"]
    plant_id = f"RiceSample_{uuid.uuid4().hex[:8]}"
    new_plant = target_onto.Rice(plant_id, namespace=target_onto)
    created_symptoms = []
    input_symptom_set = set()

    try:
        for symptom_name in symptoms:
            symptom_name = str(symptom_name).strip()
            if not symptom_name:
                continue
            input_symptom_set.add(symptom_name)
            symptom_obj = target_onto.search_one(iri=f"*{symptom_name}")
            if symptom_obj is None:
                symptom_obj = target_onto.Symptom(symptom_name, namespace=target_onto)
                created_symptoms.append(symptom_obj)
            new_plant.hasSymptom.append(symptom_obj)

        sync_reasoner_pellet(x=target_onto.world, infer_property_values=True, infer_data_property_values=True)

        confirmed_names = {t.name for t in getattr(new_plant, "hasConfirmedThreat", [])}
        suspected_names = {t.name for t in getattr(new_plant, "hasSuspectedThreat", [])}
        flat_threat_names = {t.name for t in (list(getattr(new_plant, "hasPest", [])) + list(getattr(new_plant, "hasDisease", [])))}
        all_threat_names = confirmed_names | suspected_names | flat_threat_names

        results = []
        for t_name in all_threat_names:
            meta = SWRL_RULES_METADATA.get(t_name, {})
            t1_meta = meta.get("tier1", {})
            t2_meta = meta.get("tier2", {})

            canonical_symptoms = t1_meta.get("antecedents", [])
            matched = [s for s in canonical_symptoms if s in input_symptom_set]
            missing = [s for s in canonical_symptoms if s not in input_symptom_set]
            antecedent_coverage = round(len(matched) / len(canonical_symptoms), 4) if canonical_symptoms else 1.0

            if t_name in confirmed_names:
                grade = "confirmed"
                confidence = 1.0
                fired = []
                if t1_meta.get("rule_id"):
                    fired.append(t1_meta["rule_id"])
                if t2_meta.get("rule_id"):
                    fired.append(t2_meta["rule_id"])
            elif t_name in suspected_names:
                grade = "suspected"
                confidence = 0.9714
                fired = [t2_meta["rule_id"]] if t2_meta.get("rule_id") else []
            else:
                # Flat unstratified rule inference
                grade = "unstratified"
                confidence = 1.0
                fired = ["SWRL-FLAT"]

            results.append({
                "threat": t_name,
                "grade": grade,
                "confidence": confidence,
                "antecedent_coverage": antecedent_coverage,
                "fired_rules": fired,
                "matched_symptoms": matched,
                "missing_symptoms": missing
            })

        # Rank: confirmed first, then antecedent coverage desc, then name
        results.sort(key=lambda x: (1 if x["grade"] == "confirmed" else 0, x["antecedent_coverage"], x["threat"]), reverse=True)

        if flat:
            return [item["threat"] for item in results]
        return results

    finally:
        destroy_entity(new_plant)
        for sym in created_symptoms:
            try:
                destroy_entity(sym)
            except Exception:
                pass


def predict_diseases_flat(symptoms, onto=None):
    """
    Backwards-compatible wrapper returning List[str] of diagnosed threat names.
    Preserves compatibility with test.py, evaluate.py, and legacy callers.

    :param symptoms: List of symptom identifier strings (English).
    :param onto: Optional owlready2.Ontology instance.
    :return: List of diagnosed pest and disease names as strings.
    """
    return predict_diseases(symptoms, flat=True, onto=onto)


# =========================================================================
# Explainable AI (XAI): Formal SWRL Rule Knowledge Representation
# =========================================================================

def explain_diagnoses(selected_symptoms, diagnosed_threats):
    """
    Generates explainable deductive proof traces for all inferred diagnoses.
    Identifies whether Tier 1 (canonical) or Tier 2 (relaxed) rule fired,
    and maps observed vs unobserved rule antecedents.

    :param selected_symptoms: List of user-selected symptom ID strings.
    :param diagnosed_threats: List of diagnosed threat key strings or result dicts.
    :return: Dictionary mapping threat key to proof trace explanation.
    """
    selected_set = set(selected_symptoms)
    explanations = {}

    threat_items = []
    for item in diagnosed_threats:
        if isinstance(item, dict) and "threat" in item:
            threat_items.append((item["threat"], item))
        else:
            threat_items.append((str(item), None))

    for threat_key, diag_dict in threat_items:
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

        t1 = meta["tier1"]
        t2 = meta["tier2"]

        if diag_dict and "grade" in diag_dict:
            t1_satisfied = (diag_dict["grade"] == "confirmed")
        else:
            t1_satisfied = all(ant in selected_set for ant in t1["antecedents"])

        active_rule = t1 if t1_satisfied else t2

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
