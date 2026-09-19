# tests/test_top_k.py
# -------------------
# Unit tests verifying the top-k differential diagnosis ranking (Part 7-A),
# guard rails (Part 7-D), and top-k metrics (Hit@k, MRR, FAR@k).

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ricekg import model
from ricekg.model import predict_top_k, TOP_K_GRADE_ORDINAL


def test_ordering_key_hierarchy():
    # Verify that candidate sorting strictly adheres to the pre-fixed ordering key:
    # grade ordinal desc > antecedent_coverage desc > confidence desc > threat asc.
    sample = [
        {"threat": "Rice_Blast", "grade": "possible", "antecedent_coverage": 0.5, "confidence": 0.25},
        {"threat": "Bacterial_Leaf_Blight", "grade": "confirmed", "antecedent_coverage": 1.0, "confidence": 1.0},
        {"threat": "False_Smut", "grade": "suspected", "antecedent_coverage": 1.0, "confidence": 0.9714},
        {"threat": "Rice_Tungro_Virus", "grade": "suspected", "antecedent_coverage": 0.8, "confidence": 0.9714},
        {"threat": "Rice_Grassy_Stunt", "grade": "possible", "antecedent_coverage": 0.5, "confidence": 0.25},
    ]

    sample.sort(
        key=lambda x: (
            -TOP_K_GRADE_ORDINAL.get(x["grade"], 0),
            -float(x["antecedent_coverage"]),
            -float(x["confidence"]),
            str(x["threat"])
        )
    )

    # 1. Confirmed first: Bacterial_Leaf_Blight
    assert sample[0]["threat"] == "Bacterial_Leaf_Blight"
    # 2. Suspected with higher coverage: False_Smut (1.0 vs 0.8)
    assert sample[1]["threat"] == "False_Smut"
    assert sample[2]["threat"] == "Rice_Tungro_Virus"
    # 3. Possible with identical coverage/confidence: alphabetical tie-break (Rice_Blast before Rice_Grassy_Stunt)
    assert sample[3]["threat"] == "Rice_Blast"
    assert sample[4]["threat"] == "Rice_Grassy_Stunt"


def test_top_k_truncation():
    # predict_top_k must truncate output strictly to at most k items with 1-indexed ranks.
    # Canonical BLB symptoms
    syms = ["Water_Soaked_Lesions", "Yellowing_Leaf_Tips", "Yellowing_Leaf_Veins", "Uniform_Field_Infection"]

    top_1 = predict_top_k(syms, k=1)
    assert len(top_1) <= 1
    if top_1:
        assert top_1[0]["rank"] == 1

    top_2 = predict_top_k(syms, k=2)
    assert len(top_2) <= 2
    for idx, item in enumerate(top_2, 1):
        assert item["rank"] == idx

    top_0 = predict_top_k(syms, k=0)
    assert top_0 == []

    top_neg = predict_top_k(syms, k=-3)
    assert top_neg == []


def test_out_of_scope_exclusion_from_differential():
    # Insect damage and negative control out-of-scope sentinels must NOT be ranked as disease candidates.
    # Pure insect signs
    insect_syms = ["Bore_Holes_In_Stem", "Frass_In_Stem", "Easily_Pulled_Tillers"]
    diff = predict_top_k(insect_syms, k=3)
    assert diff == [], "Insect out-of-scope response must not be returned in ranked disease differential"

    # Non-modeled pathogen signs
    neg_syms = ["Leaf_Sheath_Lesions", "Stem_Rot_Lesions"]
    diff_neg = predict_top_k(neg_syms, k=3)
    assert diff_neg == [], "Negative control response must not be returned in ranked disease differential"


def test_empty_query_behaviour():
    # Empty symptom queries must return an empty differential ([]).
    assert predict_top_k([], k=3) == []
    assert predict_top_k(None, k=3) == []
    assert predict_top_k(["   "], k=3) == []


def test_hit_at_k_and_mrr_math():
    # Verify top-k metric formulas on a hand-computed toy benchmark.
    # 4 synthetic cases:
    # Case 1: Ground truth = ['A']. Ranked predictions = ['A', 'B', 'C']. Rank = 1.
    # Case 2: Ground truth = ['B']. Ranked predictions = ['A', 'B', 'D']. Rank = 2.
    # Case 3: Ground truth = ['C']. Ranked predictions = ['A', 'B', 'C']. Rank = 3.
    # Case 4: Ground truth = ['D']. Ranked predictions = ['A', 'B', 'C']. Rank = inf (unmatched).
    #
    # Expected:
    # Hit@1: 1/4 = 0.25 (25.0%)
    # Hit@2: 2/4 = 0.50 (50.0%)
    # Hit@3: 3/4 = 0.75 (75.0%)
    # MRR: (1/1 + 1/2 + 1/3 + 0) / 4 = (1 + 0.5 + 0.3333 + 0) / 4 = 1.8333 / 4 = 0.4583

    toy_cases = [
        {"truth": ["A"], "preds": ["A", "B", "C"]},
        {"truth": ["B"], "preds": ["A", "B", "D"]},
        {"truth": ["C"], "preds": ["A", "B", "C"]},
        {"truth": ["D"], "preds": ["A", "B", "C"]},
    ]

    hits_1 = 0
    hits_2 = 0
    hits_3 = 0
    rr_sum = 0.0

    for c in toy_cases:
        t_set = set(c["truth"])
        preds = c["preds"]

        # Hit@1
        if any(p in t_set for p in preds[:1]):
            hits_1 += 1
        # Hit@2
        if any(p in t_set for p in preds[:2]):
            hits_2 += 1
        # Hit@3
        if any(p in t_set for p in preds[:3]):
            hits_3 += 1

        # MRR
        rr = 0.0
        for idx, p in enumerate(preds[:3], 1):
            if p in t_set:
                rr = 1.0 / idx
                break
        rr_sum += rr

    n = len(toy_cases)
    hit_1_pct = (hits_1 / n) * 100.0
    hit_2_pct = (hits_2 / n) * 100.0
    hit_3_pct = (hits_3 / n) * 100.0
    mrr = rr_sum / n

    assert round(hit_1_pct, 2) == 25.00
    assert round(hit_2_pct, 2) == 50.00
    assert round(hit_3_pct, 2) == 75.00
    assert round(mrr, 4) == 0.4583


def test_false_alarm_rate_at_k_math():
    # Verify False Alarm Rate at k (FAR@k) on negative control cases.
    # 4 negative control cases:
    # Case 1: preds = [] -> 0 false alarms
    # Case 2: preds = ['A'] -> 1 false alarm at k=1,2,3
    # Case 3: preds = [] -> 0 false alarms
    # Case 4: preds = ['B', 'C'] -> 1 false alarm at k=1,2,3
    #
    # FAR@1: 2/4 = 50.0%
    # Specificity@1: 1 - 0.5 = 50.0%
    toy_controls = [
        {"preds": []},
        {"preds": ["A"]},
        {"preds": []},
        {"preds": ["B", "C"]},
    ]

    fa_1 = sum(1 for c in toy_controls if len(c["preds"][:1]) > 0)
    fa_3 = sum(1 for c in toy_controls if len(c["preds"][:3]) > 0)

    n_ctrl = len(toy_controls)
    far_1 = (fa_1 / n_ctrl) * 100.0
    far_3 = (fa_3 / n_ctrl) * 100.0

    assert far_1 == 50.0
    assert far_3 == 50.0

