"""
RiceKG Expert System - Ontology Model & SWRL Reasoning Engine
-------------------------------------------------------------
Implements an OWL 2 DL ontology for rice pests and diseases using Owlready2
and the Pellet description logic reasoner. SWRL rules are defined via a
declarative registry supporting dynamic ontology construction and ablation.
"""

import os
import uuid
import subprocess
from owlready2 import *

def _configure_java_runtime():
    """Auto-detect working Java executable for Pellet reasoner if default 'java' is unavailable."""
    import owlready2
    candidates = []
    if "JAVA_HOME" in os.environ:
        candidates.append(os.path.join(os.environ["JAVA_HOME"], "bin", "java"))
    candidates.extend([
        "/opt/homebrew/opt/openjdk/bin/java",
        "/usr/local/opt/openjdk/bin/java",
        "/usr/lib/jvm/default-java/bin/java",
        "/opt/homebrew/bin/java",
        "/usr/local/bin/java",
        "java"
    ])
    app_supp = os.path.expanduser("~/Library/Application Support")
    if os.path.isdir(app_supp):
        candidates.extend([
            os.path.join(app_supp, "neo4j-desktop/Application/Cache/runtime/zulu21.44.17-ca-jdk21.0.8-macosx_aarch64/zulu-21.jdk/Contents/Home/bin/java"),
            os.path.join(app_supp, "Neo4j Desktop/Application/distributions/java/zulu17.58.21-ca-jdk17.0.15/zulu-17.jdk/Contents/Home/bin/java")
        ])
    for cand in candidates:
        if not cand:
            continue
        if cand != "java" and not (os.path.isfile(cand) and os.access(cand, os.X_OK)):
            continue
        try:
            res = subprocess.run([cand, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=5)
            owlready2.JAVA_EXE = cand
            if cand != "java" and "JAVA_HOME" not in os.environ:
                os.environ["JAVA_HOME"] = os.path.dirname(os.path.dirname(cand))
            return cand
        except Exception:
            continue
    return owlready2.JAVA_EXE

_configure_java_runtime()

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
    "Severe_Stunting", "No_Panicle_Formation", "Green_Leafhopper_Present",

    # P0-5 Step 2 vocabulary extension. Each term denotes a sign that the
    # phytopathology literature treats as diagnostically informative but that the
    # original 45-term vocabulary could not express. Sources are recorded per term
    # in docs/ONTOLOGY.md; none of these were chosen by inspecting benchmark cases.
    "Water_Soaked_Lesions",      # early bacterial lesion, leaf margin/tip
    "Bacterial_Ooze",            # bacterial exudate droplets on lesion or cut leaf
    "Leaf_Mottling",             # mosaic/mottle pattern, virus-associated
    "Interveinal_Chlorosis",     # chlorosis between veins, virus-associated
    "Grain_Discoloration",       # discoloured or spotted grain
    "Leaf_Sheath_Lesions",       # lesions on the leaf sheath (anatomy absent before)
    "Stem_Rot_Lesions",          # rot or lodging at the culm
    "Excessive_Tillering",       # RGSV hallmark; tungro shows the opposite
    "Orange_Leaf_Discoloration"  # tungro hallmark, yellow-orange from the leaf tip
]

# 21 phenotypic symptoms associated specifically with insect damage.
# Retained in the ontology vocabulary (subclassed under OutOfScopeSign / InsectDamageSign)
# so the system provides an explicit differential out-of-scope response rather than a
# silent No_Diagnosis.
INSECT_DAMAGE_SIGNS = [
    "Adult_Insects_Present", "Blackened_Feeding_Punctures", "Bore_Holes_In_Stem",
    "Broad_Leaf_Damage", "Brown_Nymphs", "Circular_Hopperburn_Patches", "Deadheart_Seedling",
    "Easily_Pulled_Tillers", "Eggs_On_Plant", "Empty_Grains", "Frass_In_Stem", "Hopperburn_Drying",
    "Leaf_Chewing_Damage", "Leaf_Margin_Sap_Sucking", "Localized_Leaf_Yellowing", "Nymphs_Present",
    "Plant_Yellowing", "Random_Feeding_Pattern", "Rotten_Panicles", "Severed_Panicles", "Yellow_Nymphs"
]

