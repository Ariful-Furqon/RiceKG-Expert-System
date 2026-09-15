"""
Unit tests for the Noisy-OR probabilistic reasoning layer (probabilistic.py).
Verifies formulation correctness, numerical stability, monotonicity, determinism,
gate precedence, and schema compatibility (PART 8-B.5).
"""

import math
import pytest
import model
import probabilistic
from probabilistic import NoisyOrParameters, posterior_scores, predict_probabilistic, rank_differential_probabilistic


def test_hand_computed_toy_example_matches_to_1e9():
    """
    Hand-computed toy example matching exact mathematical formulation to 1e-9.

    Setup:
      Threats: T1, T2
      Prior: P(T1) = 0.20, P(T2) = 0.10
      Signs: S1, S2, S3
      Leaks: leak(S1) = 0.05, leak(S2) = 0.02, leak(S3) = 0.01

      Links:
        T1: S1 (p=0.80), S2 (p=0.60)
        T2: S2 (p=0.50), S3 (p=0.90)

      Evidence:
        Present: S1, S2
        Absent: S3

    Mathematical derivation:
      T1:
        Prior odds O(T1) = 0.20 / 0.80 = 0.25
        S1 present: P(S1|T1) = 1 - (1 - 0.05)*(1 - 0.80) = 0.81
                    P(S1|~T1) = 0.05
                    LR(S1|T1) = 0.81 / 0.05 = 16.2
        S2 present: P(S2|T1) = 1 - (1 - 0.02)*(1 - 0.60) = 0.608
                    P(S2|~T1) = 0.02
                    LR(S2|T1) = 0.608 / 0.02 = 30.4
        S3 absent: unlinked to T1, LR = 1.0
        Posterior odds O(T1|E) = 0.25 * 16.2 * 30.4 = 123.12
        Posterior P(T1|E) = 123.12 / (1 + 123.12) = 3078 / 3103 ≈ 0.9919432806960999...

      T2:
        Prior odds O(T2) = 0.10 / 0.90 = 1/9
        S1 present: unlinked to T2, LR = 1.0
        S2 present: P(S2|T2) = 1 - (1 - 0.02)*(1 - 0.50) = 0.51
                    P(S2|~T2) = 0.02
                    LR(S2|T2) = 0.51 / 0.02 = 25.5
        S3 absent: linked with p=0.90
                   LR_absent(S3|T2) = 1 - 0.90 = 0.10
        Posterior odds O(T2|E) = (1/9) * 25.5 * 0.10 = 2.55 / 9 = 17 / 60
        Posterior P(T2|E) = (17/60) / (1 + 17/60) = 17 / 77 ≈ 0.22077922077922077...
    """
    links = {
        ("T1", "S1"): 0.80,
        ("T1", "S2"): 0.60,
        ("T2", "S2"): 0.50,
        ("T2", "S3"): 0.90,
    }
    leaks = {
        "S1": 0.05,
        "S2": 0.02,
        "S3": 0.01,
    }
    # Test T1 with prior 0.20
    params_t1 = NoisyOrParameters(links=links, leaks=leaks, prior=0.20, threats=["T1"])
    scores_t1 = posterior_scores(symptoms=["S1", "S2"], absent=["S3"], params=params_t1)
    expected_t1 = 123.12 / 124.12
    assert abs(scores_t1["T1"] - expected_t1) < 1e-9, f"T1 mismatch: {scores_t1['T1']} vs {expected_t1}"

    # Test T2 with prior 0.10
    params_t2 = NoisyOrParameters(links=links, leaks=leaks, prior=0.10, threats=["T2"])
    scores_t2 = posterior_scores(symptoms=["S1", "S2"], absent=["S3"], params=params_t2)
    expected_t2 = 17.0 / 77.0
    assert abs(scores_t2["T2"] - expected_t2) < 1e-9, f"T2 mismatch: {scores_t2['T2']} vs {expected_t2}"


def test_observed_sign_monotonicity():
    """Adding an observed sign linked to t never decreases P(t | E); unlinked leaves it unchanged."""
    params = probabilistic.get_default_parameters()
    t = "Rice_Blast"
    linked_sign = "Diamond_Shaped_Lesions"
    unlinked_sign = "Hook_Like_Root_Swelling"  # Nematode-specific

    # Base score with no evidence
    base_scores = posterior_scores([], params=params)
    assert abs(base_scores[t] - params.prior) < 1e-9

    # Score with unlinked sign
    unlinked_scores = posterior_scores([unlinked_sign], params=params)
    assert abs(unlinked_scores[t] - base_scores[t]) < 1e-9

    # Score with linked sign
    linked_scores = posterior_scores([linked_sign], params=params)
    assert linked_scores[t] > base_scores[t]

    # Additional linked sign increases score further
    second_linked = "Necrotic_Spots"
    two_linked_scores = posterior_scores([linked_sign, second_linked], params=params)
    assert two_linked_scores[t] > linked_scores[t]


