"""
RiceKG Expert System - Ontology Model & Description Logic (DL) Reasoning Engine
---------------------------------------------------------------------------------
Implements an OWL 2 DL ontology for rice pests and diseases using Owlready2
and the Pellet description logic reasoner. Biotic threats are diagnosed via
OWL 2 Equivalent Classes (Defined Classes) with machine-provable subsumption,
structured across a two-axis symptom taxonomy (anatomical & phenomenological).
"""

import os
import uuid
import math
import types
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY_PATH = os.path.join(BASE_DIR, "ontology", "rice_ontology.owl")
ONTOLOGY_IRI = "http://www.semanticweb.org/ontologies/rice_pest_disease.owl"

# =========================================================================
# Declarative Master Catalog: Symptoms, Threats, and Taxonomic Axes
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

    # P0-5 Step 2 vocabulary extension
    "Water_Soaked_Lesions",      # early bacterial lesion, leaf margin/tip
    "Bacterial_Ooze",            # bacterial exudate droplets on lesion or cut leaf
    "Leaf_Mottling",             # mosaic/mottle pattern, virus-associated
    "Interveinal_Chlorosis",     # chlorosis between veins, virus-associated
    "Grain_Discoloration",       # discoloured or spotted grain
    "Leaf_Sheath_Lesions",       # lesions on the leaf sheath
    "Stem_Rot_Lesions",          # rot or lodging at the culm
    "Excessive_Tillering",       # RGSV hallmark; tungro shows the opposite
    "Orange_Leaf_Discoloration", # tungro hallmark, yellow-orange from the leaf tip

    # PART 4-J: Expressivity descriptors mapped from field benchmark negative controls
    "Leaf_Desiccation",          # whole-leaf drying/desiccation (Ou 1985)
    "Chlorotic_Streaks",         # chlorotic streaking along veins (Ou 1985)
    "Brown_Streaks",             # necrotic brown streaks (Ou 1985)
    "Leaf_Bleaching",            # foliar bleaching/kresek symptoms (Ou 1985)
    "Whitened_Leaf_Tips",        # apical whitening from Aphelenchoides besseyi (Bridge et al. 2005)
    "Leaf_Wilting",              # whole-leaf wilting/senescence (Ou 1985)
    "Discolored_Roots"           # root darkening/necrosis from Hirschmanniella (Bridge et al. 2005)
]

# -------------------------------------------------------------------------
# 4-A: Evidence Type Stratification
# -------------------------------------------------------------------------
OBSERVATION_CATEGORIES = {
    # Direct organism sightings
    "Brown_Nymphs": "hasOrganismSighting",
    "Yellow_Nymphs": "hasOrganismSighting",
    "Eggs_On_Plant": "hasOrganismSighting",
    "Nymphs_Present": "hasOrganismSighting",
    "Adult_Insects_Present": "hasOrganismSighting",
    "Frass_In_Stem": "hasOrganismSighting",

    # Entomological vector sightings for viral phytopathogens
    "Brown_Planthopper_Present": "hasVectorSighting",
    "Green_Leafhopper_Present": "hasVectorSighting",

    # Stand-level and environmental epidemiological context
    "Rapid_Disease_Spread": "hasEpidemiologicalContext",
    "Rainy_Season_Outbreak": "hasEpidemiologicalContext",
    "Uniform_Field_Infection": "hasEpidemiologicalContext",
    "Milky_Stage_Vulnerability": "hasEpidemiologicalContext",
    "Infected_Seedlings": "hasEpidemiologicalContext",
    "Random_Feeding_Pattern": "hasEpidemiologicalContext",
    "Circular_Hopperburn_Patches": "hasEpidemiologicalContext",
}
# Default for all remaining terms is "hasSymptom" (plant pathological sign)

# -------------------------------------------------------------------------
# 4-B: Two-Axis Symptom Taxonomy (Anatomical & Phenomenological)
# -------------------------------------------------------------------------
SYMPTOM_TAXONOMY = {
    # Chlorosis
    "Plant_Yellowing": {"anatomical": "WholePlantSign", "phenomenological": "Chlorosis"},
    "Yellowing_Leaves": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Yellowing_Leaf_Tips": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Yellowing_Leaf_Veins": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Leaf_Discoloration_Yellow": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Localized_Leaf_Yellowing": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Interveinal_Chlorosis": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Orange_Leaf_Discoloration": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Leaf_Mottling": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Chlorotic_Streaks": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Leaf_Bleaching": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},
    "Whitened_Leaf_Tips": {"anatomical": "LeafSign", "phenomenological": "Chlorosis"},

    # Necrosis
    "Necrotic_Spots": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Diamond_Shaped_Lesions": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Water_Soaked_Lesions": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Stem_Rot_Lesions": {"anatomical": "StemSign", "phenomenological": "Necrosis"},
    "Leaf_Sheath_Lesions": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Panicle_Neck_Rot": {"anatomical": "PanicleSign", "phenomenological": "Necrosis"},
    "Rotten_Panicles": {"anatomical": "PanicleSign", "phenomenological": "Necrosis"},
    "Hopperburn_Drying": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Blackened_Feeding_Punctures": {"anatomical": "StemSign", "phenomenological": "Necrosis"},
    "Deadheart_Seedling": {"anatomical": "WholePlantSign", "phenomenological": "Necrosis"},
    "Brown_Streaks": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Leaf_Desiccation": {"anatomical": "LeafSign", "phenomenological": "Necrosis"},
    "Leaf_Wilting": {"anatomical": "WholePlantSign", "phenomenological": "Necrosis"},
    "Discolored_Roots": {"anatomical": "RootSign", "phenomenological": "Necrosis"},

    # Stunting
    "Stunted_Growth": {"anatomical": "WholePlantSign", "phenomenological": "Stunting"},
    "Severe_Stunting": {"anatomical": "WholePlantSign", "phenomenological": "Stunting"},

    # Mechanical Damage
    "Leaf_Chewing_Damage": {"anatomical": "LeafSign", "phenomenological": "MechanicalDamage"},
    "Broad_Leaf_Damage": {"anatomical": "LeafSign", "phenomenological": "MechanicalDamage"},
    "Severed_Panicles": {"anatomical": "PanicleSign", "phenomenological": "MechanicalDamage"},
    "Bore_Holes_In_Stem": {"anatomical": "StemSign", "phenomenological": "MechanicalDamage"},
    "Easily_Pulled_Tillers": {"anatomical": "StemSign", "phenomenological": "MechanicalDamage"},
    "Leaf_Margin_Sap_Sucking": {"anatomical": "LeafSign", "phenomenological": "MechanicalDamage"},

    # Grain Abnormality
    "Empty_Grains": {"anatomical": "GrainSign", "phenomenological": "GrainAbnormality"},
    "Grain_Discoloration": {"anatomical": "GrainSign", "phenomenological": "GrainAbnormality"},
    "Rusty_Grain_Balls": {"anatomical": "GrainSign", "phenomenological": "GrainAbnormality"},
    "Slight_Panicle_Infection": {"anatomical": "GrainSign", "phenomenological": "GrainAbnormality"},
    "Blackened_Grain_Balls": {"anatomical": "GrainSign", "phenomenological": "GrainAbnormality"},
    "Whitehead_Empty_Panicles": {"anatomical": "PanicleSign", "phenomenological": "GrainAbnormality"},

    # Root Morphology
    "Hook_Like_Root_Swelling": {"anatomical": "RootSign", "phenomenological": None},
    "Root_Knot_Swelling": {"anatomical": "RootSign", "phenomenological": None},
    "Deformed_Roots": {"anatomical": "RootSign", "phenomenological": None},

    # Architecture & Other Signs
    "Excessive_Tillering": {"anatomical": "WholePlantSign", "phenomenological": None},
    "No_Panicle_Formation": {"anatomical": "PanicleSign", "phenomenological": None},
    "Bacterial_Ooze": {"anatomical": "LeafSign", "phenomenological": None}
}

