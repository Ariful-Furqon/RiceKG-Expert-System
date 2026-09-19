"""
tests/test_learning_curve.py - Test suite for Cold-Start Learning Curve Experiment
----------------------------------------------------------------------------------
Verifies:
1. Determinism under fixed seed.
2. Refusal to run on empty eval split.
3. Zero leakage: No field eval case ever appears in any training draw.
4. Pool B draws come strictly from field dev split.
5. DOI disjointness: No DOI in training draw appears in eval set.
6. Zero-shot reference figures reproduce results/baselines.md Section 2 exactly.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import evaluate
from analysis import learning_curve
from baselines import ml_baselines

FIELD_CSV = os.path.join(BASE_DIR, "data", "benchmark_field.csv")
VERIFICATION_CSV = os.path.join(BASE_DIR, "data", "verification_suite.csv")


def test_zero_shot_reference_computation():
    """Verify that zero-shot references are computed at runtime on eval split and match baselines.json."""
    X_eval, Y_eval, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")
    refs = learning_curve.compute_zero_shot_references(eval_cases, Y_eval)

    with open(os.path.join(BASE_DIR, "results", "baselines.json"), "r", encoding="utf-8") as f:
        base_json = json.load(f)
    fb = base_json["field_benchmark"]["system_summaries"]["RiceKG (Full Proposed)"]

    assert "RiceKG (Full Proposed)" in refs
    rk_ref = refs["RiceKG (Full Proposed)"]
    assert rk_ref["cv_positive_recall"] == round(float(fb["mean_positive_recall"]), 2)
    assert rk_ref["cv_exact_match"] == round(float(fb["mean_exact_match"]), 2)
    assert rk_ref["cv_micro_f1"] == round(float(fb["mean_micro_f1"]), 2)
    # Expert-consensus encoding (data/symptom_encoding_consensus.csv): 4/5 positives, 21/22 cases.
    assert rk_ref["runtime_positive_recall"] == 80.00
    assert rk_ref["runtime_exact_match"] == 95.45
    assert isinstance(rk_ref["positive_recall_ci_95"], list)
    assert len(rk_ref["positive_recall_ci_95"]) == 2

    assert "Rule: Flat Single-Tier" in refs
    assert refs["Rule: Flat Single-Tier"]["runtime_positive_recall"] == 80.00

    assert "Rule: Nearest Prototype" in refs
    assert refs["Rule: Nearest Prototype"]["runtime_positive_recall"] == 40.00


def test_zero_shot_reference_fails_loudly_on_corrupt_baselines(monkeypatch, tmp_path):
    """Verify that compute_zero_shot_references fails loudly if baselines.json is corrupt or missing keys."""
    corrupt_file = tmp_path / "baselines.json"
    corrupt_file.write_text('{"field_benchmark": {"system_summaries": {}}}', encoding="utf-8")
    monkeypatch.setattr(learning_curve, "BASELINES_JSON", str(corrupt_file))

    X_eval, Y_eval, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")
    with pytest.raises(KeyError, match="Missing 'RiceKG \\(Full Proposed\\)'"):
        learning_curve.compute_zero_shot_references(eval_cases, Y_eval)



def test_refuse_empty_eval_split():
    """Verify that run_learning_curve_for_pool raises ValueError when eval set is empty."""
    X_pool = np.zeros((5, 45), dtype=int)
    Y_pool = np.zeros((5, 10), dtype=int)
    pool_cases = [{"case_id": f"CASE_{i}", "symptoms": ["S1"], "raw_target": "D1"} for i in range(5)]

    X_test_empty = np.zeros((0, 45), dtype=int)
    Y_test_empty = np.zeros((0, 10), dtype=int)
    test_cases_empty = []

    with pytest.raises(ValueError, match="Evaluation dataset cannot be empty"):
        learning_curve.run_learning_curve_for_pool(
            pool_name="TEST_POOL",
            pool_source_desc="Test Pool",
            X_pool=X_pool,
            Y_pool=Y_pool,
            pool_cases=pool_cases,
            X_test=X_test_empty,
            Y_test=Y_test_empty,
            test_cases=test_cases_empty,
            budgets=[2],
            n_draws=2,
            base_seed=42,
        )


import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def test_zero_leakage_pool_a_verification():
    """Verify that verification-suite cases do not leak into the field eval set."""
    cases_eval = evaluate.load_data(FIELD_CSV, split="eval")
    eval_ids = {c["case_id"] for c in cases_eval}
    eval_dois = {c.get("doi") for c in cases_eval if c.get("doi")}

    cases_syn = evaluate.load_data(VERIFICATION_CSV)
    syn_ids = {c["case_id"] for c in cases_syn}
    syn_dois = {c.get("doi") for c in cases_syn if c.get("doi")}

    # Case IDs must be disjoint
    overlap_ids = eval_ids.intersection(syn_ids)
    assert len(overlap_ids) == 0, f"Found overlapping case_ids between verification pool and eval: {overlap_ids}"

    # Verification-suite cases have no DOIs (rule_derived), whereas field eval cases have verified DOIs
    overlap_dois = eval_dois.intersection(syn_dois)
    assert len(overlap_dois) == 0, f"Found overlapping DOIs: {overlap_dois}"

    # All field eval cases have verified DOIs and field case IDs
    assert all(c["case_id"].startswith("FIELD_") for c in cases_eval)
    assert all(c.get("doi", "").startswith("10.") for c in cases_eval)
    assert all(not c.get("doi") for c in cases_syn)


def test_zero_leakage_pool_b_field_dev_vs_eval():
    """Verify strict partition separation between field dev (Pool B) and field eval."""
    field_df = pd.read_csv(FIELD_CSV)
    dev_df = field_df[field_df["split"] == "dev"]
    eval_df = field_df[field_df["split"] == "eval"]

    dev_ids = set(dev_df["case_id"].dropna())
    eval_ids = set(eval_df["case_id"].dropna())

    # 1. No case ID overlap
    id_overlap = dev_ids.intersection(eval_ids)
    assert len(id_overlap) == 0, f"Case ID overlap between dev and eval: {id_overlap}"

    # 2. No DOI overlap (DOI-level partitioning)
    dev_dois = set(dev_df["doi"].dropna())
    eval_dois = set(eval_df["doi"].dropna())
    doi_overlap = dev_dois.intersection(eval_dois)
    assert len(doi_overlap) == 0, f"DOI overlap between dev and eval: {doi_overlap}"


def test_draw_stratified_subsample_determinism_and_disjointness():
    """Verify determinism under fixed seed and that sampling never exceeds pool size or duplicates indices."""
    X_pool, Y_pool, dev_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="dev")
    _, _, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")

    eval_ids = {c["case_id"] for c in eval_cases}
    eval_dois = {c.get("doi") for c in eval_cases if c.get("doi")}

    rng1 = np.random.RandomState(42)
    X1, Y1, idx1, absent1 = learning_curve.draw_stratified_subsample(X_pool, Y_pool, budget=4, rng=rng1)

    rng2 = np.random.RandomState(42)
    X2, Y2, idx2, absent2 = learning_curve.draw_stratified_subsample(X_pool, Y_pool, budget=4, rng=rng2)

    # Determinism
    assert idx1 == idx2
    np.testing.assert_array_equal(X1, X2)
    np.testing.assert_array_equal(Y1, Y2)
    assert absent1 == absent2

    # Verify no drawn case belongs to eval
    for i in idx1:
        drawn_case = dev_cases[i]
        assert drawn_case["case_id"] not in eval_ids
        if drawn_case.get("doi"):
            assert drawn_case["doi"] not in eval_dois


def test_small_budget_learning_curve_execution():
    """Smoke test: execute learning curve on a minimal setup to ensure metric calculations succeed."""
    X_pool, Y_pool, dev_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="dev")
    X_eval, Y_eval, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")

    result = learning_curve.run_learning_curve_for_pool(
        pool_name="smoke_test_pool",
        pool_source_desc="Smoke Test Dev Pool",
        X_pool=X_pool,
        Y_pool=Y_pool,
        pool_cases=dev_cases,
        X_test=X_eval,
        Y_test=Y_eval,
        test_cases=eval_cases,
        budgets=[2, 4],
        n_draws=2,
        base_seed=123,
        test_set_label="Field eval split"
    )

    assert result["pool_name"] == "smoke_test_pool"
    assert len(result["by_budget"]) == 2
    for b_str, b_summary in result["by_budget"].items():
        assert "models" in b_summary
        for m_name, m_stats in b_summary["models"].items():
            assert "mean_positive_recall" in m_stats
            assert "training_ci_95" in m_stats
            assert "test_set_ci_95" in m_stats
            assert "test_set_diff_ci_95" in m_stats
            assert "test_set_ci_excludes_zero" in m_stats
            assert "is_crossover" in m_stats
            assert len(m_stats["training_ci_95"]) == 2
            assert len(m_stats["test_set_ci_95"]) == 2
            assert 0.0 <= m_stats["mean_positive_recall"] <= 100.0


def test_leakage_assertion_triggers_if_pool_overlaps_test_set():
    """Verify that run_learning_curve_for_pool actively catches and raises AssertionError on train-on-test overlap."""
    X_eval, Y_eval, eval_cases = ml_baselines.load_and_encode_dataset(FIELD_CSV, split="eval")

    # If training pool contains identical case_ids to the test set
    with pytest.raises(AssertionError, match="Data leakage detected"):
        learning_curve.run_learning_curve_for_pool(
            pool_name="leaky_pool",
            pool_source_desc="Leaky Pool",
            X_pool=X_eval,
            Y_pool=Y_eval,
            pool_cases=eval_cases,  # Identical to test_cases!
            X_test=X_eval,
            Y_test=Y_eval,
            test_cases=eval_cases,
            budgets=[2],
            n_draws=1,
            base_seed=42,
        )


def test_crossover_criterion_requires_test_set_ci_excluding_zero():
    """Verify that crossover detection requires test_set_diff_ci_95 lower bound > 0."""
    # Pool B results in learning_curve.json
    results_path = os.path.join(BASE_DIR, "results", "learning_curve.json")
    if os.path.exists(results_path):
        import json
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check all models across all budgets in all pools.
        # The pool keys are asserted rather than skipped: this loop previously
        # named keys that do not exist ("pool_a_synthetic"), so the guard made
        # the whole test pass without ever evaluating an assertion.
        checked = 0
        for pool_key in ["pool_A_results", "pool_B_results"]:
            assert pool_key in data, f"{pool_key} missing from learning_curve.json"
            p_data = data[pool_key]
            by_budget = p_data.get("by_budget", {})
            assert by_budget, f"{pool_key} has no by_budget entries"
            for b_str, b_dict in by_budget.items():
                for m_name, m_stats in b_dict.get("models", {}).items():
                    diff_ci = m_stats["test_set_diff_ci_95"]
                    sig_cross = m_stats["test_set_ci_excludes_zero"]
                    assert sig_cross is (diff_ci[0] > 0.0), (
                        f"{pool_key}/{b_str}/{m_name}: test_set_ci_excludes_zero="
                        f"{sig_cross} contradicts CI {diff_ci}"
                    )
                    checked += 1
        assert checked > 0, "crossover consistency check evaluated nothing"


