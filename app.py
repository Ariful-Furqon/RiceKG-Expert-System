import os
import csv
import json
import time
from flask import Flask, request, render_template, redirect, url_for, jsonify
from ricekg import model
from ricekg.model import predict_diseases, predict_diseases_flat, predict_top_k, explain_diagnoses, get_derivation_trace, SWRL_RULES_METADATA

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

# Labels and descriptions come from the ontology's curated term definitions, so the UI
# shows the same operational definition an annotator applies.
def load_term_definitions():
    with open(os.path.join(BASE_DIR, "ontology", "term_definitions.csv"), encoding="utf-8", newline="") as f:
        return {row["term"]: row for row in csv.DictReader(f)}

TERM_DEFINITIONS = load_term_definitions()
for cat in SYMPTOM_CATEGORIES:
    for sym in cat["symptoms"]:
        row = TERM_DEFINITIONS.get(sym["id"])
        if row:
            sym["name"] = row["label_en"][:1].upper() + row["label_en"][1:]
            sym["description"] = row["definition"]

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

# Benchmark Preset Field Scenarios for Rapid Reviewer Demonstration
BENCHMARK_SCENARIOS = [
    {
        "id": "scenario_nematode",
        "title": "Rice Root-Knot Nematode",
        "category": "Endoparasitic Nematode (Tier 1/2)",
        "badge_class": "badge-pest",
        "icon": "🪱",
        "description": "Characteristic hook-like terminal root swelling, root galls, and vegetative stunting.",
        "symptoms": ["Hook_Like_Root_Swelling", "Stunted_Growth", "Yellowing_Leaves"]
    },
    {
        "id": "scenario_blb",
        "title": "Bacterial Leaf Blight",
        "category": "Phytopathogenic Bacteria",
        "badge_class": "badge-disease",
        "icon": "🍃",
        "description": "Chlorotic yellow stripes along leaf vein ridges with uniform field spread.",
        "symptoms": ["Yellowing_Leaf_Veins", "Leaf_Discoloration_Yellow", "Uniform_Field_Infection"]
    },
    {
        "id": "scenario_coinfection",
        "title": "Dual Co-Infection (BLB + Blast)",
        "category": "Multi-Threat Co-Occurrence",
        "badge_class": "badge-disease",
        "icon": "⚡",
        "description": "Simultaneous presence of bacterial vascular blight and fungal blast lesions.",
        "symptoms": ["Yellowing_Leaf_Veins", "Uniform_Field_Infection", "Panicle_Neck_Rot", "Diamond_Shaped_Lesions"]
    },
    {
        "id": "scenario_insect_damage",
        "title": "Insect Damage (Out of Scope)",
        "category": "Differential Diagnosis Gate",
        "badge_class": "badge-neutral",
        "icon": "🦗",
        "description": "Defoliation and severed panicles; triggers explicit out-of-scope differential response.",
        "symptoms": ["Severed_Panicles", "Leaf_Chewing_Damage"]
    },
    {
        "id": "scenario_negative",
        "title": "Negative Control (Abiotic Stress)",
        "category": "Physiological Chlorosis",
        "badge_class": "badge-disease",
        "icon": "🌱",
        "description": "General nitrogen deficiency symptoms (no biotic SWRL rule and no insect gate should fire).",
        "symptoms": ["Plant_Yellowing", "Yellowing_Leaf_Tips"]
    }
]


@app.route("/")
def index_page():
    """Renders the main diagnostic form with quick-load demonstration scenarios."""
    return render_template(
        "index.html",
        symptom_categories=SYMPTOM_CATEGORIES,
        total_symptoms=sum(len(c["symptoms"]) for c in SYMPTOM_CATEGORIES),
        scenarios=BENCHMARK_SCENARIOS
    )