# 19 phenotypic symptoms associated with insect damage. Empty_Grains and Plant_Yellowing
# were removed in ontology v2.2.0: both are recorded on in-scope disease cases (blast,
# false smut, tungro), so typing them InsectDamageSign was a misclassification.
INSECT_DAMAGE_SIGNS = [
    "Adult_Insects_Present", "Blackened_Feeding_Punctures", "Bore_Holes_In_Stem",
    "Broad_Leaf_Damage", "Brown_Nymphs", "Circular_Hopperburn_Patches", "Deadheart_Seedling",
    "Easily_Pulled_Tillers", "Eggs_On_Plant", "Frass_In_Stem", "Hopperburn_Drying",
    "Leaf_Chewing_Damage", "Leaf_Margin_Sap_Sucking", "Localized_Leaf_Yellowing", "Nymphs_Present",
    "Random_Feeding_Pattern", "Rotten_Panicles", "Severed_Panicles", "Yellow_Nymphs"
]

INSECT_SPECIFIC_SIGNS = [
    "Adult_Insects_Present", "Nymphs_Present", "Brown_Nymphs", "Yellow_Nymphs", "Eggs_On_Plant",
    "Frass_In_Stem", "Bore_Holes_In_Stem", "Hopperburn_Drying", "Circular_Hopperburn_Patches",
    "Blackened_Feeding_Punctures", "Leaf_Margin_Sap_Sucking", "Leaf_Chewing_Damage",
    "Broad_Leaf_Damage", "Severed_Panicles",
]

INSECT_GATE_MIN_SIGNS = 2

INSECT_OUT_OF_SCOPE_RESPONSE = (
    "consistent with insect damage, which is outside the diagnostic scope of this system"
)
INSECT_OUT_OF_SCOPE_TARGET = "insect damage, out of scope"

# Signs belonging to plant diseases outside the six in-scope classes (e.g. sheath blight,
# stem rot, bacterial panicle blight, bacterial leaf streak, white tip).
NON_MODELED_PATHOGEN_SIGNS = [
    "Leaf_Sheath_Lesions", "Stem_Rot_Lesions", "Grain_Discoloration",
    "Chlorotic_Streaks", "Brown_Streaks", "Leaf_Bleaching",
    "Whitened_Leaf_Tips", "Discolored_Roots", "Leaf_Desiccation",
    "Leaf_Wilting"
]

NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE = (
    "signs recorded, not consistent with any disease in scope"
)
NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET = "signs recorded, not consistent with any disease in scope"


def insect_damage_evidence(symptoms):
    """Return the sorted insect-specific signs in `symptoms` if they meet the gate, else []."""
    matched = sorted(set(symptoms) & set(INSECT_SPECIFIC_SIGNS))
    return matched if len(matched) >= INSECT_GATE_MIN_SIGNS else []


def negative_control_evidence(symptoms):
    """Return non-modeled pathogen signs in `symptoms` that indicate an out-of-scope disease."""
    return sorted(set(symptoms) & set(NON_MODELED_PATHOGEN_SIGNS))


# Minimum Tier-2 antecedent coverage at which a non-firing rule is surfaced as a
# `possible` diagnosis.
POSSIBLE_COVERAGE_THRESHOLD = 0.5

# Diagnosable scope narrowed to 6 evidence-backed classes with independent field cases.
PESTS = [
    "Rice_Root_Nematode"
]

DISEASES = [
    "Bacterial_Leaf_Blight", "False_Smut", "Rice_Blast",
    "Rice_Grassy_Stunt", "Rice_Tungro_Virus"
]

ALL_DIAGNOSES = PESTS + DISEASES

# -------------------------------------------------------------------------
# 4-F: Integrated Pest Management (IPM) Control Treatments (CQ08)
# -------------------------------------------------------------------------
CONTROL_TREATMENTS = {
    "Rice_Root_Nematode": {
        "id": "Control_Rice_Root_Nematode",
        "name": "Integrated Management of Rice Root-Knot Nematode",
        "threat": "Rice_Root_Nematode",
        "treatment_type": "Cultural_and_Physical_Control",
        "recommendation": "Continuous soil flooding in lowland paddies, crop rotation with non-host legumes (mungbean, sesbania), nursery bed solarization, and biological nematicides.",
        "literature": "Bridge, J., Plowright, R.A. & Peng, D. (2005), Nematode Parasites of Rice, in Plant Parasitic Nematodes in Subtropical and Tropical Agriculture, CABI Publishing.",
        "citation": "Bridge, J., Plowright, R.A. & Peng, D. (2005), Nematode Parasites of Rice, in Plant Parasitic Nematodes in Subtropical and Tropical Agriculture, CABI Publishing.",
        "doi": "10.1079/9780851997278.0087"
    },
    "Bacterial_Leaf_Blight": {
        "id": "Control_Bacterial_Leaf_Blight",
        "name": "Integrated Management of Bacterial Leaf Blight",
        "threat": "Bacterial_Leaf_Blight",
        "treatment_type": "Chemical_and_Nutrient_Management",
        "recommendation": "Use certified disease-free seed, balanced nitrogen fertilisation, resistant cultivars (IRBB lines), and preventative copper bactericide application at early tillering.",
        "literature": "CABI Plantwise Knowledge Bank (2014), Management of bacterial leaf blight of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "citation": "CABI Plantwise Knowledge Bank (2014), Management of bacterial leaf blight of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20147801451"
    },
    "False_Smut": {
        "id": "Control_False_Smut",
        "name": "Integrated Management of False Smut",
        "threat": "False_Smut",
        "treatment_type": "Chemical_and_Preventative_Control",
        "recommendation": "Apply triazole fungicides (propiconazole, tebuconazole) at late booting stage, avoid excessive late-season nitrogen, and perform hot-water seed sanitation.",
        "literature": "CABI Plantwise Knowledge Bank (2019), False smut of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "citation": "CABI Plantwise Knowledge Bank (2019), False smut of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20197800044"
    },
    "Rice_Blast": {
        "id": "Control_Rice_Blast",
        "name": "Integrated Management of Rice Blast",
        "threat": "Rice_Blast",
        "treatment_type": "Chemical_and_Genetic_Control",
        "recommendation": "Deploy multi-line resistant varieties, apply silicon soil amendments, avoid excessive nitrogen fertilization, and apply tricyclazole or azoxystrobin at panicle initiation.",
        "literature": "Kunova et al. (2014), Sensitivity of Nonexposed and Exposed Populations of Magnaporthe oryzae from Rice to Tricyclazole and Azoxystrobin, Plant Disease 98(4):512-518; Ou, S.H. (1985), Rice Diseases, CMI.",
        "citation": "Kunova et al. (2014), Sensitivity of Nonexposed and Exposed Populations of Magnaporthe oryzae from Rice to Tricyclazole and Azoxystrobin, Plant Disease 98(4):512-518; Ou, S.H. (1985), Rice Diseases, CMI.",
        "doi": "10.1094/pdis-04-13-0432-re"
    },
    "Rice_Grassy_Stunt": {
        "id": "Control_Rice_Grassy_Stunt",
        "name": "Integrated Management of Rice Grassy Stunt Virus",
        "threat": "Rice_Grassy_Stunt",
        "treatment_type": "Vector_and_Cultural_Control",
        "recommendation": "Manage the brown planthopper (BPH, Nilaparvata lugens) vector with synchronous planting, crop-free fallow periods, conservation of mirid predators (Cyrtorhinus lividipennis), and BPH-resistant cultivars.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor.",
        "citation": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor.",
        "doi": "10.1146/annurev.phyto.34.1.249"
    },
    "Rice_Tungro_Virus": {
        "id": "Control_Rice_Tungro_Virus",
        "name": "Integrated Management of Rice Tungro Virus",
        "threat": "Rice_Tungro_Virus",
        "treatment_type": "Vector_and_Cultural_Control",
        "recommendation": "Control the green leafhopper (GLH, Nephotettix virescens) vector, practice synchronous planting, eradicate ratoon and weed reservoir hosts, and plant tungro-resistant cultivars.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor.",
        "citation": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274; IRRI Rice Doctor.",
        "doi": "10.1146/annurev.phyto.34.1.249"
    }
}

