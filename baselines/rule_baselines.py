"""
baselines/rule_baselines.py
---------------------------
Rule-based baselines for RiceKG comparative evaluation:

1. Naive Symptom-Count Nearest-Prototype Matcher:
   Constructs a prototype symptom profile for each threat class from the canonical
   rule definitions in model.RULE_REGISTRY. Computes observed symptom overlap and
   Jaccard similarity against each prototype profile.

2. Flat Single-Tier Rule Baseline:
   Reuses the unstratified single-tier OWL 2 DL ontology already exposed by
   model.build_ontology(flat_consequents=True) from P0-2 with Pellet DL reasoning.
   Does NOT reimplement rules.
"""

import os
import sys
from typing import List, Dict, Set, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import model
import evaluate

ALL_THREATS = model.PESTS + model.DISEASES

# Build canonical threat prototypes from Tier-1 rules
def _build_threat_prototypes() -> Dict[str, Set[str]]:
    prototypes: Dict[str, Set[str]] = {t: set() for t in ALL_THREATS}
    for rule in model.RULE_REGISTRY:
        if rule.get("tier") == "tier1":
            threat = rule["threat"]
            if threat in prototypes:
                prototypes[threat].update(rule["antecedents"])
    return prototypes

THREAT_PROTOTYPES: Dict[str, Set[str]] = _build_threat_prototypes()

# Cached flat ontology instance for rule baseline (b)
_FLAT_ONTO = None


def get_flat_ontology():
    """Returns a cached instance of the flat single-tier ontology world."""
    global _FLAT_ONTO
    if _FLAT_ONTO is None:
        _FLAT_ONTO = model.build_ontology(flat_consequents=True)
    return _FLAT_ONTO


def predict_nearest_prototype(symptoms: List[str], min_overlap: int = 2, min_jaccard: float = 0.25) -> List[str]:
    """(a) Naive symptom-count nearest-prototype matcher.
    
    Matches observed symptoms against each threat's canonical symptom profile.
    Predicts threats that satisfy minimum absolute symptom overlap and minimum
    Jaccard similarity. If no symptoms match any prototype, returns an empty list
    representing 'No_Diagnosis'.
    """
    obs_set = set(symptoms)
    if not obs_set:
        return []

    scores = {}
    for threat, proto_set in THREAT_PROTOTYPES.items():
        overlap = len(obs_set & proto_set)
        union = len(obs_set | proto_set)
        jaccard = overlap / union if union > 0 else 0.0
        scores[threat] = {"overlap": overlap, "jaccard": jaccard}

    diagnoses = [
        threat for threat, sc in scores.items()
        if sc["overlap"] >= min_overlap and sc["jaccard"] >= min_jaccard
    ]

    # If none met the combined threshold but there is a clear dominant match
    if not diagnoses:
        best_threat = max(scores.keys(), key=lambda t: (scores[t]["overlap"], scores[t]["jaccard"]))
        if scores[best_threat]["overlap"] >= min_overlap:
            diagnoses.append(best_threat)

    # If still no diagnosis, check if symptoms indicate out-of-scope insect damage
    if not diagnoses and model.insect_damage_evidence(obs_set):
        return [model.INSECT_OUT_OF_SCOPE_TARGET]

    return sorted(diagnoses)


def predict_flat_rules(symptoms: List[str], onto=None) -> List[str]:
    """(b) Flat single-tier rule set already exposed by model.build_ontology(flat_consequents=True).
    Reuses model.predict_diseases_flat without reimplementing rules.
    """
    target_onto = onto or get_flat_ontology()
    return model.predict_diseases_flat(symptoms, onto=target_onto)


def evaluate_rule_baselines(cases: List[Dict[str, Any]], onto=None) -> Dict[str, Any]:
    """Evaluates both rule baselines across an evaluation dataset."""
    from baselines.ml_baselines import encode_labels, compute_multilabel_metrics, ALL_THREATS
    import numpy as np

    flat_onto = onto or get_flat_ontology()
    n = len(cases)
    Y_true = np.zeros((n, len(ALL_THREATS)), dtype=int)
    Y_proto = np.zeros((n, len(ALL_THREATS)), dtype=int)
    Y_flat = np.zeros((n, len(ALL_THREATS)), dtype=int)

    for i, case in enumerate(cases):
        Y_true[i] = encode_labels(case.get("raw_target", ""))

        proto_preds = predict_nearest_prototype(case["symptoms"])
        Y_proto[i] = encode_labels(proto_preds)

        flat_preds = predict_flat_rules(case["symptoms"], onto=flat_onto)
        Y_flat[i] = encode_labels(flat_preds)

    proto_metrics = compute_multilabel_metrics(Y_true, Y_proto)
    flat_metrics = compute_multilabel_metrics(Y_true, Y_flat)

    return {
        "Nearest Prototype": {
            "metrics": proto_metrics,
            "preds": Y_proto,
        },
        "Flat Single-Tier Rules": {
            "metrics": flat_metrics,
            "preds": Y_flat,
        },
        "Y_true": Y_true
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["verification", "synthetic", "augmented", "field"], default="verification")
    args = parser.parse_args()

    csv_file = evaluate.FIELD_CSV if args.dataset == "field" else evaluate.DEFAULT_VERIFICATION_CSV
    cases = evaluate.load_data(csv_file)
    print(f"Evaluating Rule baselines on {args.dataset} ({len(cases)} cases)...")
    res = evaluate_rule_baselines(cases)

    print("-" * 80)
    print(f"{'Rule Baseline':<30} | {'Exact Match (%)':<18} | {'Micro F1 (%)':<15}")
    print("-" * 80)
    for name in ["Nearest Prototype", "Flat Single-Tier Rules"]:
        m = res[name]["metrics"]
        print(f"{name:<30} | {m['exact_match']:>6.2f}%            | {m['micro_f1']:>6.2f}%")
