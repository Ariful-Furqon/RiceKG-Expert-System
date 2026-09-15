"""
tests/test_knn_determinism.py
-----------------------------
k-NN on binary symptom vectors meets many equidistant neighbours. With algorithm="auto",
sklearn may pick a tree search in one environment and brute force in another, and the two
break ties differently: the committed Part 7 results showed holdout Hit@1 55.56% (tree search)
where this environment gives 61.11% (brute force) on identical data and code.

Asserts that:
1. The k-NN baseline pins its neighbour-search algorithm.
2. The tie-sensitivity analysis is deterministic and its span contains the reported
   fixed-order figure.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import evaluate
from baselines import ml_baselines
from analysis import differential_analysis as da

FIELD_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "benchmark_field.csv")


def test_knn_neighbour_search_is_pinned():
    clf = ml_baselines.get_ml_models()["k-NN"]
    assert clf.algorithm == "brute", "algorithm='auto' makes k-NN tie-breaking environment-dependent"


def _encoded_split(split):
    cases = evaluate.load_data(FIELD_CSV, split=split)
    X = np.array([ml_baselines.encode_symptoms(c["symptoms"]) for c in cases])
    Y = np.array([ml_baselines.encode_labels(c.get("raw_target", "")) for c in cases])
    sp = ml_baselines.get_5x2_splits(X, Y, random_state=42)[0]
    return cases, X, Y, np.asarray(sp["train_indices"]), np.asarray(sp["test_indices"])


def _fixed_order_knn_metrics(cases, X, Y, tr, te):
    ranked = [[] for _ in cases]
    for a, b in [(tr, te), (te, tr)]:
        clf = ml_baselines.get_ml_models()["k-NN"]
        clf.fit(X[a], Y[a])
        probs = da._positive_class_probs(clf.predict_proba(X[b]))
        for local_i, global_i in enumerate(b):
            ranked[global_i] = da.rank_ml_predictions(probs[local_i], k=3)
    return da.compute_top_k_metrics_for_system(cases, ranked, "k-NN")


@pytest.mark.parametrize("split", ["eval", "holdout"])
def test_tie_sensitivity_is_deterministic_and_brackets_reported_value(split):
    cases, X, Y, tr, te = _encoded_split(split)

    first = da.knn_tie_sensitivity(X, Y, cases, tr, te, n_orders=10)
    second = da.knn_tie_sensitivity(X, Y, cases, tr, te, n_orders=10)
    assert first == second

    reported = _fixed_order_knn_metrics(cases, X, Y, tr, te)
    for key in ("hit_at_1_any", "hit_at_3_any"):
        lo, hi = first[key]
        # The fixed order is not one of the permutations, so widen by one case.
        step = 100.0 / reported["n_positive"]
        assert lo - step <= reported[key] <= hi + step, (split, key, reported[key], first[key])
    assert first["tie_at_k_boundary"] > 0