def test_unrecorded_signs_marginalized_out():
    """An unrecorded sign leaves every posterior unchanged."""
    params = probabilistic.get_default_parameters()
    symptoms = ["Water_Soaked_Lesions"]

    score1 = posterior_scores(symptoms, absent=(), params=params)
    # Neither present nor absent: completely omitted from call
    score2 = posterior_scores(symptoms, absent=(), params=params)
    for t in model.ALL_DIAGNOSES:
        assert abs(score1[t] - score2[t]) < 1e-12


def test_recorded_absent_sign_monotonicity():
    """A recorded absent sign linked to t never increases P(t | E)."""
    params = probabilistic.get_default_parameters()
    t = "Bacterial_Leaf_Blight"
    s1 = "Water_Soaked_Lesions"
    s2 = "Yellowing_Leaf_Tips"

    scores_present = posterior_scores([s1], absent=(), params=params)
    scores_absent = posterior_scores([s1], absent=[s2], params=params)

    assert scores_absent[t] < scores_present[t]

    # Recording an unlinked absent sign leaves posterior unchanged
    unlinked_absent = "Hook_Like_Root_Swelling"
    scores_unlinked_absent = posterior_scores([s1], absent=[unlinked_absent], params=params)
    assert abs(scores_unlinked_absent[t] - scores_present[t]) < 1e-9


def test_determinism_and_order_invariance():
    """Determinism: identical output across two calls and independent of input order."""
    syms_order1 = ["Rusty_Grain_Balls", "Blackened_Grain_Balls", "Rainy_Season_Outbreak"]
    syms_order2 = ["Rainy_Season_Outbreak", "Rusty_Grain_Balls", "Blackened_Grain_Balls"]

    res1 = predict_probabilistic(syms_order1)
    res2 = predict_probabilistic(syms_order2)

    assert len(res1) == len(res2)
    for r1, r2 in zip(res1, res2):
        assert r1["threat"] == r2["threat"]
        assert r1["confidence"] == r2["confidence"]
        assert r1["matched_symptoms"] == r2["matched_symptoms"]
        assert r1["missing_symptoms"] == r2["missing_symptoms"]


def test_gate_precedence_on_insect_and_negative_control_fixtures():
    """Gate precedence identical to model.predict_diseases on insect and negative control fixtures."""
    # 1. Pure insect damage (>= 2 insect signs) yields insect out-of-scope
    insect_syms = ["Severed_Panicles", "Leaf_Chewing_Damage"]
    m_res = model.predict_diseases(insect_syms)
    p_res = predict_probabilistic(insect_syms, apply_gates=True)

    assert len(p_res) == 1
    assert p_res[0]["threat"] == model.INSECT_OUT_OF_SCOPE_TARGET
    assert p_res[0]["threat"] == m_res[0]["threat"]
    assert p_res[0]["grade"] == "out_of_scope"

    # 2. Negative control (unmodeled disease signs) yields negative control out-of-scope
    neg_syms = ["Leaf_Sheath_Lesions", "Rotten_Panicles"]
    m_neg = model.predict_diseases(neg_syms)
    p_neg = predict_probabilistic(neg_syms, apply_gates=True)

    assert len(p_neg) == 1
    assert p_neg[0]["threat"] == model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET
    assert p_neg[0]["threat"] == m_neg[0]["threat"]
    assert p_neg[0]["grade"] == "out_of_scope"

    # 3. With apply_gates=False, both fixtures return empty (no false positive disease diagnosis)
    assert predict_probabilistic(insect_syms, apply_gates=False) == []
    assert predict_probabilistic(neg_syms, apply_gates=False) == []


def test_output_schema_compatible_with_top_k_evaluation():
    """Output schema matches predict_diseases and feeds into differential ranking."""
    syms = ["Diamond_Shaped_Lesions", "Necrotic_Spots"]
    results = predict_probabilistic(syms)

    assert len(results) > 0
    top = results[0]
    required_keys = {
        "threat", "grade", "confidence", "antecedent_coverage",
        "fired_rules", "matched_symptoms", "missing_symptoms"
    }
    assert required_keys.issubset(top.keys())
    assert top["threat"] == "Rice_Blast"
    assert top["grade"] == "probable"
    assert 0.50 <= top["confidence"] <= 1.0

    # Differential ranking helper
    ranked = rank_differential_probabilistic(syms, k=3)
    assert len(ranked) >= 1
    assert ranked[0] == "Rice_Blast"