@app.route('/result', methods=['GET', 'POST'])
def diagnose():
    """Handles symptom selection and executes ontology-based reasoning with XAI proof traces."""
    if request.method == 'POST':
        start_time = time.time()
        selected_symptoms = request.form.getlist('mycheckbox')
        print(f"[Diagnosis Request] Selected symptoms ({len(selected_symptoms)}):", selected_symptoms)
        
        graded_results = predict_diseases(selected_symptoms)
        diagnosed_results = [item["threat"] for item in graded_results]
        grade_map = {item["threat"]: item for item in graded_results}
        elapsed_time = round(time.time() - start_time, 3)
        print(f"[Diagnosis Result] Inferred in {elapsed_time}s:", diagnosed_results)

        # Generate Explainable AI (XAI) deductive proof traces
        explanations = explain_diagnoses(selected_symptoms, diagnosed_results)

        # Enrich diagnosis details
        enriched_diagnoses = []
        for diag_name in diagnosed_results:
            threat_info = THREAT_MAP.get(diag_name)
            if not threat_info:
                for t in THREAT_CATALOG:
                    if t.get("key") == diag_name or diag_name in t.get("nama", ""):
                        threat_info = t
                        break

            item_grade = grade_map.get(diag_name, {})
            if threat_info:
                threat_copy = dict(threat_info)
                threat_copy["grade"] = item_grade.get("grade", "confirmed")
                threat_copy["confidence"] = item_grade.get("confidence", 1.0)
                threat_copy["fired_rules"] = item_grade.get("fired_rules", [])
                threat_copy["explanation"] = explanations.get(diag_name, {})
                enriched_diagnoses.append(threat_copy)
            else:
                enriched_diagnoses.append({
                    "key": diag_name,
                    "nama": diag_name.replace("_", " "),
                    "nama_latin": "Scientific identification confirmed via SWRL",
                    "kategori": "Biotic Threat",
                    "grade": item_grade.get("grade", "confirmed"),
                    "confidence": item_grade.get("confidence", 1.0),
                    "fired_rules": item_grade.get("fired_rules", []),
                    "icon": "🌾",
                    "badge_class": "badge-disease",
                    "organ_target": "Rice Crop",
                    "deskripsi": "Inferred successfully via RiceKG SWRL description logic reasoning.",
                    "pengendalian_ipm": ["Consult local agricultural extension officers for localized IPM measures."],
                    "explanation": explanations.get(diag_name, {})
                })

        derivation_trace = get_derivation_trace(selected_symptoms, graded_results)

        # Part 7-A: Top-k Differential Diagnosis
        top_k_differential = model.predict_top_k(
            selected_symptoms, k=3, include_possible=True, base_results=graded_results
        )
        for cand in top_k_differential:
            t_key = cand["threat"]
            threat_info = THREAT_MAP.get(t_key)
            if not threat_info:
                for t in THREAT_CATALOG:
                    if t.get("key") == t_key or t_key in t.get("nama", ""):
                        threat_info = t
                        break
            cand["name"] = threat_info.get("nama", t_key.replace("_", " ")) if threat_info else t_key.replace("_", " ")
            cand["scientific_name"] = threat_info.get("nama_latin", "") if threat_info else ""

        return render_template(
            'result.html',
            penyakit=diagnosed_results,
            diagnoses=enriched_diagnoses,
            differential=top_k_differential,
            explanations=explanations,
            derivation_trace=derivation_trace,
            selected_symptoms=selected_symptoms,
            symptom_name_map=SYMPTOM_NAME_MAP,
            elapsed_time=elapsed_time
        )
    return redirect(url_for('index_page'))


@app.route("/about/")
def about():
    """Renders about page."""
    return render_template("about.html")


@app.route("/threats")
@app.route("/knowledge-base")
def threat_catalog():
    """Renders the biotic threats knowledge base catalog."""
    return render_template("threats.html", threats=THREAT_CATALOG)


# =========================================================================
# RESTful API Endpoints (v1)
# =========================================================================

