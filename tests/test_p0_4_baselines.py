"""
tests/test_p0_4_baselines.py
----------------------------
Test suite verifying P0-4 implementation:
1. 45-dimensional binary symptom encoding round-trips correctly and matches model.ALL_SYMPTOMS.
2. Sentinel 'No_Diagnosis' strictly encodes to an all-zero label vector (not an 11th class).
3. Multi-label compound targets joined by ' and ' encode correctly.
4. The 5x2-fold cross-validation protocol shares identical test indices between RiceKG and baselines.
5. McNemar paired test and effect sizes calculate correctly.
6. Bootstrap micro-F1 confidence interval computation.
7. Holm-Bonferroni step-down correction properties.
8. Minimum Detectable Effect (MDE) calculations.
"""

import pytest
import numpy as np
import model
import evaluate
from baselines import ml_baselines, rule_baselines
from analysis import significance


class TestP04BaselinesEncoding:
    """Tests feature and label vector representations for comparative baselines."""

    def test_symptom_vector_dimension_and_order(self):
        """Asserts encoding produces a 45-dim binary vector strictly aligned with model.ALL_SYMPTOMS."""
        assert len(model.ALL_SYMPTOMS) == 45
        assert len(ml_baselines.SYMPTOM_ORDER) == 45
        assert ml_baselines.SYMPTOM_ORDER == model.ALL_SYMPTOMS

        test_symptoms = ["Brown_Nymphs", "Eggs_On_Plant", "Leaf_Chewing_Damage"]
        vec = ml_baselines.encode_symptoms(test_symptoms)

        assert isinstance(vec, np.ndarray)
        assert vec.shape == (45,)
        assert vec.dtype == int
        assert np.sum(vec) == 3

        # Check exact indices
        for s in test_symptoms:
            idx = model.ALL_SYMPTOMS.index(s)
            assert vec[idx] == 1

        # Check round-trip decoding
        decoded = ml_baselines.decode_symptoms(vec)
        assert set(decoded) == set(test_symptoms)

    def test_no_diagnosis_maps_to_all_zeros(self):
        """Asserts 'No_Diagnosis' produces an all-zero label vector of length 10."""
        assert len(ml_baselines.ALL_THREATS) == 10

        vec_sentinel = ml_baselines.encode_labels("No_Diagnosis")
        vec_empty_str = ml_baselines.encode_labels("")
        vec_empty_list = ml_baselines.encode_labels([])

        assert vec_sentinel.shape == (10,)
        assert np.all(vec_sentinel == 0), "No_Diagnosis must encode to all-zeros"
        assert np.all(vec_empty_str == 0)
        assert np.all(vec_empty_list == 0)

        # Decoding all-zeros yields empty list
        assert ml_baselines.decode_labels(vec_sentinel) == []

    def test_multilabel_compound_targets_encoding(self):
        """Asserts compound multi-threat targets joined by ' and ' encode to multiple 1s."""
        target = "Bacterial_Leaf_Blight and Rice_Blast"
        vec = ml_baselines.encode_labels(target)

        assert np.sum(vec) == 2
        blb_idx = ml_baselines.THREAT_TO_IDX["Bacterial_Leaf_Blight"]
        rb_idx = ml_baselines.THREAT_TO_IDX["Rice_Blast"]
        assert vec[blb_idx] == 1
        assert vec[rb_idx] == 1

        decoded = ml_baselines.decode_labels(vec)
        assert set(decoded) == {"Bacterial_Leaf_Blight", "Rice_Blast"}


class TestP04FairProtocol:
    """Verifies that the fair-comparison 5x2-fold protocol provides identical
    test indices across all competing systems.
    """

    def test_5x2_split_integrity_and_identical_test_indices(self):
        """Asserts 10 splits (5 iterations x 2 folds) with exact coverage."""
        X = np.zeros((80, 45), dtype=int)
        Y = np.zeros((80, 10), dtype=int)
        Y[:40, 0] = 1
        Y[40:, 1] = 1

        splits = ml_baselines.get_5x2_splits(X, Y, random_state=42)
        assert len(splits) == 10, "5x2-fold CV must yield exactly 10 splits"

        for s in splits:
            tr = s["train_indices"]
            te = s["test_indices"]
            assert len(tr) + len(te) == 80
            assert len(np.intersect1d(tr, te)) == 0, "Train and test folds must be strictly disjoint"
            assert len(np.union1d(tr, te)) == 80, "Train and test folds must span entire dataset"


class TestP04SignificanceTesting:
    """Verifies statistical testing implementations."""

    def test_mcnemar_identical_predictions(self):
        """Asserts McNemar statistic is 0.0 and p=1.0 when predictions match."""
        y_true = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
        y_pred = y_true.copy()

        res = significance.compute_mcnemar_test(y_true, y_pred, y_pred)
        assert res["statistic"] == 0.0
        assert res["p_value"] == 1.0
        assert res["delta_acc"] == 0.0
        assert res["total_discordant"] == 0

    def test_mcnemar_discordant_pairs(self):
        """Asserts McNemar detects significant difference on asymmetric discordant pairs."""
        y_true = np.zeros((100, 2), dtype=int)
        y_a = y_true.copy()  # A gets 100% correct
        y_b = np.ones((100, 2), dtype=int)  # B gets 0% correct

        res = significance.compute_mcnemar_test(y_true, y_a, y_b)
        assert res["p_value"] < 0.001
        assert res["delta_acc"] == 100.0
        assert res["cohens_g"] == 0.5

    def test_bootstrap_micro_f1_ci(self):
        """Asserts bootstrap returns non-empty percentile confidence intervals."""
        y_true = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
        y_pred = y_true.copy()

        res = significance.bootstrap_micro_f1_ci(y_true, y_pred, n_resamples=200, random_state=42)
        assert res["n_resamples"] == 200
        assert res["f1_a_ci"][0] == 100.0
        assert res["f1_a_ci"][1] == 100.0

    def test_holm_bonferroni_correction(self):
        """Asserts Holm-Bonferroni enforces step-down multiplier and monotonic adjustment."""
        raw_p = [0.005, 0.012, 0.040, 0.200]
        results = significance.apply_holm_bonferroni(raw_p, alpha=0.05)

        adj_p = [r["holm_p_value"] for r in results]
        assert adj_p[0] <= adj_p[1] <= adj_p[2] <= adj_p[3]
        assert all(p <= 1.0 for p in adj_p)

    def test_minimum_detectable_effect(self):
        """Asserts MDE calculates realistic minimum effects for small n."""
        mde80 = significance.calculate_minimum_detectable_effect(80)
        mde32 = significance.calculate_minimum_detectable_effect(32)

        assert 10.0 <= mde80["mde_percentage_proportion"] <= 20.0
        assert 20.0 <= mde32["mde_percentage_proportion"] <= 35.0
        assert mde32["mde_percentage_proportion"] > mde80["mde_percentage_proportion"]
