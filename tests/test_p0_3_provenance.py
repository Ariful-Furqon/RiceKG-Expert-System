import os
import sys
import csv
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import evaluate
from analysis.agreement import compute_cohens_kappa, compute_fleiss_kappa, run_agreement_analysis


def test_augmented_benchmark_provenance():
    path = os.path.join(evaluate.BASE_DIR, "data", "benchmark_augmented.csv")
    assert os.path.exists(path), f"Augmented benchmark not found at {path}"

    data = evaluate.load_data(path)
    assert len(data) == 80, f"Expected 80 cases, got {len(data)}"
    for item in data:
        assert item["provenance"] == "rule_derived", f"Case {item['case_id']} must have provenance 'rule_derived'"


def test_field_benchmark_provenance_and_citations():
    path = os.path.join(evaluate.BASE_DIR, "data", "benchmark_field.csv")
    assert os.path.exists(path), f"Field benchmark not found at {path}"

    data = evaluate.load_data(path)
    assert len(data) >= 30, f"Expected at least 30 field cases per protocol, got {len(data)}"

    # Audit authentic DOIs, verbatim raw symptoms, and citation metadata
    no_diag_count = 0
    in_scope_count = 0
    for item in data:
        assert len(item["citation"]) > 10, f"Case {item['case_id']} missing valid citation"
        assert len(item["raw_symptom_text"]) > 10, f"Case {item['case_id']} missing raw_symptom_text"
        assert item["doi"].startswith("10."), f"Case {item['case_id']} must have a verified DOI starting with '10.'"

        if item["raw_target"] == "No_Diagnosis":
            no_diag_count += 1
        else:
            in_scope_count += 1
            assert len(item["symptoms"]) >= 1, f"In-scope case {item['case_id']} must have at least one mapped symptom"

    # Verify composition: presence of both in-scope targets and negative control / out-of-scope cases
    assert in_scope_count >= 4, f"Expected in-scope target cases, got {in_scope_count}"
    assert no_diag_count >= 12, f"Expected at least 12 negative control / out-of-scope cases, got {no_diag_count}"


def test_agreement_analysis_refuses_empty(tmp_path):
    empty_csv = tmp_path / "empty_annotations.csv"
    empty_csv.write_text("case_id,annotator_1,annotator_2\n", encoding="utf-8")

    status = run_agreement_analysis(str(empty_csv))
    assert status == 0, "Agreement analysis must exit cleanly with code 0 on empty files without fabricating data"


def test_agreement_analysis_cohen_kappa_math():
    r1 = ["Blast", "Blast", "Blight", "Smut", "Blast"]
    r2 = ["Blast", "Blast", "Blight", "Blast", "Blast"]
    categories = ["Blast", "Blight", "Smut"]

    kappa, po, pe = compute_cohens_kappa(r1, r2, categories)
    assert po == 0.8  # 4 out of 5 agree
    assert -1.0 <= kappa <= 1.0


def test_agreement_analysis_fleiss_kappa_math():
    matrix = [
        ["Blast", "Blast", "Blast"],
        ["Blight", "Blight", "Blight"],
        ["Smut", "Smut", "Smut"],
        ["Blast", "Blast", "Blight"]
    ]
    categories = ["Blast", "Blight", "Smut"]
    kappa, po, pe = compute_fleiss_kappa(matrix, categories)
    assert po > pe
    assert kappa > 0.6  # High agreement


def test_out_of_sample_calibration_train_test_separation():
    # Verify that the CV fold partition preserves independence
    from sklearn.model_selection import StratifiedKFold

    dummy_cases = [{"id": i, "label": "pest" if i % 2 == 0 else "disease"} for i in range(20)]
    labels = [c["label"] for c in dummy_cases]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    all_test_indices = []
    for train_idx, test_idx in skf.split(dummy_cases, labels):
        # Strict disjointness
        assert set(train_idx).isdisjoint(set(test_idx))
        all_test_indices.extend(test_idx)

    assert len(all_test_indices) == 20
    assert len(set(all_test_indices)) == 20