@app.route("/api/v1/diagnose", methods=["POST"])
def api_diagnose():
    """
    REST API endpoint for RiceKG automated diagnosis.
    Accepts JSON: {"symptoms": ["Symptom_1", "Symptom_2", ...]}
    Returns JSON with inferred biotic threats, XAI proof traces, and reference management measures.
    """
    data = request.get_json(silent=True)
    if not data or "symptoms" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'symptoms' array in JSON request body."
        }), 400

    symptoms = data.get("symptoms", [])
    if not isinstance(symptoms, list):
        return jsonify({
            "status": "error",
            "message": "'symptoms' must be a JSON array of symptom identifier strings."
        }), 400

    start_time = time.time()
    graded_results = predict_diseases(symptoms)
    diagnosed_results = [item["threat"] for item in graded_results]
    grade_map = {item["threat"]: item for item in graded_results}
    elapsed_time = round(time.time() - start_time, 3)

    explanations = explain_diagnoses(symptoms, diagnosed_results)

    enriched_diagnoses = []
    for diag_name in diagnosed_results:
        threat_info = THREAT_MAP.get(diag_name)
        if not threat_info:
            for t in THREAT_CATALOG:
                if t.get("key") == diag_name or diag_name in t.get("nama", ""):
                    threat_info = t
                    break

        item_grade = grade_map.get(diag_name, {})
        item = {
            "key": diag_name,
            "name": threat_info.get("nama", diag_name.replace("_", " ")) if threat_info else diag_name,
            "scientific_name": threat_info.get("nama_latin", "Scientific ID confirmed via SWRL") if threat_info else "",
            "category": threat_info.get("kategori", "Biotic Threat") if threat_info else "Biotic Threat",
            "grade": item_grade.get("grade", "confirmed"),
            "confidence": item_grade.get("confidence", 1.0),
            "fired_rules": item_grade.get("fired_rules", []),
            "target_organ": threat_info.get("organ_target", "Rice Plant") if threat_info else "Rice Plant",
            "description": threat_info.get("deskripsi", "") if threat_info else "",
            "ipm_prescriptions": threat_info.get("pengendalian_ipm", []) if threat_info else [],
            "explanation": explanations.get(diag_name, {})
        }
        enriched_diagnoses.append(item)

    # Part 7-A: Top-k Differential Diagnosis
    top_k_differential = model.predict_top_k(
        symptoms, k=3, include_possible=True, base_results=graded_results
    )
    for cand in top_k_differential:
        t_key = cand["threat"]
        threat_info = THREAT_MAP.get(t_key)
        if not threat_info:
            for t in THREAT_CATALOG:
                if t.get("key") == t_key or t_key in t.get("nama", ""):
                    threat_info = t
                    break
        cand["name"] = threat_info.get("nama", t_key.replace("_", " ")) if threat_info else t_key.replace("_", " ")
        cand["scientific_name"] = threat_info.get("nama_latin", "") if threat_info else ""

    return jsonify({
        "status": "success",
        "query": {
            "symptoms_count": len(symptoms),
            "symptoms": symptoms
        },
        "inference": {
            "reasoner": "Pellet DL (Tableau Forward-Chaining)",
            "execution_time_seconds": elapsed_time,
            "diagnoses_count": len(diagnosed_results)
        },
        "diagnoses": enriched_diagnoses,
        "differential_diagnosis": top_k_differential,
        "explanations": explanations
    }), 200


