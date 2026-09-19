from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ricekg import model


def get_in_scope_threats() -> List[str]:
    # Return sorted list of active in-scope threat classes from RULE_REGISTRY.
    return sorted(list({r["threat"] for r in model.RULE_REGISTRY}))


def get_canonical_antecedents() -> Dict[str, List[str]]:
    # Return dictionary mapping threat name to sorted list of Tier-1 canonical antecedents.
    canonical = {}
    for r in model.RULE_REGISTRY:
        if r.get("tier") == "tier1":
            canonical[r["threat"]] = sorted(r["antecedents"])
    return canonical


def get_relaxed_antecedents() -> Dict[str, List[str]]:
    # Return dictionary mapping threat name to the sorted antecedents of its primary Tier-2 rule.
    relaxed = {}
    for r in model.RULE_REGISTRY:
        if r.get("tier") == "tier2":
            relaxed.setdefault(r["threat"], sorted(r["antecedents"]))
    return relaxed


def get_distractor_pool() -> List[str]:
    # Return pool of non-diagnostic environmental / contextual symptoms.
    pool = [
        s for s, cat in model.OBSERVATION_CATEGORIES.items()
        if cat == "hasEpidemiologicalContext"
    ]
    # Add unspecific chlorosis/necrosis terms that are not pathognomonic
    for s in ["Plant_Yellowing", "Leaf_Discoloration_Yellow", "Necrotic_Spots"]:
        if s not in pool and s in model.ALL_SYMPTOMS:
            pool.append(s)
    return sorted(pool)


def generate_benchmark(
    n_cases: int,
    occlusion_rate: float,
    distractor_rate: float,
    coinfection_rate: float,
    out_of_vocab_rate: float,
    seed: int,
) -> List[Dict[str, Any]]:
    # Generate a parameterised diagnostic benchmark dataset.
    #
    # :param n_cases: Total number of test cases to generate.
    # :param occlusion_rate: Probability of masking each canonical antecedent [0.0, 1.0].
    # :param distractor_rate: Probability of adding non-diagnostic contextual symptoms [0.0, 1.0].
    # :param coinfection_rate: Fraction of in-scope cases carrying two simultaneous threats [0.0, 1.0].
    # :param out_of_vocab_rate: Fraction of cases representing out-of-scope / negative controls [0.0, 1.0].
    # :param seed: Random seed guaranteeing byte-identical determinism.
    # :return: List of case dictionaries with symptoms, target, expected, and provenance.
    if not (0.0 <= occlusion_rate <= 1.0):
        raise ValueError(f"occlusion_rate must be between 0.0 and 1.0, got {occlusion_rate}")
    if not (0.0 <= distractor_rate <= 1.0):
        raise ValueError(f"distractor_rate must be between 0.0 and 1.0, got {distractor_rate}")
    if not (0.0 <= coinfection_rate <= 1.0):
        raise ValueError(f"coinfection_rate must be between 0.0 and 1.0, got {coinfection_rate}")
    if not (0.0 <= out_of_vocab_rate <= 1.0):
        raise ValueError(f"out_of_vocab_rate must be between 0.0 and 1.0, got {out_of_vocab_rate}")

    rng = random.Random(seed)
    threats = get_in_scope_threats()
    canonical = get_canonical_antecedents()
    distractors = get_distractor_pool()

    cases: List[Dict[str, Any]] = []

    for idx in range(n_cases):
        case_id = f"GEN_{seed}_{idx+1:04d}"
        case_symptoms: Set[str] = set()
        is_oov = rng.random() < out_of_vocab_rate

        if is_oov:
            # Out-of-vocabulary control case
            # Split among 3 distinct negative control archetypes:
            # 1. Insect damage (triggers out-of-scope insect gate)
            # 2. Non-modeled pathogen signs (triggers out-of-scope disease differential)
            # 3. Insufficient non-specific signs (triggers No_Diagnosis)
            oov_type = rng.choice(["insect", "non_modeled_pathogen", "insufficient"])

            if oov_type == "insect":
                # Sample 2 to 4 insect-specific signs
                k = min(len(model.INSECT_SPECIFIC_SIGNS), rng.randint(2, 4))
                sampled = rng.sample(model.INSECT_SPECIFIC_SIGNS, k)
                case_symptoms.update(sampled)
                diagnosis = model.INSECT_OUT_OF_SCOPE_TARGET
                expected = [model.INSECT_OUT_OF_SCOPE_TARGET]

            elif oov_type == "non_modeled_pathogen":
                # Sample 1 to 3 non-modeled pathogen signs
                k = min(len(model.NON_MODELED_PATHOGEN_SIGNS), rng.randint(1, 3))
                sampled = rng.sample(model.NON_MODELED_PATHOGEN_SIGNS, k)
                case_symptoms.update(sampled)
                diagnosis = model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET
                expected = [model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET]

            else:
                # 1 isolated non-specific symptom that does not trigger any rule
                # Pick an isolated contextual or general sign
                safe_candidates = [
                    s for s in distractors
                    if s not in model.INSECT_SPECIFIC_SIGNS and s not in model.NON_MODELED_PATHOGEN_SIGNS
                ]
                sampled = [rng.choice(safe_candidates)] if safe_candidates else ["Uniform_Field_Infection"]
                case_symptoms.update(sampled)
                diagnosis = "No_Diagnosis"
                expected = []

        else:
            # In-scope threat case
            is_coinfection = (rng.random() < coinfection_rate) and (len(threats) >= 2)
            if is_coinfection:
                active_threats = sorted(rng.sample(threats, 2))
            else:
                active_threats = [rng.choice(threats)]

            # Generate observed symptoms for each active threat under occlusion
            for t in active_threats:
                c_symptoms = canonical.get(t, [])
                retained: List[str] = []
                for sym in c_symptoms:
                    if rng.random() >= occlusion_rate:
                        retained.append(sym)

                # If occlusion_rate < 1.0 and everything was occluded by chance, keep at least one symptom
                if not retained and c_symptoms and occlusion_rate < 1.0:
                    retained.append(rng.choice(c_symptoms))

                case_symptoms.update(retained)

            # Apply distractor perturbation
            if rng.random() < distractor_rate:
                available_distractors = [d for d in distractors if d not in case_symptoms]
                if available_distractors:
                    num_dist = rng.randint(1, min(2, len(available_distractors)))
                    sampled_dist = rng.sample(available_distractors, num_dist)
                    case_symptoms.update(sampled_dist)

            diagnosis = " and ".join(active_threats)
            expected = list(active_threats)

        sorted_symptoms = sorted(list(case_symptoms))

        cases.append({
            "case_id": case_id,
            "symptoms": sorted_symptoms,
            "diagnosis": diagnosis,
            "raw_target": diagnosis,
            "expected": expected,
            "provenance": "rule_derived",
            "generator_parameters": {
                "occlusion_rate": round(occlusion_rate, 4),
                "distractor_rate": round(distractor_rate, 4),
                "coinfection_rate": round(coinfection_rate, 4),
                "out_of_vocab_rate": round(out_of_vocab_rate, 4),
                "seed": seed,
                "case_index": idx + 1,
            }
        })

    return cases


