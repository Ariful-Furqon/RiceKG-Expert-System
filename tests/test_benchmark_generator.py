import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ricekg import model
from ricekg import evaluate
from data.generator import (
    generate_benchmark,
    export_benchmark_to_csv,
    get_in_scope_threats,
    get_canonical_antecedents,
    explain_historical_suite_reproducibility,
)


def test_generator_determinism():
    # Identical seeds must yield byte-identical outputs across repeated calls.
    run_1 = generate_benchmark(
        n_cases=50,
        occlusion_rate=0.25,
        distractor_rate=0.15,
        coinfection_rate=0.10,
        out_of_vocab_rate=0.20,
        seed=1337,
    )
    run_2 = generate_benchmark(
        n_cases=50,
        occlusion_rate=0.25,
        distractor_rate=0.15,
        coinfection_rate=0.10,
        out_of_vocab_rate=0.20,
        seed=1337,
    )
    assert run_1 == run_2, "Generator must be strictly deterministic under identical seeds"


def test_generator_seed_divergence():
    # Different seeds must yield distinct stochastic draws.
    run_a = generate_benchmark(
        n_cases=30,
        occlusion_rate=0.3,
        distractor_rate=0.1,
        coinfection_rate=0.1,
        out_of_vocab_rate=0.2,
        seed=42,
    )
    run_b = generate_benchmark(
        n_cases=30,
        occlusion_rate=0.3,
        distractor_rate=0.1,
        coinfection_rate=0.1,
        out_of_vocab_rate=0.2,
        seed=999,
    )
    assert run_a != run_b, "Different seeds must produce different benchmark samples"


def test_rule_registry_linkage():
    # All antecedents and threat names must be derived dynamically from RULE_REGISTRY.
    threats = get_in_scope_threats()
    canonical = get_canonical_antecedents()

    expected_threats = sorted(list({r["threat"] for r in model.RULE_REGISTRY}))
    assert threats == expected_threats
    assert len(threats) == 6

    for t in threats:
        assert t in canonical
        assert len(canonical[t]) >= 2
        for sym in canonical[t]:
            assert sym in model.ALL_SYMPTOMS


def test_provenance_and_metadata_embedding():
    # Every generated case must declare provenance='rule_derived' and parameter metadata.
    cases = generate_benchmark(
        n_cases=25,
        occlusion_rate=0.35,
        distractor_rate=0.15,
        coinfection_rate=0.20,
        out_of_vocab_rate=0.25,
        seed=777,
    )
    assert len(cases) == 25
    for c in cases:
        assert c["provenance"] == "rule_derived"
        assert "generator_parameters" in c
        params = c["generator_parameters"]
        assert params["occlusion_rate"] == 0.35
        assert params["distractor_rate"] == 0.15
        assert params["coinfection_rate"] == 0.20
        assert params["out_of_vocab_rate"] == 0.25
        assert params["seed"] == 777
        assert isinstance(c["symptoms"], list)
        assert isinstance(c["diagnosis"], str)


def test_zero_occlusion_preserves_canonical_profiles():
    # At occlusion_rate=0.0 and distractor_rate=0.0, single-threat cases retain 100% canonical symptoms.
    cases = generate_benchmark(
        n_cases=50,
        occlusion_rate=0.0,
        distractor_rate=0.0,
        coinfection_rate=0.0,
        out_of_vocab_rate=0.0,
        seed=101,
    )
    canonical = get_canonical_antecedents()
    for c in cases:
        threat = c["diagnosis"]
        expected_syms = canonical[threat]
        assert sorted(c["symptoms"]) == expected_syms, (
            f"Case {c['case_id']} with zero occlusion must match canonical symptoms exactly"
        )


def test_occlusion_monotonicity():
    # Higher occlusion rates must monotonically decrease the average symptom count per positive case.
    low_occ = generate_benchmark(
        n_cases=200,
        occlusion_rate=0.1,
        distractor_rate=0.0,
        coinfection_rate=0.0,
        out_of_vocab_rate=0.0,
        seed=555,
    )
    high_occ = generate_benchmark(
        n_cases=200,
        occlusion_rate=0.7,
        distractor_rate=0.0,
        coinfection_rate=0.0,
        out_of_vocab_rate=0.0,
        seed=555,
    )
    mean_low = sum(len(c["symptoms"]) for c in low_occ) / len(low_occ)
    mean_high = sum(len(c["symptoms"]) for c in high_occ) / len(high_occ)
    assert mean_low > mean_high, (
        f"Mean symptom count under low occlusion ({mean_low:.2f}) must exceed high occlusion ({mean_high:.2f})"
    )


def test_out_of_vocab_rate_controls():
    # out_of_vocab_rate=1.0 must generate strictly out-of-scope controls and negative controls.
    cases = generate_benchmark(
        n_cases=60,
        occlusion_rate=0.2,
        distractor_rate=0.1,
        coinfection_rate=0.0,
        out_of_vocab_rate=1.0,
        seed=888,
    )
    valid_targets = {
        "No_Diagnosis",
        model.INSECT_OUT_OF_SCOPE_TARGET,
        model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET,
    }
    for c in cases:
        assert c["diagnosis"] in valid_targets, f"Unexpected target {c['diagnosis']} in pure out-of-vocab set"


def test_coinfection_rate():
    # coinfection_rate=1.0 (with oov=0.0) must produce multi-threat pairs.
    cases = generate_benchmark(
        n_cases=40,
        occlusion_rate=0.0,
        distractor_rate=0.0,
        coinfection_rate=1.0,
        out_of_vocab_rate=0.0,
        seed=999,
    )
    for c in cases:
        assert " and " in c["diagnosis"], f"Expected coinfection pair, got {c['diagnosis']}"
        assert len(c["expected"]) == 2


def test_csv_export_and_evaluation_compatibility(tmp_path):
    # Exported CSV must be cleanly readable by evaluate.load_data().
    cases = generate_benchmark(
        n_cases=30,
        occlusion_rate=0.2,
        distractor_rate=0.1,
        coinfection_rate=0.1,
        out_of_vocab_rate=0.2,
        seed=42,
    )
    csv_file = tmp_path / "test_benchmark.csv"
    export_benchmark_to_csv(cases, str(csv_file))
    assert csv_file.exists()

    loaded = evaluate.load_data(str(csv_file))
    assert len(loaded) == 30
    for original, read in zip(cases, loaded):
        assert set(original["symptoms"]) == set(read["symptoms"])
        assert original["raw_target"] == read["raw_target"]
        assert read["provenance"] == "rule_derived"


def test_historical_suite_reproducibility_documentation():
    # explain_historical_suite_reproducibility() must provide complete formal mappings.
    info = explain_historical_suite_reproducibility()
    assert "tier_mappings" in info
    assert "non_reproducible_aspects_of_legacy_csv" in info
    assert "T1_canonical" in info["tier_mappings"]
    assert "T6_controls" in info["tier_mappings"]
