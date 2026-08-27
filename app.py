"""
Flask Web Application for RiceKG: Rice Pest and Disease Diagnostic Expert System.
"""

import os
import json
import time
from flask import Flask, request, render_template, redirect, url_for
from model import predict_diseases

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SYMPTOM_CATEGORIES = [
    {
        "category_id": "leaf",
        "category_name": "Leaf & Foliage Symptoms",
        "icon": "fa-leaf",
        "description": "Foliar lesions, chlorosis, hopperburn, and leaf chewing damage",
        "symptoms": [
            {"id": "Yellowing_Leaf_Veins", "name": "Yellowing Leaf Veins", "description": "Chlorotic yellow stripes along leaf vein ridges"},
            {"id": "Leaf_Discoloration_Yellow", "name": "Leaf Discoloration (Yellow)", "description": "Generalized yellowing across the leaf blade"},
            {"id": "Yellowing_Leaf_Tips", "name": "Yellowing Leaf Tips", "description": "Tip-burning and apical foliar yellowing"},
            {"id": "Rapid_Disease_Spread", "name": "Rapid Disease Spread", "description": "Fast propagation to adjacent tillers and hills"},
            {"id": "Broad_Leaf_Damage", "name": "Broad Leaf Damage", "description": "Extensive defoliation across broad leaf surfaces"},
            {"id": "Leaf_Chewing_Damage", "name": "Leaf Chewing Damage", "description": "Notched, serrated, or chewed leaf margins"},
            {"id": "Leaf_Margin_Sap_Sucking", "name": "Leaf Margin Sap Sucking", "description": "Sap extraction puncture marks along margins"},
            {"id": "Localized_Leaf_Yellowing", "name": "Localized Leaf Yellowing", "description": "Discrete yellow chlorotic patches on leaves"},
            {"id": "Diamond_Shaped_Lesions", "name": "Diamond-Shaped Lesions", "description": "Spindle/elliptical lesions with grayish centers"},
            {"id": "Hopperburn_Drying", "name": "Hopperburn Drying", "description": "Severe foliar wilting and drying from sap loss"},
            {"id": "Circular_Hopperburn_Patches", "name": "Circular Hopperburn Patches", "description": "Concentric circular dying zones in the field"},
            {"id": "Blackened_Feeding_Punctures", "name": "Blackened Feeding Punctures", "description": "Dark stylet feeding punctures on leaf sheaths"},
            {"id": "Yellowing_Leaves", "name": "Yellowing Leaves", "description": "Yellow to orange discoloration on mature leaves"},
            {"id": "Plant_Yellowing", "name": "Plant Yellowing", "description": "Generalized chlorosis across the entire foliage"}
        ]
    },
    {
        "category_id": "stem",
        "category_name": "Stem & Tiller Symptoms",
        "icon": "fa-seedling",
        "description": "Culm boring, internal frass, deadhearts, and tillering anomalies",
        "symptoms": [
            {"id": "Frass_In_Stem", "name": "Frass in Stem", "description": "Sawdust-like larval excrement inside central culm"},
            {"id": "Bore_Holes_In_Stem", "name": "Bore Holes in Stem", "description": "Visible entry/exit holes on outer stem surface"},
            {"id": "Deadheart_Seedling", "name": "Deadheart Seedling", "description": "Drying and death of central vegetative shoot"},
            {"id": "Easily_Pulled_Tillers", "name": "Easily Pulled Tillers", "description": "Damaged tillers detach effortlessly when pulled"},
            {"id": "Severe_Stunting", "name": "Severe Stunting", "description": "Drastic height reduction and excessive tillering"},
            {"id": "Stunted_Growth", "name": "Stunted Growth", "description": "Impaired vertical growth and general lack of vigor"}
        ]
    },
    {
        "category_id": "panicle",
        "category_name": "Panicle & Grain Symptoms",
        "icon": "fa-wheat-awn",
        "description": "Smut spore balls, chalky empty grains, neck rot, and severed panicles",
        "symptoms": [
            {"id": "Severed_Panicles", "name": "Severed Panicles", "description": "Panicle stalks cut or severed by insect mandibles"},
            {"id": "Whitehead_Empty_Panicles", "name": "Whitehead / Empty Panicles", "description": "Bleached, completely empty, upright panicles"},
            {"id": "Rotten_Panicles", "name": "Rotten Panicles", "description": "Dark decay and necrotic breakdown of panicles"},
            {"id": "Empty_Grains", "name": "Empty / Chalky Grains", "description": "Spikelets lacking filled endosperm or chalky grains"},
            {"id": "Rusty_Grain_Balls", "name": "Rusty Grain Balls", "description": "Orange/yellow velvet spore balls replacing grains"},
            {"id": "Blackened_Grain_Balls", "name": "Blackened Grain Balls", "description": "Mature greenish-black fungal smut balls"},
            {"id": "Rainy_Season_Outbreak", "name": "Rainy Season Outbreak", "description": "Severe panicle infection during high rainfall"},
            {"id": "Uniform_Field_Infection", "name": "Uniform Field Infection", "description": "Homogeneous symptom spread across the field"},
            {"id": "Slight_Panicle_Infection", "name": "Slight Panicle Infection", "description": "Isolated floret infections on panicle branches"},
            {"id": "Milky_Stage_Vulnerability", "name": "Milky Stage Vulnerability", "description": "Damage concentrated during liquid grain filling"},
            {"id": "Panicle_Neck_Rot", "name": "Panicle Neck Rot", "description": "Brown to black necrotic lesion at panicle node/neck"},
            {"id": "No_Panicle_Formation", "name": "No Panicle Formation", "description": "Complete suppression of floral heading"}
        ]
    },
    {
        "category_id": "root",
        "category_name": "Root System Symptoms",
        "icon": "fa-diagram-project",
        "description": "Root swelling, galls, cortical necrosis, and tip deformations",
        "symptoms": [
            {"id": "Hook_Like_Root_Swelling", "name": "Hook-Like Root Swelling", "description": "Characteristic curling and galling at root tips"},
            {"id": "Root_Knot_Swelling", "name": "Root Knot Swelling", "description": "Nodular galls and swellings along root axes"},
            {"id": "Deformed_Roots", "name": "Deformed Roots", "description": "Abnormal root branching, shortening, and distortion"},
            {"id": "Necrotic_Spots", "name": "Necrotic Spots on Roots", "description": "Dark brown to black necrotic lesions on root cortex"}
        ]
    },
    {
        "category_id": "vector",
        "category_name": "Entomological Signs & Vectors",
        "icon": "fa-bug",
        "description": "Direct insect sightings, egg clusters, nymphs, and vectors",
        "symptoms": [
            {"id": "Brown_Nymphs", "name": "Brown Nymphs Observed", "description": "Immature brown grasshopper or planthopper nymphs"},
            {"id": "Yellow_Nymphs", "name": "Yellow Nymphs Observed", "description": "Early instar yellowish insect nymphs"},
            {"id": "Eggs_On_Plant", "name": "Egg Clusters on Plant", "description": "Egg masses deposited on leaves or leaf sheaths"},
            {"id": "Nymphs_Present", "name": "Nymphs Present", "description": "Active nymph colonies on stems or leaves"},
            {"id": "Adult_Insects_Present", "name": "Adult Insects Present", "description": "Winged adult bugs or grasshoppers in the field"},
            {"id": "Brown_Planthopper_Present", "name": "Brown Planthopper Present", "description": "Direct sighting of Nilaparvata lugens colonies"},
            {"id": "Green_Leafhopper_Present", "name": "Green Leafhopper Present", "description": "Direct sighting of Nephotettix virescens vectors"},
            {"id": "Infected_Seedlings", "name": "Infected Seedlings", "description": "Early disease manifestations in nursery beds"},
            {"id": "Random_Feeding_Pattern", "name": "Random Feeding Pattern", "description": "Irregular feeding punctures scattered on grains/leaves"}
        ]
    }
]