# The subset of INSECT_DAMAGE_SIGNS that only an insect produces: the organism itself, its
# eggs, or a feeding mechanism no pathogen reproduces. The remaining seven terms
# (Plant_Yellowing, Localized_Leaf_Yellowing, Empty_Grains, Rotten_Panicles,
# Deadheart_Seedling, Easily_Pulled_Tillers, Random_Feeding_Pattern) are also produced by
# in-scope and out-of-scope pathogens, nutrient deficiency or abiotic stress, so they never
# count as evidence of insect damage on their own.
INSECT_SPECIFIC_SIGNS = [
    "Adult_Insects_Present", "Nymphs_Present", "Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant",
    "Frass_In_Stem", "Bore_Holes_In_Stem", "Hopperburn_Drying", "Circular_Hopperburn_Patches",
    "Blackened_Feeding_Punctures", "Leaf_Margin_Sap_Sucking", "Leaf_Chewing_Damage",
    "Broad_Leaf_Damage", "Severed_Panicles",
]

# Distinct insect-specific signs required before the out-of-scope response is returned.
# Two matches the evidentiary minimum of the removed Tier-2 insect rules (SWRL-R11, R13, R15
# each required two), so a single isolated sign stays a No_Diagnosis negative control.
INSECT_GATE_MIN_SIGNS = 2

INSECT_OUT_OF_SCOPE_RESPONSE = (
    "consistent with insect damage, which is outside the diagnostic scope of this system"
)
INSECT_OUT_OF_SCOPE_TARGET = "insect damage, out of scope"


def insect_damage_evidence(symptoms):
    """Return the sorted insect-specific signs in `symptoms` if they meet the gate, else []."""
    matched = sorted(set(symptoms) & set(INSECT_SPECIFIC_SIGNS))
    return matched if len(matched) >= INSECT_GATE_MIN_SIGNS else []


# Minimum Tier-2 antecedent coverage at which a non-firing rule is surfaced as a
# `possible` diagnosis. Strict Horn-clause matching returns nothing when a single
# antecedent is unobserved, which discards strong partial evidence; P0-1 specified an
# ordinal grade set {confirmed, probable, possible} that was never implemented.
# Calibrated on the field benchmark `dev` split only — see docs/ONTOLOGY.md.
POSSIBLE_COVERAGE_THRESHOLD = 0.5

# Diagnosable scope narrowed to 6 evidence-backed classes with independent field cases.
# Rice_Root_Nematode is retained as an in-scope parasitic nematode pest.
PESTS = [
    "Rice_Root_Nematode"
]

DISEASES = [
    "Bacterial_Leaf_Blight", "False_Smut", "Rice_Blast",
    "Rice_Grassy_Stunt", "Rice_Tungro_Virus"
]

ALL_DIAGNOSES = PESTS + DISEASES

