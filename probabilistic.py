"""
RiceKG Expert System - Probabilistic Reasoning Layer (Noisy-OR)
-----------------------------------------------------------------
Implements an independent multi-label probabilistic scoring layer based on the
Noisy-OR formulation for the six in-scope rice pests and diseases.

Mathematical formulation (Protocol Section 8-F):
- Each threat t in ALL_DIAGNOSES is modeled as an independent binary hypothesis.
- P(t) = PRIOR = 0.10 (fixed a priori; uniform uninformative prior).
- For each observation e linked to t:
    P(e present | t present) = 1 - (1 - leak_e) * (1 - p_te)
    P(e present | t absent)  = leak_e
- Observed present signs contribute LR = P(e | t) / P(e | ~t).
- Unrecorded signs are marginalized out (contribute nothing, LR = 1.0).
- Recorded absent signs contribute (1 - P(e | t)) / (1 - P(e | ~t)) = 1 - p_te.
- Observations with no link to t contribute nothing (LR = 1.0).

Inference is performed in log-odds space for numerical stability.
Does not alter or write into the OWL ontology.
"""

import csv
import math
import os
from typing import Any, Collection, Dict, List, Optional, Set, Tuple

import model

PRIOR: float = 0.10
DECISION_THRESHOLD: float = 0.50

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PARAMS_CSV = os.path.join(BASE_DIR, "data", "noisy_or_parameters.csv")
DEFAULT_LEAKS_CSV = os.path.join(BASE_DIR, "data", "noisy_or_leaks.csv")


class NoisyOrParameters:
    """Holds elicited conditional probabilities, background leaks, and priors."""

    def __init__(
        self,
        links: Dict[Tuple[str, str], float],
        leaks: Dict[str, float],
        prior: float = PRIOR,
        threats: Optional[Collection[str]] = None,
    ):
        self.links = dict(links)  # (threat, observation) -> p_te
        self.leaks = dict(leaks)  # observation -> leak_e
        self.prior = float(prior)
        self.threats = list(threats) if threats is not None else list(model.ALL_DIAGNOSES)

        # Index links by threat for fast evaluation
        self.threat_links: Dict[str, Dict[str, float]] = {t: {} for t in self.threats}
        for (t, obs), p_val in self.links.items():
            if t in self.threat_links:
                self.threat_links[t][obs] = p_val


def load_noisy_or_parameters(
    params_csv: str = DEFAULT_PARAMS_CSV,
    leaks_csv: str = DEFAULT_LEAKS_CSV,
    prior: float = PRIOR,
    threats: Optional[Collection[str]] = None,
) -> NoisyOrParameters:
    """Loads Noisy-OR conditional parameters and leak priors from CSV files."""
    leaks: Dict[str, float] = {}
    if os.path.exists(leaks_csv):
        with open(leaks_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                obs = row["observation"].strip()
                leak_val = float(row["leak"].strip())
                leaks[obs] = leak_val

    links: Dict[Tuple[str, str], float] = {}
    if os.path.exists(params_csv):
        with open(params_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = row["threat"].strip()
                obs = row["observation"].strip()
                p_val = float(row["p_sign_given_threat"].strip())
                links[(t, obs)] = p_val

    return NoisyOrParameters(links=links, leaks=leaks, prior=prior, threats=threats)


# Global cached default parameters instance
_DEFAULT_PARAMS: Optional[NoisyOrParameters] = None


def get_default_parameters() -> NoisyOrParameters:
    """Returns or lazily initializes the default parameter set."""
    global _DEFAULT_PARAMS
    if _DEFAULT_PARAMS is None:
        _DEFAULT_PARAMS = load_noisy_or_parameters()
    return _DEFAULT_PARAMS


def _log_odds_to_prob(log_odds: float) -> float:
    """Numerically stable sigmoid function."""
    if log_odds > 35.0:
        return 1.0
    if log_odds < -35.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-log_odds))


def posterior_scores(
    symptoms: Collection[str],
    absent: Collection[str] = (),
    params: Optional[NoisyOrParameters] = None,
) -> Dict[str, float]:
    """
    Computes posterior probability P(threat | evidence) for all in-scope threats
    using independent binary noisy-OR formulation in log space.

    :param symptoms: Collection of observed present symptom identifiers.
    :param absent: Collection of verified absent symptom identifiers.
    :param params: Optional NoisyOrParameters instance. If None, uses default parameters.
    :return: dict mapping threat identifier -> posterior probability in [0.0, 1.0].
    """
    p_config = params if params is not None else get_default_parameters()

    present_set: Set[str] = {str(s).strip() for s in symptoms if str(s).strip()}
    absent_set: Set[str] = {str(s).strip() for s in absent if str(s).strip()}

    prior = p_config.prior
    log_prior_odds = math.log(prior) - math.log(1.0 - prior)

    scores: Dict[str, float] = {}

    for threat in p_config.threats:
        t_links = p_config.threat_links.get(threat, {})
        log_odds = log_prior_odds

        # Present signs linked to threat contribute their likelihood ratio
        for obs in present_set:
            if obs in t_links:
                p_te = t_links[obs]
                leak = p_config.leaks.get(obs, 0.05)
                p_e_given_t = 1.0 - (1.0 - leak) * (1.0 - p_te)
                p_e_given_not_t = leak
                lr = p_e_given_t / p_e_given_not_t
                log_odds += math.log(lr)

        # Absent signs linked to threat contribute (1 - P(e|t)) / (1 - P(e|~t)) = 1 - p_te
        for obs in absent_set:
            if obs in t_links:
                p_te = t_links[obs]
                lr_absent = 1.0 - p_te
                if lr_absent > 0.0:
                    log_odds += math.log(lr_absent)
                else:
                    log_odds = -float("inf")

        scores[threat] = _log_odds_to_prob(log_odds)

    return scores