# Build lookup maps
SYMPTOM_NAME_MAP = {}
for cat in SYMPTOM_CATEGORIES:
    for sym in cat["symptoms"]:
        SYMPTOM_NAME_MAP[sym["id"]] = sym["name"]

def load_threat_catalog():
    data_path = os.path.join(BASE_DIR, 'static', 'data.json')
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

THREAT_CATALOG = load_threat_catalog()
THREAT_MAP = {}
for t in THREAT_CATALOG:
    if "key" in t:
        THREAT_MAP[t["key"]] = t


@app.route("/")
def index_page():
    """Renders the main diagnostic form."""
    return render_template(
        "index.html",
        symptom_categories=SYMPTOM_CATEGORIES,
        total_symptoms=sum(len(c["symptoms"]) for c in SYMPTOM_CATEGORIES)
    )


@app.route('/result', methods=['GET', 'POST'])
def diagnose():
    """Handles symptom selection and executes ontology-based reasoning."""
    if request.method == 'POST':
        start_time = time.time()
        selected_symptoms = request.form.getlist('mycheckbox')
        print(f"[Diagnosis Request] Selected symptoms ({len(selected_symptoms)}):", selected_symptoms)
        
        diagnosed_results = predict_diseases(selected_symptoms)
        elapsed_time = round(time.time() - start_time, 3)
        print(f"[Diagnosis Result] Inferred in {elapsed_time}s:", diagnosed_results)

        # Enrich diagnosis details
        enriched_diagnoses = []
        for diag_name in diagnosed_results:
            threat_info = THREAT_MAP.get(diag_name)
            if not threat_info:
                for t in THREAT_CATALOG:
                    if t.get("key") == diag_name or diag_name in t.get("nama", ""):
                        threat_info = t
                        break

            if threat_info:
                enriched_diagnoses.append(threat_info)
            else:
                enriched_diagnoses.append({
                    "key": diag_name,
                    "nama": diag_name.replace("_", " "),
                    "nama_latin": "Scientific identification confirmed via SWRL",
                    "kategori": "Biotic Threat",
                    "icon": "🌾",
                    "badge_class": "badge-disease",
                    "organ_target": "Rice Crop",
                    "deskripsi": "Inferred successfully via RiceKG SWRL description logic reasoning.",
                    "pengendalian_ipm": ["Consult local agricultural extension officers for localized IPM measures."]
                })

        return render_template(
            'result.html',
            penyakit=diagnosed_results,
            diagnoses=enriched_diagnoses,
            selected_symptoms=selected_symptoms,
            symptom_name_map=SYMPTOM_NAME_MAP,
            elapsed_time=elapsed_time
        )
    return redirect(url_for('index_page'))


@app.route("/about/")
def about():
    """Renders about page."""
    return render_template("about.html")


@app.route("/turtle")
@app.route("/threats")
@app.route("/knowledge-base")
def turtle():
    """Biotic threats catalog endpoint."""
    return render_template("penyu.html", threats=THREAT_CATALOG)

    
if __name__ == "__main__":
    app.run(debug=True)