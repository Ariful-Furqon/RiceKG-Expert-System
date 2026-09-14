import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model
import app as flask_app
from studies.explainability.analyse import analyze_explainability_study, compute_cronbach_alpha, paired_t_test
import numpy as np


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


class TestP16DerivationTrace:
    def test_derivation_trace_structure_on_canonical_blast(self):
        r08 = next(r for r in model.RULE_REGISTRY if r["id"] == "SWRL-R08")
        symptoms = r08["antecedents"]
        trace = model.get_derivation_trace(symptoms)

        assert "summary" in trace
        assert "fired_rules" in trace
        assert "proof_trees" in trace
        assert "candidate_rules_by_threat" in trace
        assert "evaluated_rules_trace" in trace

        assert trace["summary"]["total_rules_evaluated"] == 20
        assert trace["summary"]["fired_rules_count"] >= 1
        assert "Rice_Blast" in trace["proof_trees"]

        tree = trace["proof_trees"]["Rice_Blast"]
        assert tree["threat"] == "Rice_Blast"
        assert tree["grade"] == "confirmed"
        assert tree["inference_step"]["inference_rule"] == "Modus Ponens"
        assert len(tree["inference_step"]["premises"]) >= 4

        # Every premise in Tier 1 should be satisfied
        for premise in tree["inference_step"]["premises"]:
            assert premise["observed"] is True
            assert premise["status"] == "SATISFIED"

    def test_derivation_trace_records_unmet_antecedents(self):
        # Only 1 symptom for Rice Blast (insufficient to fire)
        symptoms = ["Diamond_Shaped_Lesions"]
        trace = model.get_derivation_trace(symptoms)

        blast_rules = trace["candidate_rules_by_threat"]["Rice_Blast"]
        t1_rule = next(r for r in blast_rules if r["tier"] == "tier1")
        t2_rule = next(r for r in blast_rules if r["tier"] == "tier2")

        assert t1_rule["status"] == "UNSATISFIED"
        assert len(t1_rule["satisfied_antecedents"]) == 1
        assert len(t1_rule["unmet_antecedents"]) >= 3
        assert "Diamond_Shaped_Lesions" in t1_rule["satisfied_antecedents"]

        # Proof tree for unconfirmed case records unmet premises
        tree = trace["proof_trees"].get("Rice_Blast")
        assert tree is not None
        unmet_premises = [p for p in tree["inference_step"]["premises"] if not p["observed"]]
        assert len(unmet_premises) >= 1
        for p in unmet_premises:
            assert p["status"] == "UNMET"


class TestP16ApiV2Endpoints:
    def test_api_v1_backward_compatibility(self, client):
        payload = {"symptoms": ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips"]}
        res = client.post("/api/v1/diagnose", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "diagnoses" in data
        assert "explanations" in data

    def test_api_v2_diagnose_structure(self, client):
        payload = {
            "symptoms": [
                "Water_Soaked_Lesions",
                "Yellowing_Leaf_Tips",
                "Leaf_Discoloration_Yellow"
            ],
            "include_possible": True
        }
        res = client.post("/api/v2/diagnose", json=payload)
        assert res.status_code == 200
        data = res.get_json()

        assert data["status"] == "success"
        assert data["api_version"] == "v2"
        assert "derivation_summary" in data
        assert "proof_trees" in data
        assert "fired_rules" in data
        assert "all_candidate_rules" in data
        assert len(data["all_candidate_rules"]) == 20

        # Verify enriched diagnoses contain complete derivation trace
        blb_diag = next((d for d in data["diagnoses"] if d["key"] == "Bacterial_Leaf_Blight"), None)
        assert blb_diag is not None
        assert "derivation_trace" in blb_diag
        trace = blb_diag["derivation_trace"]
        assert "active_rule" in trace
        assert "proof_tree" in trace
        assert "candidate_rules" in trace
        assert len(trace["candidate_rules"]) == 2

    def test_api_v2_empty_or_invalid_payload(self, client):
        res = client.post("/api/v2/diagnose", json={})
        assert res.status_code == 400
        assert "Missing 'symptoms'" in res.get_json()["message"]

        res2 = client.post("/api/v2/diagnose", json={"symptoms": "not-a-list"})
        assert res2.status_code == 400


class TestP16StudyArtifactsAndAnalysis:
    def test_protocol_and_instrument_exist(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        proto_path = os.path.join(base, "studies", "explainability", "protocol.md")
        inst_path = os.path.join(base, "studies", "explainability", "instrument_explanation_satisfaction.md")
        ethics_path = os.path.join(base, "docs", "ETHICS.md")

        assert os.path.exists(proto_path), "studies/explainability/protocol.md missing"
        assert os.path.exists(inst_path), "instrument_explanation_satisfaction.md missing"
        assert os.path.exists(ethics_path), "docs/ETHICS.md missing"

        with open(inst_path, encoding="utf-8") as f:
            inst_text = f.read()
            assert "Hoffman et al." in inst_text
            assert "ESS_01" in inst_text
            assert "ESS_08" in inst_text
            assert "Trust in Automation" in inst_text

    def test_responses_csv_zero_rows(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resp_path = os.path.join(base, "studies", "explainability", "responses.csv")
        assert os.path.exists(resp_path)

        with open(resp_path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            assert len(lines) == 1, "responses.csv must contain exactly one header line and zero data rows"
            assert "participant_id" in lines[0]
            assert "ess_composite" in lines[0]

    def test_analyse_py_exits_cleanly_on_empty(self):
        status = analyze_explainability_study()
        assert status == 0, "analyse.py must exit cleanly with code 0 on empty responses.csv"

    def test_cronbach_alpha_math(self):
        # Test scale reliability math on synthetic matrix
        items = np.array([
            [5, 4, 5, 4, 5],
            [4, 4, 4, 3, 4],
            [5, 5, 5, 5, 5],
            [2, 3, 2, 2, 3],
            [1, 2, 1, 1, 2]
        ])
        alpha = compute_cronbach_alpha(items)
        assert alpha > 0.80, f"Expected high alpha for concordant items, got {alpha}"

    def test_paired_t_test_math(self):
        x = np.array([10.0, 12.0, 14.0, 16.0, 18.0])
        y = np.array([8.0, 9.0, 11.0, 12.0, 13.0])
        t, p, d = paired_t_test(x, y)
        assert t > 0
        assert p < 0.05
        assert d > 0.80
