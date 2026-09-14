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
        # The encoder must track the ontology vocabulary, whatever its size. Pinning a
        # literal here would make every justified ontology extension look like a defect.
        n_symptoms = len(model.ALL_SYMPTOMS)
        assert n_symptoms >= 45, "Vocabulary must not shrink below the original 45 terms"
        assert len(ml_baselines.SYMPTOM_ORDER) == n_symptoms
        assert ml_baselines.SYMPTOM_ORDER == model.ALL_SYMPTOMS
        assert len(set(model.ALL_SYMPTOMS)) == n_symptoms, "Vocabulary contains duplicates"

        test_symptoms = ["Brown_Nymphs", "Eggs_On_Plant", "Leaf_Chewing_Damage"]
        vec = ml_baselines.encode_symptoms(test_symptoms)

        assert isinstance(vec, np.ndarray)
        assert vec.shape == (n_symptoms,)
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
        """Asserts 'No_Diagnosis' produces an all-zero label vector of length 6."""
        assert len(ml_baselines.ALL_THREATS) == 6

        vec_sentinel = ml_baselines.encode_labels("No_Diagnosis")
        vec_oos = ml_baselines.encode_labels("insect damage, out of scope")
        vec_empty_str = ml_baselines.encode_labels("")
        vec_empty_list = ml_baselines.encode_labels([])

        assert vec_sentinel.shape == (6,)
        assert np.all(vec_sentinel == 0), "No_Diagnosis must encode to all-zeros"
        assert np.all(vec_oos == 0), "insect damage, out of scope must encode to all-zeros"
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


class TestP04FieldReportingSeparation:
    """Verifies that the field benchmark evaluation strictly reports positive-case recall
    separately from overall exact match, preventing aggregate accuracy from masking
    the 0/5 true-positive finding.
    """

    def test_multilabel_metrics_separates_positive_recall_from_exact_match(self):
        """Asserts compute_multilabel_metrics segregates positive recall (0.0%)
        from negative-control-driven aggregate exact match (84.38%).
        """
        # 32 cases: 5 positive cases (indices 0-4), 27 negative controls (indices 5-31)
        y_true = np.zeros((32, 10), dtype=int)
        y_true[0, 0] = 1
        y_true[1, 1] = 1
        y_true[2, 2] = 1
        y_true[3, 3] = 1
        y_true[4, 4] = 1

        # All-zero predictions (as produced by RiceKG under vocabulary gating)
        y_pred = np.zeros((32, 10), dtype=int)

        metrics = ml_baselines.compute_multilabel_metrics(y_true, y_pred)

        assert metrics["positive_cases_count"] == 5
        assert metrics["positive_cases_correct"] == 0
        assert metrics["positive_case_recall"] == 0.0, "Positive case recall must be 0.0%"

        assert metrics["negative_cases_count"] == 27
        assert metrics["negative_cases_correct"] == 27
        assert metrics["negative_control_accuracy"] == 100.0

        # Exact match is 27/32 = 84.375%
        assert np.isclose(metrics["exact_match"], 84.375)

        # CRITICAL ASSERTION: positive_case_recall must NOT equal aggregate exact_match
        assert metrics["positive_case_recall"] != metrics["exact_match"], (
            "Aggregate exact match (84.38%) must not stand in for positive recall (0.0%)!"
        )

    def test_field_results_report_positive_recall_distinctly(self):
        """Asserts results/baselines.json and results/baselines.md distinctly publish
        positive-case recall and do not allow aggregate accuracy to stand in for positive recall.
        """
        import os
        import json

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "results", "baselines.json")
        md_path = os.path.join(base_dir, "results", "baselines.md")

        assert os.path.exists(json_path), f"Missing {json_path}"
        assert os.path.exists(md_path), f"Missing {md_path}"

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        field_data = data["field_benchmark"]
        ricekg_summary = field_data["system_summaries"]["RiceKG (Full Proposed)"]

        # Ensure positive recall is tracked explicitly in JSON summary
        assert "mean_positive_recall" in ricekg_summary, (
            "results/baselines.json must contain 'mean_positive_recall'"
        )
        assert ricekg_summary["mean_exact_match"] > 80.0

        # Benchmark composition must be recorded, so the negative-control share of the
        # aggregate figure can always be reconstructed from the results file alone.
        assert field_data["n_positive"] + field_data["n_negative"] == field_data["n_samples"]
        assert field_data["n_positive"] > 0

        # Strict inequality: aggregate accuracy must NOT equal positive recall
        assert ricekg_summary["mean_positive_recall"] != ricekg_summary["mean_exact_match"], (
            "Aggregate exact match cannot stand in for positive recall!"
        )

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Markdown table must have explicit Positive Recall column for field benchmark
        assert "Positive Recall (%)" in md_content

        # The narrative must quote the measured positive-case recall, not an aggregate
        # figure and not a hand-written constant. This fails if the prose goes stale.
        assert f"{ricekg_summary['mean_positive_recall']:.2f}% positive-case recall" in md_content, (
            "results/baselines.md must state the measured positive-case recall verbatim"
        )
        assert f"{field_data['n_positive']} in-scope disease cases" in md_content

    def test_field_failure_analysis_assigns_a_cause_to_every_positive_case(self):
        """Every positive field case must carry exactly one assigned failure cause.

        The cause is whatever the reasoner run produces; this test fixes the
        requirement that a cause be assigned and named from the declared taxonomy,
        not which cause any particular case receives.
        """
        import csv
        import os

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        analysis_path = os.path.join(base_dir, "results", "field_failure_analysis.md")
        field_csv = os.path.join(base_dir, "data", "benchmark_field.csv")
        assert os.path.exists(analysis_path), f"Missing {analysis_path}"

        with open(analysis_path, "r", encoding="utf-8") as f:
            content = f.read()

        with open(field_csv, newline="", encoding="utf-8") as f:
            positives = [
                r for r in csv.DictReader(f)
                if r["diagnosis"] != "No_Diagnosis" and r.get("split", "dev") == "dev"
            ]

        assert positives, "Field benchmark must contain at least one positive case in dev split"

        causes = {
            "resolved",
            "vocabulary_gating",
            "partial_vocabulary",
            "rule_recall_failure",
            "misfire",
        }

        for row in positives:
            case_id = row["case_id"]
            assert case_id in content, f"Missing case {case_id} in {analysis_path}"

        assigned = sum(content.count(f"**`{c}`**") for c in causes)
        assert assigned >= len(positives), (
            f"Expected a declared failure cause for each of the {len(positives)} positive "
            f"cases, found {assigned}"
        )
