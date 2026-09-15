"""
tests/test_degradation_curve.py
-------------------------------
Unit tests verifying the degradation experiment engine (analysis/degradation_curve.py)
and asserting formal equivalence between the fast exact solver and Pellet DL forward chaining.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model
from baselines import rule_baselines
from data.generator import generate_benchmark
from analysis.degradation_curve import (
    fast_predict_ricekg,
    fast_predict_ricekg_possible,
    fast_predict_flat,
    run_degradation_experiment,
)


def test_fast_solver_equivalence_to_pellet_dl():
    """Empirically prove that fast_predict_ricekg yields 100% identical outputs to Pellet DL.

    Compares fast_predict_ricekg against model.predict_diseases(symptoms) across 20 synthetic cases.
    """
    onto = model.build_ontology()
    cases = generate_benchmark(
        n_cases=20,
        occlusion_rate=0.3,
        distractor_rate=0.1,
        coinfection_rate=0.2,
        out_of_vocab_rate=0.2,
        seed=123,
    )

    for c in cases:
        syms = c["symptoms"]
        # Pellet DL forward chaining
        pellet_out = model.predict_diseases(syms, onto=onto)
        pellet_threats = sorted([p["threat"] for p in pellet_out if p.get("threat")])

        # Fast exact solver
        fast_out = sorted(fast_predict_ricekg(syms))

        assert fast_out == pellet_threats, (
            f"Equivalence violation for symptoms {syms}: "
            f"Pellet DL produced {pellet_threats}, fast solver produced {fast_out}"
        )


def test_fast_possible_solver_equivalence_to_pellet_dl():
    """fast_predict_ricekg_possible must match model.predict_diseases(include_possible=True)."""
    onto = model.build_ontology()
    cases = generate_benchmark(
        n_cases=25,
        occlusion_rate=0.5,
        distractor_rate=0.1,
        coinfection_rate=0.2,
        out_of_vocab_rate=0.2,
        seed=789,
    )

    for c in cases:
        syms = c["symptoms"]
        pellet_out = model.predict_diseases(syms, onto=onto, include_possible=True)
        pellet_threats = sorted(p["threat"] for p in pellet_out if p.get("threat"))
        assert sorted(fast_predict_ricekg_possible(syms)) == pellet_threats, (
            f"Possible-grade equivalence violation for {syms}: Pellet={pellet_threats}"
        )


def test_fast_flat_solver_equivalence_to_pellet():
    """Prove that fast_predict_flat matches rule_baselines.predict_flat_rules under Pellet DL."""
    flat_onto = rule_baselines.get_flat_ontology()
    cases = generate_benchmark(
        n_cases=15,
        occlusion_rate=0.2,
        distractor_rate=0.1,
        coinfection_rate=0.1,
        out_of_vocab_rate=0.2,
        seed=456,
    )

    for c in cases:
        syms = c["symptoms"]
        pellet_flat = sorted(rule_baselines.predict_flat_rules(syms, onto=flat_onto))
        fast_flat = sorted(fast_predict_flat(syms))
        assert fast_flat == pellet_flat, (
            f"Flat equivalence violation for {syms}: Pellet={pellet_flat}, Fast={fast_flat}"
        )


def test_degradation_experiment_quick_run():
    """Verify end-to-end execution of degradation experiment on a small sweep."""
    sweep = [0.0, 0.4, 0.8]
    res = run_degradation_experiment(
        occlusion_sweep=sweep,
        n_cases=40,
        num_seeds=2,
        verbose=False,
    )

    assert "metadata" in res
    assert "systems" in res
    systems = res["systems"]

    assert "RiceKG (Full Proposed)" in systems
    assert "Rule: Flat Single-Tier" in systems
    assert "Rule: Nearest Prototype" in systems
    assert "Random Forest" in systems

    # Check monotonicity of RiceKG degradation
    rk = systems["RiceKG (Full Proposed)"]
    rec_0 = rk["0.0"]["positive_recall_mean"]
    rec_8 = rk["0.8"]["positive_recall_mean"]
    assert rec_0 > rec_8, (
        f"RiceKG recall must degrade under severe occlusion (rec_0={rec_0}, rec_8={rec_8})"
    )