# -------------------------------------------------------------------------
# 4-C & 4-H: Rule Registry with Provable Subsumption & Verified Provenance
# -------------------------------------------------------------------------
RULE_REGISTRY = [
    # ---------------------------------------------------------------------
    # Tier 1: Canonical Pathognomonic Rules (Strict Superset of Tier 2)
    # ---------------------------------------------------------------------
    {
        "id": "SWRL-R02",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier1",
        "name": "Canonical Rice Root-Knot Nematode Diagnosis",
        "antecedents": ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves", "Root_Knot_Swelling", "Deformed_Roots"],
        "consequent_property": "hasConfirmedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Full root galling morphology with secondary vegetative stunting and chlorosis.",
        "literature": "Bridge, J., Plowright, R.A. & Peng, D. (2005), Nematode Parasites of Rice, in Plant Parasitic Nematodes in Subtropical and Tropical Agriculture, CABI Publishing.",
        "doi": "10.1079/9780851997278.0087"
    },
    {
        "id": "SWRL-R06",
        "threat": "Bacterial_Leaf_Blight",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Bacterial Leaf Blight Diagnosis",
        "antecedents": ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips", "Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow", "Uniform_Field_Infection", "Rapid_Disease_Spread"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Initial marginal water-soaked lesions developing systemic vascular yellowing and rapid epidemiological spread.",
        "literature": "CABI Plantwise Knowledge Bank (2014), Management of bacterial leaf blight of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20147801451"
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
        "rationale": "Transformation of individual spikelets into yellow-orange velvety spore balls turning greenish-black during humid heading.",
        "literature": "CABI Plantwise Knowledge Bank (2019), False smut of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20197800044"
    },
    {
        "id": "SWRL-R08",
        "threat": "Rice_Blast",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Blast Diagnosis",
        "antecedents": ["Diamond_Shaped_Lesions", "Necrotic_Spots", "Panicle_Neck_Rot", "Uniform_Field_Infection", "Infected_Seedlings"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Elliptical diamond foliar lesions with necrotic centres accompanied by panicle neck rot caused by Pyricularia oryzae.",
        "literature": "Kunova et al. (2014), Sensitivity of Nonexposed and Exposed Populations of Magnaporthe oryzae from Rice to Tricyclazole and Azoxystrobin, Plant Disease 98(4):512-518; Ou, S.H. (1985), Rice Diseases, CMI.",
        "doi": "10.1094/pdis-04-13-0432-re"
    },
    {
        "id": "SWRL-R09",
        "threat": "Rice_Grassy_Stunt",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Grassy Stunt Virus Diagnosis",
        "antecedents": ["Severe_Stunting", "Excessive_Tillering", "Brown_Planthopper_Present", "No_Panicle_Formation"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Excessive profuse tillering, severe dwarfing, heading suppression, and confirmed Nilaparvata lugens vector presence.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274.",
        "doi": "10.1146/annurev.phyto.34.1.249"
    },
    {
        "id": "SWRL-R10",
        "threat": "Rice_Tungro_Virus",
        "threat_type": "Disease",
        "tier": "tier1",
        "name": "Canonical Rice Tungro Virus Diagnosis",
        "antecedents": ["Stunted_Growth", "Orange_Leaf_Discoloration", "Green_Leafhopper_Present", "Yellowing_Leaves", "Whitehead_Empty_Panicles"],
        "consequent_property": "hasConfirmedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Stunting with characteristic yellow-orange discoloration from leaf tips, empty panicles, and Nephotettix virescens presence.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274.",
        "doi": "10.1146/annurev.phyto.34.1.249"
    },

    # ---------------------------------------------------------------------
    # Tier 2: Relaxed Composite Rules (Partial Scouting, High Sensitivity)
    # ---------------------------------------------------------------------
    {
        "id": "SWRL-R12",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier2",
        "name": "Relaxed Root-Knot Nematode Diagnosis",
        "antecedents": ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Root galling with hooked tips accompanied by above-ground stunting and chlorosis.",
        "literature": "Bridge, J., Plowright, R.A. & Peng, D. (2005), Nematode Parasites of Rice, in Plant Parasitic Nematodes in Subtropical and Tropical Agriculture, CABI Publishing.",
        "doi": "10.1079/9780851997278.0087"
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
        "rationale": "Water-soaked lesions beginning at the leaf tip or margin and progressing longitudinally.",
        "literature": "CABI Plantwise Knowledge Bank (2014), Management of bacterial leaf blight of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20147801451"
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
        "rationale": "Presence of mature and immature chlamydospore smut balls replacing grain kernels.",
        "literature": "CABI Plantwise Knowledge Bank (2019), False smut of rice; Ou, S.H. (1985), Rice Diseases, 2nd ed., CMI.",
        "doi": "10.1079/pwkb.20197800044"
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
        "rationale": "Diamond or spindle-shaped leaf lesions with necrotic centres.",
        "literature": "Kunova et al. (2014), Sensitivity of Nonexposed and Exposed Populations of Magnaporthe oryzae from Rice to Tricyclazole and Azoxystrobin, Plant Disease 98(4):512-518; Ou, S.H. (1985), Rice Diseases, CMI.",
        "doi": "10.1094/pdis-04-13-0432-re"
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
        "rationale": "Severe stunting together with excessive tillering, separating grassy stunt from tungro.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274.",
        "doi": "10.1146/annurev.phyto.34.1.249"
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
        "rationale": "Stunting with characteristic yellow-orange leaf discoloration progressing from the tip.",
        "literature": "Hibino, H. (1996), Biology and epidemiology of rice viruses, Annual Review of Phytopathology 34:249-274.",
        "doi": "10.1146/annurev.phyto.34.1.249"
    },
    # ---------------------------------------------------------------------
    # Tier 2: Diagnostic-sign rules (ruleset v2.4.0)
    # A single sign suffices for `suspected` when (i) the cited source describes it as
    # characteristic of, or specific to, the threat, and (ii) no other in-scope threat uses
    # it. The criterion was fixed from data/noisy_or_parameters.csv before any benchmark was
    # re-run. Signs that fail it: Severe_Stunting and Orange_Leaf_Discoloration (the sources
    # name other viruses or rice orange leaf phytoplasma with the same sign) and
    # Water_Soaked_Lesions (described only as part of a combination). Each composite rule
    # above stays the threat's primary Tier-2 rule and still defines the `possible` grade.
    # ---------------------------------------------------------------------
    {
        "id": "SWRL-R21",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Hook-Shaped Root Gall (Root-Knot Nematode)",
        "antecedents": ["Hook_Like_Root_Swelling"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Hook-shaped galls at the root tips are characteristic of Meloidogyne graminicola.",
        "literature": "Mantelin, S., Bellafiore, S. & Willig, E.B. (2017), Meloidogyne graminicola: a major threat to rice agriculture, Molecular Plant Pathology 18(1):3-15.",
        "doi": "10.1111/mpp.12394"
    },
    {
        "id": "SWRL-R22",
        "threat": "Rice_Root_Nematode",
        "threat_type": "Pest",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Root Galling (Root-Knot Nematode)",
        "antecedents": ["Root_Knot_Swelling"],
        "consequent_property": "hasSuspectedPest",
        "flat_consequent_property": "hasPest",
        "rationale": "Root galls (root swellings) are the characteristic symptom of Meloidogyne graminicola on rice.",
        "literature": "Mantelin, S., Bellafiore, S. & Willig, E.B. (2017), Meloidogyne graminicola: a major threat to rice agriculture, Molecular Plant Pathology 18(1):3-15.",
        "doi": "10.1111/mpp.12394"
    },
    {
        "id": "SWRL-R23",
        "threat": "Rice_Grassy_Stunt",
        "threat_type": "Disease",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Excessive Tillering (Grassy Stunt)",
        "antecedents": ["Excessive_Tillering"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Excess tillering is a symptom specific to RGSV infection; chlorosis and stunting also occur with other tenuiviruses.",
        "literature": "Satoh, K. et al. (2013), Relationship between gene responses and symptoms induced by Rice grassy stunt virus, Frontiers in Microbiology 4:313.",
        "doi": "10.3389/fmicb.2013.00313"
    },
    {
        "id": "SWRL-R24",
        "threat": "False_Smut",
        "threat_type": "Disease",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Yellow-Orange Smut Balls (False Smut)",
        "antecedents": ["Rusty_Grain_Balls"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Yellow to orange smut balls replacing individual grains are the typical symptom of false smut.",
        "literature": "Yang, D., He, N., Huang, F., Jin, Y. & Li, S. (2023), The Genetic Mechanism of the Immune Response to the Rice False Smut (RFS) Fungus Ustilaginoidea virens, Plants 12(4):741.",
        "doi": "10.3390/plants12040741"
    },
    {
        "id": "SWRL-R25",
        "threat": "False_Smut",
        "threat_type": "Disease",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Greenish-Black Smut Balls (False Smut)",
        "antecedents": ["Blackened_Grain_Balls"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Mature greenish-black smut balls on the panicle are the typical symptom of false smut.",
        "literature": "Yang, D., He, N., Huang, F., Jin, Y. & Li, S. (2023), The Genetic Mechanism of the Immune Response to the Rice False Smut (RFS) Fungus Ustilaginoidea virens, Plants 12(4):741.",
        "doi": "10.3390/plants12040741"
    },
    {
        "id": "SWRL-R26",
        "threat": "Rice_Blast",
        "threat_type": "Disease",
        "tier": "tier2",
        "form": "diagnostic_sign",
        "name": "Diamond-Shaped Lesions (Blast)",
        "antecedents": ["Diamond_Shaped_Lesions"],
        "consequent_property": "hasSuspectedDisease",
        "flat_consequent_property": "hasDisease",
        "rationale": "Leaf blast lesions develop a diamond shape with a grey centre and brown margin.",
        "literature": "Ashkani, S. et al. (2015), Molecular Breeding Strategy and Challenges Towards Improvement of Blast Disease Resistance in Rice Crop, Frontiers in Plant Science 6:886.",
        "doi": "10.3389/fpls.2015.00886"
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
    if tier_key == "tier1":
        tier_title = "Tier 1: Canonical Pathognomonic"
    elif r.get("form") == "diagnostic_sign":
        tier_title = "Tier 2: Diagnostic Sign"
    else:
        tier_title = "Tier 2: Relaxed Composite (Partial Observation)"
    formula = " ∧ ".join(f"hasSymptom(?Rice, {a})" for a in r["antecedents"]) + f" → {r['consequent_property']}(?Rice, {threat})"
    entry = {
        "rule_id": r["id"],
        "name": r["name"],
        "tier": tier_title,
        "tier_badge": badge,
        "antecedents": r["antecedents"],
        "formula": formula,
        "rationale": r["rationale"],
        "literature": r.get("literature", ""),
        "doi": r.get("doi", "")
    }
    # "tier1" / "tier2" hold the threat's canonical and primary composite rule (the first in
    # RULE_REGISTRY); "tier2_rules" lists every Tier-2 rule, any of which yields `suspected`.
    SWRL_RULES_METADATA[threat].setdefault(tier_key, entry)
    if tier_key == "tier2":
        SWRL_RULES_METADATA[threat].setdefault("tier2_rules", []).append(entry)


def tier2_rules(threat):
    """All Tier-2 rule metadata entries for `threat`, primary composite rule first."""
    return SWRL_RULES_METADATA.get(threat, {}).get("tier2_rules", [])


def fired_tier2_rules(threat, observed):
    """Tier-2 rules of `threat` whose antecedents are all in `observed`."""
    observed = set(observed)
    return [m for m in tier2_rules(threat) if set(m["antecedents"]) <= observed]


# =========================================================================
# Dynamic Ontology Factory: Isolated World Construction for Ablation
# =========================================================================

def build_ontology(enabled_tiers=None, flat_consequents=False, world=None):
    """
    Constructs a RiceKG OWL 2 DL ontology in an isolated owlready2.World()
    with Defined Classes and symptom taxonomies.

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

        class Observation(Thing):
            namespace = onto

        class Symptom(Observation):
            namespace = onto

        class OrganismSighting(Observation):
            namespace = onto

        class VectorSighting(Observation):
            namespace = onto

        class EpidemiologicalContext(Observation):
            namespace = onto

        # Anatomical Axis
        class LeafSign(Symptom): namespace = onto
        class StemSign(Symptom): namespace = onto
        class RootSign(Symptom): namespace = onto
        class PanicleSign(Symptom): namespace = onto
        class GrainSign(Symptom): namespace = onto
        class WholePlantSign(Symptom): namespace = onto

        # Phenomenological Axis
        class Chlorosis(Symptom): namespace = onto
        class Necrosis(Symptom): namespace = onto
        class Stunting(Symptom): namespace = onto
        class MechanicalDamage(Symptom): namespace = onto
        class GrainAbnormality(Symptom): namespace = onto

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

        class InsectDamageSign(OutOfScopeSign, MechanicalDamage):
            namespace = onto

        # Observation Property Hierarchy (4-A)
        class hasObservation(Rice >> Observation):
            namespace = onto

        class hasSymptom(hasObservation):
            namespace = onto
            domain = [Rice]
            range = [Symptom]

        class hasOrganismSighting(hasObservation):
            namespace = onto
            domain = [Rice]
            range = [OrganismSighting]

        class hasVectorSighting(hasObservation):
            namespace = onto
            domain = [Rice]
            range = [VectorSighting]

        class hasEpidemiologicalContext(hasObservation):
            namespace = onto
            domain = [Rice]
            range = [EpidemiologicalContext]

        # Threat Property Hierarchy
        class hasThreat(Rice >> Threat):
            namespace = onto

        class hasConfirmedThreat(hasThreat):
            namespace = onto
            domain = [Rice]
            range = [Threat]

        class hasSuspectedThreat(hasThreat):
            namespace = onto
            domain = [Rice]
            range = [Threat]

        class hasDisease(hasThreat):
            namespace = onto
            domain = [Rice]
            range = [Disease]

        class hasPest(hasThreat):
            namespace = onto
            domain = [Rice]
            range = [Pest]

        class hasConfirmedPest(hasConfirmedThreat, hasPest):
            namespace = onto
            domain = [Rice]
            range = [Pest]

        class hasSuspectedPest(hasSuspectedThreat, hasPest):
            namespace = onto
            domain = [Rice]
            range = [Pest]

        class hasConfirmedDisease(hasConfirmedThreat, hasDisease):
            namespace = onto
            domain = [Rice]
            range = [Disease]

        class hasSuspectedDisease(hasSuspectedThreat, hasDisease):
            namespace = onto
            domain = [Rice]
            range = [Disease]

        class hasControlTreatment(Threat >> ControlTreatment):
            namespace = onto

        class hasDiagnosticConfidence(Rice >> str):
            namespace = onto

        # Instantiate observations with taxonomy typing (4-A & 4-B)
        obs_individuals = {}
        for s_name in ALL_SYMPTOMS:
            prop_name = OBSERVATION_CATEGORIES.get(s_name, "hasSymptom")
            types_list = []

            if prop_name == "hasOrganismSighting":
                types_list.append(OrganismSighting)
            elif prop_name == "hasVectorSighting":
                types_list.append(VectorSighting)
            elif prop_name == "hasEpidemiologicalContext":
                types_list.append(EpidemiologicalContext)
            else:
                types_list.append(Symptom)
                tax = SYMPTOM_TAXONOMY.get(s_name, {})
                anat = tax.get("anatomical")
                phen = tax.get("phenomenological")
                if anat and hasattr(onto, anat):
                    types_list.append(getattr(onto, anat))
                if phen and hasattr(onto, phen):
                    types_list.append(getattr(onto, phen))
                if s_name in INSECT_DAMAGE_SIGNS:
                    types_list.append(InsectDamageSign)

            inst = types_list[0](s_name, namespace=onto)
            for extra_type in types_list[1:]:
                inst.is_a.append(extra_type)
            obs_individuals[s_name] = inst

        AllDifferent(list(obs_individuals.values()))

        # Instantiate Control Treatments (CQ08)
        control_individuals = {}
        for threat_key, c_data in CONTROL_TREATMENTS.items():
            c_inst = ControlTreatment(c_data["id"], namespace=onto)
            control_individuals[threat_key] = c_inst

        # Instantiate Threat individuals
        threat_individuals = {}
        for p_name in PESTS:
            p_inst = Pest(p_name, namespace=onto)
            threat_individuals[p_name] = p_inst

        for d_name in DISEASES:
            d_inst = Disease(d_name, namespace=onto)
            threat_individuals[d_name] = d_inst

        AllDifferent(list(threat_individuals.values()))
        AllDisjoint([Pest, Disease])

        # Link Control Treatments and Antecedents (CQ08, CQ10)
        for t_name, t_inst in threat_individuals.items():
            if t_name in control_individuals:
                t_inst.hasControlTreatment = [control_individuals[t_name]]
            t1_meta = SWRL_RULES_METADATA.get(t_name, {}).get("tier1", {})
            canonical_ants = t1_meta.get("antecedents", [])
            t_inst.hasSymptom = [obs_individuals[a] for a in canonical_ants if a in obs_individuals]

        # -------------------------------------------------------------
        # Defined Classes for DL Reasoning & Machine-Provable Subsumption (4-C)
        # -------------------------------------------------------------
        for t_name, t_inst in threat_individuals.items():
            meta = SWRL_RULES_METADATA.get(t_name, {})
            t1_ants = meta.get("tier1", {}).get("antecedents", [])
            t2_ants = meta.get("tier2", {}).get("antecedents", [])
            flat_prop = hasPest if t_name in PESTS else hasDisease

            # Tier 2 Suspect Defined Class
            if "tier2" in enabled_tiers:
                susp_prop = flat_prop if flat_consequents else (hasSuspectedPest if t_name in PESTS else hasSuspectedDisease)
                # Union over the threat's Tier-2 rules: any one of them yields `suspected`
                disjuncts = []
                for rule_meta in meta.get("tier2_rules", []):
                    expr = Rice
                    for a in rule_meta["antecedents"]:
                        if a in obs_individuals:
                            expr = expr & hasObservation.value(obs_individuals[a])
                    disjuncts.append(expr)
                susp_expr = disjuncts[0] if len(disjuncts) == 1 else Or(disjuncts)

                susp_cls_name = f"{t_name}Suspect"
                susp_cls = types.new_class(susp_cls_name, (Rice,))
                susp_cls.equivalent_to = [susp_expr]
                susp_cls.is_a.append(susp_prop.value(t_inst))

            # Tier 1 Confirmed Defined Class (Strict superset of Tier 2)
            if "tier1" in enabled_tiers:
                conf_prop = flat_prop if flat_consequents else (hasConfirmedPest if t_name in PESTS else hasConfirmedDisease)
                conf_expr = Rice
                for a in t1_ants:
                    if a in obs_individuals:
                        conf_expr = conf_expr & hasObservation.value(obs_individuals[a])

                conf_cls_name = f"{t_name}Confirmed"
                conf_cls = types.new_class(conf_cls_name, (Rice,))
                conf_cls.equivalent_to = [conf_expr]
                conf_cls.is_a.append(conf_prop.value(t_inst))

            # Tier 3 Possible Defined Class (Qualified Cardinality, 4-D)
            k = max(1, int(math.ceil(len(t2_ants) * POSSIBLE_COVERAGE_THRESHOLD)))
            obs_cls_name = f"{t_name}Observation"
            obs_cls = types.new_class(obs_cls_name, (Observation,))
            for a in t2_ants:
                if a in obs_individuals:
                    obs_individuals[a].is_a.append(obs_cls)

            poss_cls_name = f"{t_name}Possible"
            poss_cls = types.new_class(poss_cls_name, (Rice,))
            poss_cls.equivalent_to = [Rice & hasObservation.min(k, obs_cls)]

        # Backward-compatible SWRL rules according to enabled tiers
        for r_meta in RULE_REGISTRY:
            if r_meta["tier"] in enabled_tiers:
                consequent_prop = r_meta["flat_consequent_property"] if flat_consequents else r_meta["consequent_property"]
                body_atoms = " ^ ".join(f"hasObservation(?Rice, {ant})" for ant in r_meta["antecedents"])
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
# Pellet DL Reasoning Engine & Graded Classification
# =========================================================================

def predict_diseases(symptoms, flat=False, onto=None, include_possible=False):
    """
    Infers rice pests and diseases using Description Logic defined class classification
    and Pellet forward-chaining inference with confidence-graded output.

    :param symptoms: List of symptom identifier strings (English).
    :param flat: If True, returns List[str] of threat names for backwards compatibility.
    :param onto: Optional owlready2.Ontology instance (defaults to global module ontology).
    :param include_possible: When True, also surface threats whose Tier-2 antecedent
        coverage reaches POSSIBLE_COVERAGE_THRESHOLD but whose rule did not fire, graded
        `possible`.
    :return: List of dicts (or List[str] if flat=True).
    """
    target_onto = onto if onto is not None else globals()["onto"]
    plant_id = f"RiceSample_{uuid.uuid4().hex[:8]}"
    new_plant = target_onto.Rice(plant_id, namespace=target_onto)
    created_symptoms = []
    input_symptom_set = set()
    observed_objs = []

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

            observed_objs.append(symptom_obj)
            new_plant.hasObservation.append(symptom_obj)

            # Assign to specific subproperty based on evidence category (4-A)
            prop_name = OBSERVATION_CATEGORIES.get(symptom_name, "hasSymptom")
            if hasattr(new_plant, prop_name):
                getattr(new_plant, prop_name).append(symptom_obj)

        if observed_objs:
            AllDifferent(observed_objs)

        sync_reasoner_pellet(x=target_onto.world, infer_property_values=True, infer_data_property_values=True)

        # Inferred classes & relations
        all_inferred_classes = set(new_plant.is_a) | set(new_plant.INDIRECT_is_a)
        confirmed_names = {t.name for t in getattr(new_plant, "hasConfirmedThreat", [])}
        suspected_names = {t.name for t in getattr(new_plant, "hasSuspectedThreat", [])}
        flat_threat_names = {t.name for t in (list(getattr(new_plant, "hasPest", [])) + list(getattr(new_plant, "hasDisease", [])))}

        # Also inspect direct/indirect defined class membership
        for t_name in ALL_DIAGNOSES:
            conf_cls = getattr(target_onto, f"{t_name}Confirmed", None)
            susp_cls = getattr(target_onto, f"{t_name}Suspect", None)
            if conf_cls and conf_cls in all_inferred_classes:
                confirmed_names.add(t_name)
            elif susp_cls and susp_cls in all_inferred_classes:
                suspected_names.add(t_name)

        all_threat_names = confirmed_names | suspected_names | flat_threat_names

        results = []
        highest_grade = "unstratified"

        for t_name in all_threat_names:
            meta = SWRL_RULES_METADATA.get(t_name, {})
            t1_meta = meta.get("tier1", {})

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
                fired += [m["rule_id"] for m in fired_tier2_rules(t_name, input_symptom_set)]
                highest_grade = "confirmed"
            elif t_name in suspected_names:
                grade = "suspected"
                confidence = 0.9714
                fired = [m["rule_id"] for m in fired_tier2_rules(t_name, input_symptom_set)]
                if highest_grade != "confirmed":
                    highest_grade = "suspected"
            else:
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

        # Assert diagnostic confidence datatype property into the ontology graph (CQ09)
        if results:
            new_plant.hasDiagnosticConfidence = [highest_grade]

        # Negative controls and Out-of-Scope differential diagnosis (4-J & 5-B)
        # Check out-of-scope gates before relaxing to partial/possible evidence
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
            else:
                neg_matched = negative_control_evidence(input_symptom_set)
                if neg_matched:
                    results.append({
                        "threat": NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET,
                        "grade": "out_of_scope",
                        "confidence": 0.0,
                        "antecedent_coverage": 0.0,
                        "fired_rules": [],
                        "matched_symptoms": neg_matched,
                        "missing_symptoms": [],
                        "message": NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE
                    })

        # Partial evidence ('possible' grade): only evaluated if no confirmed/suspected diagnosis
        # and no out-of-scope evidence was triggered
        if include_possible and not results:
            for t_name, meta in SWRL_RULES_METADATA.items():
                if t_name in all_threat_names:
                    continue
                t2_ants = meta.get("tier2", {}).get("antecedents", [])
                if not t2_ants:
                    continue

                poss_cls = getattr(target_onto, f"{t_name}Possible", None)
                matched = [s for s in t2_ants if s in input_symptom_set]
                coverage = round(len(matched) / len(t2_ants), 4)

                if coverage >= POSSIBLE_COVERAGE_THRESHOLD and matched:
                    results.append({
                        "threat": t_name,
                        "grade": "possible",
                        "confidence": round(0.5 * coverage, 4),
                        "antecedent_coverage": coverage,
                        "fired_rules": [],
                        "matched_symptoms": matched,
                        "missing_symptoms": [s for s in t2_ants if s not in input_symptom_set]
                    })
                    if highest_grade not in ("confirmed", "suspected"):
                        highest_grade = "possible"
            if results and highest_grade == "possible":
                new_plant.hasDiagnosticConfidence = [highest_grade]

        # Rank: confirmed first, then antecedent coverage desc, then name
        grade_rank = {"confirmed": 3, "unstratified": 2, "suspected": 2, "possible": 1, "out_of_scope": 0}
        results.sort(key=lambda x: (grade_rank.get(x["grade"], 0), x["antecedent_coverage"], x["threat"]), reverse=True)

        if flat:
            return [item["threat"] for item in results if item.get("grade") != "out_of_scope"]
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
    Preserves compatibility with tests/test_canonical_diagnoses.py, ricekg/evaluate.py, and legacy callers.

    :param symptoms: List of symptom identifier strings (English).
    :param onto: Optional owlready2.Ontology instance.
    :return: List of diagnosed pest and disease names as strings.
    """
    return predict_diseases(symptoms, flat=True, onto=onto)


# -------------------------------------------------------------------------
# Part 7-A: Top-k Differential Diagnosis with Pre-Fixed Deterministic Ordering
# -------------------------------------------------------------------------
TOP_K_GRADE_ORDINAL = {
    "confirmed": 4,
    "suspected": 3,
    "possible": 2,
    "weak": 1,
    "out_of_scope": 0,
}


def predict_top_k(symptoms, k=3, onto=None, include_possible=True, include_weak=False, base_results=None):
    """
    Returns the top-k differential diagnoses ranked by evidence strength.

    Pre-fixed deterministic ordering key (Part 7-A):
    1. Grade ordinal: confirmed (4) > suspected (3) > possible (2) > weak (1) > out_of_scope (0)
    2. Antecedent coverage (descending float)
    3. Diagnostic confidence (descending float)
    4. Threat identifier (ascending alphabetical deterministic tie-break)

    Rules:
    - Only in-scope diseases and pests are included in the ranked differential.
    - Insect out-of-scope (5-B) and negative control (4-J) responses are never ranked
      alongside diseases; if only out-of-scope evidence exists, candidates list is empty.
    - If include_weak=True, candidate threats with coverage > 0 but below the possible
      threshold (0.50) are included with grade="weak". By default, include_weak=False.
    - Returns at most k candidates. If no threat has evidence, returns [].

    :param symptoms: List of observed symptom strings.
    :param k: Maximum number of differential candidates to return (default 3).
    :param onto: Optional loaded owlready2 ontology instance.
    :param include_possible: Whether to include possible-grade candidates (default True).
    :param include_weak: Whether to include weak-grade candidates (<50% coverage, default False).
    :param base_results: Optional pre-computed output of predict_diseases to avoid redundant Pellet reasoning.
    :return: List of dicts representing top-k candidates, each containing:
             threat, grade, confidence, antecedent_coverage, matched_symptoms,
             missing_symptoms, fired_rules, rank.
    """
    if k <= 0:
        return []

    input_symptoms = [str(s).strip() for s in (symptoms or []) if str(s).strip()]
    input_symptom_set = set(input_symptoms)
    if not input_symptom_set:
        return []

    # Get baseline predictions (includes confirmed, suspected, and optional possible)
    if base_results is None:
        base_results = predict_diseases(input_symptoms, include_possible=include_possible, onto=onto)
    else:
        base_results = [dict(c) for c in base_results]
        # If include_possible is requested but base_results came from standard unrelaxed prediction,
        # evaluate possible candidates here if no confirmed/suspected/out_of_scope fired.
        has_definitive = any(c.get("grade") in ("confirmed", "suspected", "out_of_scope") for c in base_results)
        if include_possible and not has_definitive:
            existing = {c["threat"] for c in base_results}
            for t_name, meta in SWRL_RULES_METADATA.items():
                if t_name in existing:
                    continue
                t2_ants = meta.get("tier2", {}).get("antecedents", [])
                if not t2_ants:
                    continue
                matched = [s for s in t2_ants if s in input_symptom_set]
                cov = round(len(matched) / len(t2_ants), 4)
                if cov >= POSSIBLE_COVERAGE_THRESHOLD and matched:
                    base_results.append({
                        "threat": t_name,
                        "grade": "possible",
                        "confidence": round(0.5 * cov, 4),
                        "antecedent_coverage": cov,
                        "fired_rules": [],
                        "matched_symptoms": matched,
                        "missing_symptoms": [s for s in t2_ants if s not in input_symptom_set]
                    })

    # Check for out-of-scope evidence: if out-of-scope gate fired, no disease candidate is ranked
    has_out_of_scope = any(c.get("grade") == "out_of_scope" for c in base_results)
    if has_out_of_scope:
        return []

    # Filter strictly for in-scope threats
    candidates = [
        dict(c) for c in base_results
        if c.get("threat") in ALL_DIAGNOSES and c.get("grade") != "out_of_scope"
    ]

    # Optional inclusion of weak candidates (<50% antecedent coverage)
    if include_weak and not has_out_of_scope:
        existing_threats = {c["threat"] for c in candidates}
        for t_name in ALL_DIAGNOSES:
            if t_name not in existing_threats:
                meta = SWRL_RULES_METADATA.get(t_name, {})
                t2_ants = meta.get("tier2", {}).get("antecedents", [])
                if not t2_ants:
                    continue
                matched = [s for s in t2_ants if s in input_symptom_set]
                if matched:
                    cov = round(len(matched) / len(t2_ants), 4)
                    if cov < POSSIBLE_COVERAGE_THRESHOLD:
                        candidates.append({
                            "threat": t_name,
                            "grade": "weak",
                            "confidence": round(0.2 * cov, 4),
                            "antecedent_coverage": cov,
                            "fired_rules": [],
                            "matched_symptoms": matched,
                            "missing_symptoms": [s for s in t2_ants if s not in input_symptom_set]
                        })

    # Sort strictly using the pre-fixed deterministic ordering key
    candidates.sort(
        key=lambda x: (
            -TOP_K_GRADE_ORDINAL.get(x.get("grade"), 0),
            -float(x.get("antecedent_coverage", 0.0)),
            -float(x.get("confidence", 0.0)),
            str(x.get("threat", ""))
        )
    )

    top_k = candidates[:k]
    for idx, item in enumerate(top_k, 1):
        item["rank"] = idx

    return top_k


# =========================================================================
# Explainable AI (XAI): Formal SWRL Rule Knowledge Representation & Traces
# =========================================================================

def _tier_label(rule):
    """Human-readable tier label of a trace entry (None gives the composite label)."""
    if rule and rule["tier"] == "tier1":
        return "Tier 1 (Canonical)"
    if rule and rule.get("form") == "diagnostic_sign":
        return "Tier 2 (Diagnostic Sign)"
    return "Tier 2 (Relaxed Composite)"


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

    diagnosed_map = {}
    if diagnosed_threats:
        for item in diagnosed_threats:
            if isinstance(item, dict) and "threat" in item:
                diagnosed_map[item["threat"]] = item
            else:
                diagnosed_map[str(item)] = {"threat": str(item), "grade": "confirmed", "confidence": 1.0}

    # Evaluate all production rules in standard stratified execution order (Tier 1 then Tier 2)
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
            "form": rule.get("form", "composite"),
            "consequent_property": rule["consequent_property"],
            "antecedents_count": len(antecedents),
            "satisfied_count": len(satisfied),
            "unmet_count": len(unmet),
            "status": "FIRED" if is_fired else "UNSATISFIED",
            "coverage_percentage": coverage_pct,
            "antecedents": antecedents,
            "satisfied_antecedents": satisfied,
            "unmet_antecedents": unmet,
            "formula": " ∧ ".join(f"hasObservation(?Rice, {a})" for a in antecedents) + f" → {rule['consequent_property']}(?Rice, {threat})",
            "rationale": rule.get("rationale", ""),
            "literature": rule.get("literature", ""),
            "doi": rule.get("doi", "")
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
        # The Tier-2 rule that fired (primary composite first), else the primary composite
        t2_all = [r for r in threat_rules if r["tier"] == "tier2"]
        t2_rule = next((r for r in t2_all if r["status"] == "FIRED"), t2_all[0] if t2_all else None)

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
                    "predicate": f"hasObservation(Rice_Sample, {ant})",
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
                "tier": _tier_label(active_rule),
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


def explain_abstention(selected_symptoms, k=2):
    """
    Explains why no diagnosis was reached: the in-scope rules closest to firing, with the
    antecedents already observed and those still missing, and the observed terms that no rule
    uses. Pure set arithmetic over RULE_REGISTRY; it never changes a diagnosis.

    Expert raters judged silent abstentions the least useful output (usefulness 1.98/5), so an
    abstention should say which additional observation would settle the case.

    :param selected_symptoms: List of observed symptom identifiers.
    :param k: Maximum number of nearest rules to return.
    :return: Dict with `nearest_rules` (list) and `unused_observations` (list).
    """
    observed = set(selected_symptoms)
    candidates = []
    for rule in RULE_REGISTRY:
        ants = set(rule["antecedents"])
        matched = ants & observed
        if not matched:
            continue
        candidates.append({
            "threat": rule["threat"],
            "rule_id": rule["id"],
            "tier": rule["tier"],
            "coverage": round(len(matched) / len(ants), 4),
            "matched_symptoms": sorted(matched),
            "missing_symptoms": sorted(ants - observed),
        })
    # Closest first: fewest missing antecedents, then highest coverage; Tier-2 before Tier-1
    # on ties because it is the rule that would fire first.
    candidates.sort(key=lambda c: (len(c["missing_symptoms"]), -c["coverage"], c["tier"] != "tier2", c["threat"]))
    nearest, seen = [], set()
    for c in candidates:
        if c["threat"] not in seen:
            seen.add(c["threat"])
            nearest.append(c)
        if len(nearest) == k:
            break
    used = {a for r in RULE_REGISTRY for a in r["antecedents"]}
    return {"nearest_rules": nearest, "unused_observations": sorted(observed - used)}


def explain_diagnoses(selected_symptoms, diagnosed_threats):
    """
    Generates explainable deductive proof traces for all inferred diagnoses.
    Identifies whether Tier 1 (canonical) or Tier 2 (relaxed) rule fired,
    and maps observed vs unobserved rule antecedents.

    :param selected_symptoms: List of user-selected symptom ID strings.
    :param diagnosed_threats: List of diagnosed threat key strings or dicts.
    :return: Dictionary mapping threat key to proof trace explanation.
    """
    selected_set = set(selected_symptoms)
    explanations = {}

    for item in diagnosed_threats:
        threat_key = item["threat"] if isinstance(item, dict) and "threat" in item else str(item)
        meta = SWRL_RULES_METADATA.get(threat_key)
        if not meta:
            if threat_key == INSECT_OUT_OF_SCOPE_TARGET:
                explanations[threat_key] = {
                    "rule_id": "OUT-OF-SCOPE-INSECT",
                    "name": "Insect Damage (Outside Diagnostic Scope)",
                    "tier": "Scope Boundary Assessment",
                    "tier_badge": "tier-relaxed",
                    "formula": f"≥{INSECT_GATE_MIN_SIGNS} distinct insect-specific signs ∧ no in-scope rule fires → OutOfScope(?Rice)",
                    "rationale": INSECT_OUT_OF_SCOPE_RESPONSE,
                    "antecedents_status": [{"symptom": s, "symptom_name": s.replace("_", " "), "observed": True} for s in insect_damage_evidence(selected_symptoms)]
                }
                continue
            elif threat_key == NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET:
                explanations[threat_key] = {
                    "rule_id": "OUT-OF-SCOPE-DISEASE",
                    "name": "Non-Modeled Pathogen Signs (Outside Diagnostic Scope)",
                    "tier": "Scope Boundary Assessment",
                    "tier_badge": "tier-relaxed",
                    "formula": "NonModeledPathogenSign(?s) ∧ hasObservation(?Rice, ?s) ∧ no in-scope rule fires → NegativeControl(?Rice)",
                    "rationale": NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE,
                    "antecedents_status": [{"symptom": s, "symptom_name": s.replace("_", " "), "observed": True} for s in negative_control_evidence(selected_symptoms)]
                }
                continue

            explanations[threat_key] = {
                "rule_id": "DL-CLASSIFICATION",
                "name": f"Deductive Classification for {threat_key.replace('_', ' ')}",
                "tier": "Description Logic Inference",
                "tier_badge": "tier-relaxed",
                "formula": f"hasObservation(?Rice, ...) → {threat_key}(?Rice)",
                "rationale": "Inferred via Pellet description logic tableau classification.",
                "antecedents_status": [{"symptom": s, "symptom_name": s.replace("_", " "), "observed": True} for s in selected_symptoms]
            }
            continue

        # Check if Tier 1 (canonical) rule fully satisfied
        t1 = meta.get("tier1", {})
        t2 = meta.get("tier2", {})

        if isinstance(item, dict) and "grade" in item:
            t1_satisfied = (item["grade"] == "confirmed")
        else:
            t1_satisfied = all(ant in selected_set for ant in t1.get("antecedents", []))

        fired_t2 = fired_tier2_rules(threat_key, selected_set)
        active_rule = t1 if (t1_satisfied and t1) else (fired_t2[0] if fired_t2 else t2)

        ant_status = []
        for ant in active_rule.get("antecedents", []):
            ant_status.append({
                "symptom": ant,
                "symptom_name": ant.replace("_", " "),
                "observed": ant in selected_set
            })

        explanations[threat_key] = {
            "rule_id": active_rule.get("rule_id", ""),
            "name": active_rule.get("name", ""),
            "tier": active_rule.get("tier", ""),
            "tier_badge": active_rule.get("tier_badge", "tier-relaxed"),
            "formula": active_rule.get("formula", ""),
            "rationale": active_rule.get("rationale", ""),
            "literature": active_rule.get("literature", ""),
            "doi": active_rule.get("doi", ""),
            "antecedents": active_rule.get("antecedents", []),
            "antecedents_status": ant_status,
            "rule_level": "Tier 1 (Canonical)" if t1_satisfied else (
                "Tier 2 (Diagnostic Sign)" if active_rule.get("tier") == "Tier 2: Diagnostic Sign" else "Tier 2 (Relaxed Composite)")
        }

    return explanations