def predict_probabilistic(
    symptoms: Collection[str],
    absent: Collection[str] = (),
    threshold: float = DECISION_THRESHOLD,
    apply_gates: bool = True,
    params: Optional[NoisyOrParameters] = None,
) -> List[Dict[str, Any]]:
    """
    Infers diagnoses whose posterior probability meets or exceeds threshold.

    Returns the same dict shape as model.predict_diseases:
    - threat: threat class name (or out_of_scope target)
    - grade: "probable" for predicted in-scope threats, "out_of_scope" for gates
    - confidence: float posterior probability
    - antecedent_coverage: fraction of linked symptoms observed
    - fired_rules: ["NOISY-OR"]
    - matched_symptoms: list of observed symptoms linked to the threat
    - missing_symptoms: list of linked symptoms not observed in input
    - message: diagnostic explanation or gate description

    :param symptoms: Collection of observed symptom identifiers.
    :param absent: Optional collection of confirmed absent symptom identifiers.
    :param threshold: Operating cutoff (default DECISION_THRESHOLD = 0.50).
    :param apply_gates: Whether to apply insect and non-modeled out-of-scope gates.
    :param params: Optional NoisyOrParameters instance.
    :return: List of diagnostic outcome dictionaries.
    """
    p_config = params if params is not None else get_default_parameters()
    input_symptoms = [str(s).strip() for s in (symptoms or []) if str(s).strip()]
    input_set = set(input_symptoms)

    scores = posterior_scores(input_set, absent=absent, params=p_config)

    results: List[Dict[str, Any]] = []

    for threat in p_config.threats:
        post = scores.get(threat, 0.0)
        if post >= threshold:
            t_links = p_config.threat_links.get(threat, {})
            linked_symptoms = sorted(t_links.keys())
            matched = [s for s in linked_symptoms if s in input_set]
            missing = [s for s in linked_symptoms if s not in input_set]
            cov = round(len(matched) / len(linked_symptoms), 4) if linked_symptoms else 1.0

            results.append({
                "threat": threat,
                "grade": "probable",
                "confidence": round(post, 4),
                "antecedent_coverage": cov,
                "fired_rules": ["NOISY-OR"],
                "matched_symptoms": matched,
                "missing_symptoms": missing,
            })

    # Sort deterministically: highest confidence first, then ascending threat name
    results.sort(key=lambda x: (-x["confidence"], x["threat"]))

    # Gate precedence identical to model.predict_diseases
    if not results and apply_gates:
        insect_matched = model.insect_damage_evidence(input_set)
        if insect_matched:
            results.append({
                "threat": model.INSECT_OUT_OF_SCOPE_TARGET,
                "grade": "out_of_scope",
                "confidence": 0.0,
                "antecedent_coverage": 0.0,
                "fired_rules": [],
                "matched_symptoms": insect_matched,
                "missing_symptoms": [],
                "message": model.INSECT_OUT_OF_SCOPE_RESPONSE,
            })
        else:
            neg_matched = model.negative_control_evidence(input_set)
            if neg_matched:
                results.append({
                    "threat": model.NEGATIVE_CONTROL_OUT_OF_SCOPE_TARGET,
                    "grade": "out_of_scope",
                    "confidence": 0.0,
                    "antecedent_coverage": 0.0,
                    "fired_rules": [],
                    "matched_symptoms": neg_matched,
                    "missing_symptoms": [],
                    "message": model.NEGATIVE_CONTROL_OUT_OF_SCOPE_RESPONSE,
                })

    return results


def rank_differential_probabilistic(
    symptoms: Collection[str],
    absent: Collection[str] = (),
    k: int = 3,
    apply_gates: bool = True,
    params: Optional[NoisyOrParameters] = None,
) -> List[str]:
    """
    Returns top-k ranked threat names by posterior probability.
    If apply_gates=True and an out-of-scope gate triggers, returns [] (rejection),
    matching the behavior of model.differential_diagnosis.
    """
    if k <= 0:
        return []

    input_symptoms = [str(s).strip() for s in (symptoms or []) if str(s).strip()]
    input_set = set(input_symptoms)
    if not input_set:
        return []

    p_config = params if params is not None else get_default_parameters()

    if apply_gates:
        if model.insect_damage_evidence(input_set) or model.negative_control_evidence(input_set):
            return []

    scores = posterior_scores(input_set, absent=absent, params=p_config)

    # Sort all threats by posterior descending, tie-break by name ascending
    ranked = sorted(p_config.threats, key=lambda t: (-scores.get(t, 0.0), t))

    # Only return threats whose posterior exceeds prior odds (earned positive evidence)
    # or return up to k threats with posterior > prior
    evidence_backed = [t for t in ranked if scores.get(t, 0.0) > p_config.prior]
    return evidence_backed[:k]