RULE_REGISTRY = [
    # ---------------------------------------------------------------------
    # Tier 1: Canonical Pathognomonic Rules (High Specificity, 100% Precision)
    # ---------------------------------------------------------------------
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
        "id": "SWRL-R12",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Root Nematode Diagnosis",
        "antecedents": ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Root galling with hooked tips accompanied by above-ground stunting and chlorosis. The previous antecedent set required two distinct gall morphologies (hook-like and knot) to be recorded simultaneously, which conflates Hirschmanniella and Meloidogyne damage and is rarely reported together.",
        "literature": "Bridge, Plowright & Peng (2005), Nematode Parasites of Rice, in Plant Parasitic Nematodes in Subtropical and Tropical Agriculture, CABI; IRRI Rice Doctor, root-knot nematode fact sheet."
    },
    {
        "id": "SWRL-R16",
        "threat": "Bacterial_Leaf_Blight",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Bacterial Leaf Blight Diagnosis",
        "antecedents": ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Water-soaked lesions beginning at the leaf tip or margin and progressing along it. Uniform_Field_Infection described the stand rather than the plant. Bacterial_Ooze was tried and withdrawn: exudate is a genus-level sign shared with X. oryzicola, Burkholderia and Pantoea, so it cannot discriminate bacterial blight from the other bacterial diseases of rice. Tip and margin onset is the discriminating feature against the interveinal streaking of bacterial leaf streak.",
        "literature": "Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI, pp. 61-96; IRRI Rice Doctor, bacterial blight fact sheet."
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
        "antecedents": ["Diamond_Shaped_Lesions", "Necrotic_Spots"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Diamond or spindle-shaped leaf lesions with necrotic centres. The previous antecedent set required the leaf phase and the panicle-neck phase to be present at once; these are distinct phenological phases of the same pathogen and are rarely reported together.",
        "literature": "Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI, pp. 109-201; IRRI Rice Doctor, rice blast fact sheet."
    },
    {
        "id": "SWRL-R19",
        "threat": "Rice_Grassy_Stunt",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Rice Grassy Stunt Virus Diagnosis",
        "antecedents": ["Severe_Stunting", "Excessive_Tillering"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Severe stunting together with excessive tillering. Vector presence was withdrawn because it makes diagnosis contingent on entomological sampling. Stunting with mottling was tried and withdrawn: both signs are shared across rice viruses. Excessive tillering discriminates grassy stunt from tungro, which reduces tillering.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor, rice grassy stunt fact sheet."
    },
    {
        "id": "SWRL-R20",
        "threat": "Rice_Tungro_Virus",
        "threat_type": "Disease",
        "tier": "tier2",
        "name": "Relaxed Rice Tungro Virus Diagnosis",
        "antecedents": ["Stunted_Growth", "Orange_Leaf_Discoloration"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Stunting with the characteristic yellow-orange leaf discoloration progressing from the tip. Vector presence was withdrawn as for grassy stunt. Interveinal chlorosis was tried and withdrawn: it is shared with other rice viruses, whereas the orange cast is the tungro hallmark.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor, rice tungro fact sheet."
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

        class OutOfScopeSign(Symptom):
            namespace = onto

        class InsectDamageSign(OutOfScopeSign):
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

        # Instantiate all known symptom individuals.
        # The 21 insect-only terms are typed as InsectDamageSign (subclass of Symptom).
        for s_name in ALL_SYMPTOMS:
            if s_name in INSECT_DAMAGE_SIGNS:
                InsectDamageSign(s_name, namespace=onto)
            else:
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

def predict_diseases(symptoms, flat=False, onto=None, include_possible=False):
    """
    Infers rice pests and diseases using SWRL reasoning with confidence-graded output.

    Creates a temporary Rice individual in the target ontology, attaches observed
    symptoms, executes Pellet DL forward-chaining inference, extracts inferred
    properties, and returns ranked, graded diagnoses.

    :param symptoms: List of symptom identifier strings (English).
    :param flat: If True, returns List[str] of threat names for backwards compatibility.
    :param onto: Optional owlready2.Ontology instance (defaults to global module ontology).
    :param include_possible: When True, also surface threats whose Tier-2 antecedent
        coverage reaches POSSIBLE_COVERAGE_THRESHOLD but whose rule did not fire, graded
        `possible`. Off by default so that the v1 API and predict_diseases_flat keep
        their existing behaviour exactly.
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

        if include_possible:
            # Strict subset matching yields nothing when one antecedent is unobserved.
            # Score the Tier-2 rules that did not fire and surface the strongest partial
            # evidence as a weaker grade, keeping the matched and unmet antecedents visible
            # so the derivation stays auditable.
            for t_name, meta in SWRL_RULES_METADATA.items():
                if t_name in all_threat_names:
                    continue
                t2_ants = meta.get("tier2", {}).get("antecedents", [])
                if not t2_ants:
                    continue
                matched = [s for s in t2_ants if s in input_symptom_set]
                coverage = round(len(matched) / len(t2_ants), 4)
                if coverage < POSSIBLE_COVERAGE_THRESHOLD or not matched:
                    continue
                results.append({
                    "threat": t_name,
                    "grade": "possible",
                    "confidence": round(0.5 * coverage, 4),
                    "antecedent_coverage": coverage,
                    "fired_rules": [],
                    "matched_symptoms": matched,
                    "missing_symptoms": [s for s in t2_ants if s not in input_symptom_set]
                })

        # If no in-scope threats diagnosed, check if observed symptoms indicate out-of-scope insect damage
        if not results:
            insect_matched = insect_damage_evidence(input_symptom_set)
            if insect_matched:
                results.append({
                    "threat": INSECT_OUT_OF_SCOPE_TARGET,
                    "grade": "out_of_scope",
                    "confidence": 0.0,
                    "antecedent_coverage": 0.0,
                    "fired_rules": [],
                    "matched_symptoms": insect_matched,
                    "missing_symptoms": [],
                    "message": INSECT_OUT_OF_SCOPE_RESPONSE
                })

        # Rank: confirmed first, then antecedent coverage desc, then name
        grade_rank = {"confirmed": 3, "unstratified": 2, "suspected": 2, "possible": 1, "out_of_scope": 0}
        results.sort(key=lambda x: (grade_rank.get(x["grade"], 0), x["antecedent_coverage"], x["threat"]), reverse=True)

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
# Explainable AI (XAI): Formal SWRL Rule Knowledge Representation & Traces
# =========================================================================

def get_derivation_trace(selected_symptoms, diagnosed_threats=None):
    """
    Generates a full explainable derivation trace across all SWRL rules in RiceKG.

    Identifies:
    - Which rules fired, in what order
    - Which observed symptoms satisfied which antecedent
    - Which antecedents were unmet for unsatisfied or candidate rules
    - Resulting confidence grade and formal Horn-clause proof trees

    :param selected_symptoms: List of user-selected symptom ID strings.
    :param diagnosed_threats: Optional list of diagnosed threat keys or result dicts.
    :return: Dictionary containing complete derivation trace and proof trees.
    """
    selected_set = set(selected_symptoms)
    fired_rules = []
    candidate_rules_by_threat = {}
    evaluated_rules_trace = []

    # Map diagnosed threats and grades if provided
    diagnosed_map = {}
    if diagnosed_threats:
        for item in diagnosed_threats:
            if isinstance(item, dict) and "threat" in item:
                diagnosed_map[item["threat"]] = item
            else:
                diagnosed_map[str(item)] = {"threat": str(item), "grade": "confirmed", "confidence": 1.0}

    # Evaluate all 20 production rules in standard stratified execution order (Tier 1 then Tier 2)
    for rule in RULE_REGISTRY:
        threat = rule["threat"]
        antecedents = rule["antecedents"]
        satisfied = [ant for ant in antecedents if ant in selected_set]
        unmet = [ant for ant in antecedents if ant not in selected_set]
        is_fired = (len(unmet) == 0)
        coverage_pct = round((len(satisfied) / len(antecedents)) * 100, 1) if antecedents else 0.0

        trace_entry = {
            "rule_id": rule["id"],
            "name": rule["name"],
            "threat": threat,
            "threat_type": rule["threat_type"],
            "tier": rule["tier"],
            "consequent_property": rule["consequent_property"],
            "antecedents_count": len(antecedents),
            "satisfied_count": len(satisfied),
            "unmet_count": len(unmet),
            "status": "FIRED" if is_fired else "UNSATISFIED",
            "coverage_percentage": coverage_pct,
            "antecedents": antecedents,
            "satisfied_antecedents": satisfied,
            "unmet_antecedents": unmet,
            "formula": " ^ ".join(f"hasSymptom(?Rice, {a})" for a in antecedents) + f" -> {rule['consequent_property']}(?Rice, {threat})",
            "rationale": rule.get("rationale", "")
        }

        evaluated_rules_trace.append(trace_entry)

        if is_fired:
            fired_rules.append(trace_entry)

        if threat not in candidate_rules_by_threat:
            candidate_rules_by_threat[threat] = []
        candidate_rules_by_threat[threat].append(trace_entry)

    # Construct formal proof trees for diagnosed or relevant threats
    proof_trees = {}
    if diagnosed_map:
        threats_to_trace = list(diagnosed_map.keys())
    else:
        threats_to_trace = list(set(r["threat"] for r in fired_rules))
        if not threats_to_trace:
            threats_to_trace = [
                threat for threat, rules in candidate_rules_by_threat.items()
                if any(r["satisfied_count"] > 0 for r in rules)
            ]

    for threat in threats_to_trace:
        threat_rules = candidate_rules_by_threat.get(threat, [])
        t1_rule = next((r for r in threat_rules if r["tier"] == "tier1"), None)
        t2_rule = next((r for r in threat_rules if r["tier"] == "tier2"), None)

        diag_info = diagnosed_map.get(threat, {})
        grade = diag_info.get("grade")
        if not grade:
            if t1_rule and t1_rule["status"] == "FIRED":
                grade = "confirmed"
            elif t2_rule and t2_rule["status"] == "FIRED":
                grade = "suspected"
            else:
                grade = "possible"

        confidence = diag_info.get("confidence", 1.0 if grade == "confirmed" else (0.80 if grade == "suspected" else 0.50))

        # Select primary proving rule
        if grade == "confirmed" and t1_rule and t1_rule["status"] == "FIRED":
            active_rule = t1_rule
            predicate = "hasConfirmedThreat"
        elif t2_rule and t2_rule["status"] == "FIRED":
            active_rule = t2_rule
            predicate = "hasSuspectedThreat"
        elif t2_rule:
            active_rule = t2_rule
            predicate = "hasPossibleThreat"
        else:
            active_rule = threat_rules[0] if threat_rules else None
            predicate = "hasThreat"

        premises = []
        if active_rule:
            for ant in active_rule["antecedents"]:
                observed = ant in selected_set
                premises.append({
                    "symptom_id": ant,
                    "symptom_name": ant.replace("_", " "),
                    "predicate": f"hasSymptom(Rice_Sample, {ant})",
                    "observed": observed,
                    "status": "SATISFIED" if observed else "UNMET"
                })

        proof_tree = {
            "conclusion": f"{predicate}(Rice_Sample, {threat})",
            "threat": threat,
            "grade": grade,
            "confidence": confidence,
            "inference_step": {
                "rule_id": active_rule["rule_id"] if active_rule else "SWRL-GENERIC",
                "rule_name": active_rule["name"] if active_rule else f"Deductive Rule for {threat}",
                "inference_rule": "Modus Ponens" if (active_rule and active_rule["status"] == "FIRED") else "Partial Antecedent Match",
                "tier": "Tier 1 (Canonical)" if (active_rule and active_rule["tier"] == "tier1") else "Tier 2 (Relaxed Composite)",
                "formula": active_rule["formula"] if active_rule else "",
                "rationale": active_rule["rationale"] if active_rule else "",
                "premises": premises
            },
            "candidate_rules": threat_rules
        }
        proof_trees[threat] = proof_tree

    return {
        "summary": {
            "total_rules_evaluated": len(evaluated_rules_trace),
            "fired_rules_count": len(fired_rules),
            "fired_rules_sequence": [r["rule_id"] for r in fired_rules],
            "observed_symptoms_count": len(selected_symptoms),
            "observed_symptoms": selected_symptoms,
            "diagnoses_count": len(threats_to_trace)
        },
        "fired_rules": fired_rules,
        "proof_trees": proof_trees,
        "candidate_rules_by_threat": candidate_rules_by_threat,
        "evaluated_rules_trace": evaluated_rules_trace
    }


def explain_diagnoses(selected_symptoms, diagnosed_threats):
    """
    Generates explainable deductive proof traces for all inferred diagnoses.
    Identifies whether Tier 1 (canonical) or Tier 2 (relaxed) rule fired,
    maps observed vs unobserved rule antecedents, and attaches full proof trees.

    :param selected_symptoms: List of user-selected symptom ID strings.
    :param diagnosed_threats: List of diagnosed threat key strings or result dicts.
    :return: Dictionary mapping threat key to proof trace explanation.
    """
    selected_set = set(selected_symptoms)
    explanations = {}

    trace_data = get_derivation_trace(selected_symptoms, diagnosed_threats)
    proof_trees = trace_data["proof_trees"]

    threat_items = []
    for item in diagnosed_threats:
        if isinstance(item, dict) and "threat" in item:
            threat_items.append((item["threat"], item))
        else:
            threat_items.append((str(item), None))

    for threat_key, diag_dict in threat_items:
        proof_tree = proof_trees.get(threat_key)
        meta = SWRL_RULES_METADATA.get(threat_key)

        if not meta:
            if threat_key == INSECT_OUT_OF_SCOPE_TARGET or (diag_dict and diag_dict.get("grade") == "out_of_scope"):
                explanations[threat_key] = {
                    "rule_id": "OUT-OF-SCOPE-INSECT",
                    "name": "Insect Damage (Outside Diagnostic Scope)",
                    "tier": "Scope Boundary Assessment",
                    "tier_badge": "tier-relaxed",
                    "formula": f"≥{INSECT_GATE_MIN_SIGNS} distinct insect-specific signs ∧ no in-scope rule fires → OutOfScope(?Rice)",
                    "rationale": INSECT_OUT_OF_SCOPE_RESPONSE,
                    "antecedents_status": [{"symptom": s, "symptom_name": s.replace("_", " "), "observed": True} for s in insect_damage_evidence(selected_symptoms)],
                    "proof_tree": proof_tree
                }
                continue

            explanations[threat_key] = {
                "rule_id": "SWRL-GENERIC",
                "name": f"Deductive Rule for {threat_key.replace('_', ' ')}",
                "tier": "First-Order Logic Inference",
                "tier_badge": "tier-relaxed",
                "formula": f"hasSymptom(?Rice, ...) → hasThreat(?Rice, {threat_key})",
                "rationale": "Inferred via Pellet description logic tableau algorithm.",
                "antecedents_status": [{"symptom": s, "observed": True} for s in selected_symptoms],
                "proof_tree": proof_tree
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
            "rule_level": "Tier 1 (Canonical)" if t1_satisfied else "Tier 2 (Relaxed Composite)",
            "proof_tree": proof_tree,
            "candidate_rules": trace_data["candidate_rules_by_threat"].get(threat_key, [])
        }

    return explanations