def export_benchmark_to_csv(cases: List[Dict[str, Any]], filepath: str) -> None:
    # Export generated benchmark cases to a CSV conforming to evaluate.load_data().
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    max_symptoms = max((len(c["symptoms"]) for c in cases), default=6)
    max_symptoms = max(max_symptoms, 6)
    symptom_cols = [f"symptom_{i+1}" for i in range(max_symptoms)]
    header = symptom_cols + ["diagnosis", "provenance", "case_id"]

    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for c in cases:
            row = list(c["symptoms"]) + [""] * (max_symptoms - len(c["symptoms"]))
            row.append(c["diagnosis"])
            row.append(c["provenance"])
            row.append(c["case_id"])
            writer.writerow(row)


def explain_historical_suite_reproducibility() -> Dict[str, Any]:
    # Document how the parameterised generator formalizes the static T1–T6 construction.
    return {
        "tier_mappings": {
            "T1_canonical": "Corresponds to generate_benchmark with occlusion_rate=0.0, distractor_rate=0.0, coinfection_rate=0.0, out_of_vocab_rate=0.0.",
            "T2_relaxed": "Represents partial scouting profiles, corresponding to occlusion_rate targeting the difference between Tier-1 and Tier-2 antecedents.",
            "T3_coinfection": "Corresponds to coinfection_rate > 0.0 with disjoint antecedent unions of distinct threats.",
            "T4_distractor": "Corresponds to distractor_rate > 0.0 perturbing profiles with non-diagnostic context terms.",
            "T5_partial": "Corresponds to intermediate occlusion_rate (0.2 - 0.5) generating incomplete symptom subsets.",
            "T6_controls": "Corresponds to out_of_vocab_rate > 0.0 distributing across insect damage, unmodeled pathogens, and insufficient signs."
        },
        "non_reproducible_aspects_of_legacy_csv": [
            "The legacy 80-case suite (dataText.csv) was authored manually by knowledge engineers who hand-selected arbitrary combinations and specific insect pest cases prior to the Part 5 scope narrowing.",
            "Manual case numbers in the legacy suite (e.g. Case 39 with Rainy_Season_Outbreak, Case 40 with Deadheart_Seedling) were idiosyncratic point choices rather than draws from a stated distribution.",
            "Stochastic generation under stated parameter distributions replaces ad hoc manual curation with a formally controlled experimental instrument."
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Generate parameterised RiceKG benchmark datasets.")
    parser.add_argument("--n-cases", type=int, default=500, help="Number of benchmark cases to generate.")
    parser.add_argument("--occlusion", type=float, default=0.2, help="Antecedent occlusion rate [0.0 - 1.0].")
    parser.add_argument("--distractors", type=float, default=0.1, help="Contextual distractor rate [0.0 - 1.0].")
    parser.add_argument("--coinfection", type=float, default=0.1, help="Co-infection rate [0.0 - 1.0].")
    parser.add_argument("--oov", type=float, default=0.2, help="Out-of-vocabulary rate [0.0 - 1.0].")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation.")
    parser.add_argument("--output", type=str, default="data/benchmark_generated.csv", help="Output CSV path.")
    args = parser.parse_args()

    cases = generate_benchmark(
        n_cases=args.n_cases,
        occlusion_rate=args.occlusion,
        distractor_rate=args.distractors,
        coinfection_rate=args.coinfection,
        out_of_vocab_rate=args.oov,
        seed=args.seed,
    )
    export_benchmark_to_csv(cases, args.output)
    print(f"Successfully generated {len(cases)} cases to {args.output} (seed={args.seed})")


if __name__ == "__main__":
    main()