@app.route("/api/v2/diagnose", methods=["POST"])
def api_diagnose_v2():
    """
    REST API v2 endpoint for RiceKG automated diagnosis with full Explainable AI (XAI)
    derivation trace, rule evaluation order, unsatisfied antecedents, and formal proof trees.

    Accepts JSON:
    {
        "symptoms": ["Symptom_1", "Symptom_2", ...],
        "include_possible": false
    }

    Returns JSON with:
    - Diagnosed threats with grades (confirmed, suspected, possible)
    - Full derivation trace per threat (rules fired, candidate rules, unmet symptoms)
    - Hierarchical Horn-clause Modus Ponens proof trees
    - Global derivation execution summary
    """
    data = request.get_json(silent=True)
    if not data or "symptoms" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing 'symptoms' array in JSON request body."
        }), 400

    symptoms = data.get("symptoms", [])
    if not isinstance(symptoms, list):
        return jsonify({
            "status": "error",
            "message": "'symptoms' must be a JSON array of symptom identifier strings."
        }), 400

    include_possible = bool(data.get("include_possible", False))

    start_time = time.time()
    graded_results = predict_diseases(symptoms, include_possible=include_possible)
    diagnosed_results = [item["threat"] for item in graded_results]
    grade_map = {item["threat"]: item for item in graded_results}
    elapsed_time = round(time.time() - start_time, 3)

    explanations = explain_diagnoses(symptoms, graded_results)
    derivation_trace = get_derivation_trace(symptoms, graded_results)

    enriched_diagnoses = []
    for diag_name in diagnosed_results:
        threat_info = THREAT_MAP.get(diag_name)
        if not threat_info:
            for t in THREAT_CATALOG:
                if t.get("key") == diag_name or diag_name in t.get("nama", ""):
                    threat_info = t
                    break

        item_grade = grade_map.get(diag_name, {})
        expl = explanations.get(diag_name, {})
        proof_tree = derivation_trace["proof_trees"].get(diag_name, expl.get("proof_tree", {}))
        candidate_rules = derivation_trace["candidate_rules_by_threat"].get(diag_name, [])

        item = {
            "key": diag_name,
            "name": threat_info.get("nama", diag_name.replace("_", " ")) if threat_info else diag_name,
            "scientific_name": threat_info.get("nama_latin", "Scientific ID confirmed via SWRL") if threat_info else "",
            "category": threat_info.get("kategori", "Biotic Threat") if threat_info else "Biotic Threat",
            "grade": item_grade.get("grade", "confirmed"),
            "confidence": item_grade.get("confidence", 1.0),
            "fired_rules": item_grade.get("fired_rules", []),
            "target_organ": threat_info.get("organ_target", "Rice Plant") if threat_info else "Rice Plant",
            "description": threat_info.get("deskripsi", "") if threat_info else "",
            "ipm_prescriptions": threat_info.get("pengendalian_ipm", []) if threat_info else [],
            "derivation_trace": {
                "rule_level": expl.get("rule_level", "Tier 1 (Canonical)"),
                "active_rule": expl.get("rule_id", ""),
                "formula": expl.get("formula", ""),
                "rationale": expl.get("rationale", ""),
                "antecedents_status": expl.get("antecedents_status", []),
                "candidate_rules": candidate_rules,
                "proof_tree": proof_tree
            }
        }
        enriched_diagnoses.append(item)

    return jsonify({
        "status": "success",
        "api_version": "v2",
        "query": {
            "symptoms_count": len(symptoms),
            "symptoms": symptoms,
            "include_possible": include_possible
        },
        "inference": {
            "reasoner": "Pellet DL (Tableau Forward-Chaining)",
            "execution_time_seconds": elapsed_time,
            "diagnoses_count": len(diagnosed_results)
        },
        "diagnoses": enriched_diagnoses,
        "derivation_summary": derivation_trace["summary"],
        "proof_trees": derivation_trace["proof_trees"],
        "fired_rules": derivation_trace["fired_rules"],
        "all_candidate_rules": derivation_trace["evaluated_rules_trace"]
    }), 200


@app.route("/api/v1/threats", methods=["GET"])
def api_threats():
    """Returns all 10 formalized rice biotic threats and metadata."""
    return jsonify({
        "status": "success",
        "total_threats": len(THREAT_CATALOG),
        "threats": THREAT_CATALOG
    }), 200


@app.route("/api/v1/symptoms", methods=["GET"])
def api_symptoms():
    """Returns the phenotypic symptoms grouped by anatomical organ."""
    return jsonify({
        "status": "success",
        "total_symptoms": sum(len(c["symptoms"]) for c in SYMPTOM_CATEGORIES),
        "categories": SYMPTOM_CATEGORIES
    }), 200


@app.route("/api/v1/scenarios", methods=["GET"])
def api_scenarios():
    """Returns preset benchmark field scenarios."""
    return jsonify({
        "status": "success",
        "scenarios": BENCHMARK_SCENARIOS
    }), 200


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")

