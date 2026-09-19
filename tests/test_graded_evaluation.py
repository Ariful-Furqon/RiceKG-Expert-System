# Tests for the case-level graded evaluation (analysis/graded_evaluation.py) and the
# knowledge-base verification (analysis/kb_verification.py).

import json
import os

import pytest

from analysis import graded_evaluation as ge
from analysis import kb_verification as kv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRADED_JSON = os.path.join(BASE_DIR, "results", "graded_evaluation.json")


# ---------------------------------------------------------------------------
# Outcome classification
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("outputs,truth,expected", [
    ([("Rice_Blast", "suspected")], {"Rice_Blast"}, "correct"),
    ([("Rice_Blast", "confirmed"), ("False_Smut", "suspected")], {"Rice_Blast"}, "correct"),
    ([("False_Smut", "suspected")], {"Rice_Blast"}, "misfire"),
    ([("Rice_Blast", "possible")], {"Rice_Blast"}, "possible_hit"),
    ([("False_Smut", "possible")], {"Rice_Blast"}, "possible_miss"),
    ([("insect damage, out of scope", "out_of_scope")], {"Rice_Blast"}, "rejected"),
    ([], {"Rice_Blast"}, "abstain"),
    ([("Rice_Blast", "suspected")], set(), "false_alarm"),
    ([("Rice_Blast", "possible")], set(), "possible_alarm"),
    ([("signs recorded", "out_of_scope")], set(), "explicit_rejection"),
    ([], set(), "silent_abstention"),
    ([("Rice_Blast", "committed")], {"Rice_Blast"}, "correct"),
])
def test_classify(outputs, truth, expected):
    assert ge.classify(outputs, truth) == expected


def test_committed_diagnosis_outranks_possible():
    # A wrong committed diagnosis is a misfire even if the true threat is also `possible`.
    outputs = [("False_Smut", "suspected"), ("Rice_Blast", "possible")]
    assert ge.classify(outputs, {"Rice_Blast"}) == "misfire"


def test_clopper_pearson_known_values():
    assert ge.clopper_pearson(0, 17) == [0.0, 19.5]
    assert ge.clopper_pearson(2, 5) == [5.3, 85.3]
    assert ge.clopper_pearson(5, 5) == [47.8, 100.0]
    assert ge.clopper_pearson(0, 0) == [None, None]


def test_strict_view_drops_only_possible_grade():
    rk = [("Rice_Blast", "suspected"), ("False_Smut", "possible"), ("x", "out_of_scope")]
    assert ge.ricekg_strict(rk) == [("Rice_Blast", "suspected"), ("x", "out_of_scope")]


# ---------------------------------------------------------------------------
# Persisted results
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def graded():
    with open(GRADED_JSON, encoding="utf-8") as f:
        return json.load(f)


def test_outcome_counts_partition_the_cases(graded):
    for group, per_sys in graded["groups"].items():
        for system, m in per_sys.items():
            assert sum(m["positive_outcomes"].values()) == m["n_positive"], (group, system)
            assert sum(m["control_outcomes"].values()) == m["n_control"], (group, system)


def test_strict_and_possible_agree_on_committed_outcomes(graded):
    # The `possible` grade adds candidates but never changes a committed diagnosis.
    for c in graded["cases"]:
        strict, loose = c["outcome"]["RiceKG strict"], c["outcome"]["RiceKG + possible"]
        if strict in ("correct", "misfire", "false_alarm"):
            assert loose == strict, c["case_id"]


def test_case_count_matches_benchmark(graded):
    import csv
    with open(os.path.join(BASE_DIR, "data", "benchmark_field.csv"), encoding="utf-8-sig") as f:
        n = sum(1 for _ in csv.DictReader(f))
    assert len(graded["cases"]) == n


# ---------------------------------------------------------------------------
# Knowledge-base verification (structural checks; no reasoner call)
# ---------------------------------------------------------------------------

def test_every_threat_has_both_tiers():
    rules = kv.rules_by_threat()
    assert all({r["tier"] for r in rs} == {"tier1", "tier2"} for rs in rules.values())


def test_tier2_is_subset_of_tier1():
    assert all(r["tier2_subset_of_tier1"] for r in kv.check_tier_subsumption(kv.rules_by_threat()))


def test_no_rule_forces_another_threat():
    assert kv.check_cross_threat_subsumption(kv.rules_by_threat()) == []


def test_vocabulary_partition_is_complete():
    users, _ = kv.antecedent_sharing(kv.rules_by_threat())
    voc = kv.vocabulary_use(users)
    parts = set(voc["used_by_rules"]) | set(voc["gate_only"]) | set(voc["unused"])
    assert len(parts) == voc["total"]
    assert not set(voc["used_by_rules"]) & set(voc["gate_only"])
