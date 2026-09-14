"""
baselines/ml_baselines.py
-------------------------
Multi-label machine learning baselines for RiceKG evaluation.

Encodes cases into a 45-dimensional binary symptom vector (indexed strictly
by model.ALL_SYMPTOMS) and multi-label targets across 10 biotic threat classes
(model.PESTS + model.DISEASES), with 'No_Diagnosis' represented as an all-zero
label vector.

Implements 5 ML architectures:
1. Decision Tree (DecisionTreeClassifier, random_state=42)
2. Random Forest (RandomForestClassifier, random_state=42)
3. Multinomial Naive Bayes (OneVsRestClassifier(MultinomialNB()))
4. k-Nearest Neighbors (KNeighborsClassifier(n_neighbors=3))
5. One-vs-Rest Logistic Regression (OneVsRestClassifier(LogisticRegression(random_state=42)))

Evaluates via stratified 5x2-fold cross-validation with transparent fallback
to KFold when multi-label combination counts are < 2.
"""

import os
import pathlib
import sys
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import KFold

# Ensure repository root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _repo_relative(path: str) -> str:
    """Return `path` relative to the repository root with POSIX separators.

    Absolute paths leak the author's username and institution into
    results/*.json, which breaks double-blind anonymisation.
    """
    try:
        return pathlib.PurePath(os.path.relpath(path, BASE_DIR)).as_posix()
    except ValueError:
        return os.path.basename(path)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import model
import evaluate

# Canonical 10 target threat classes (5 pests + 5 diseases)
ALL_THREATS: List[str] = model.PESTS + model.DISEASES
THREAT_TO_IDX: Dict[str, int] = {threat: idx for idx, threat in enumerate(ALL_THREATS)}
IDX_TO_THREAT: Dict[int, str] = {idx: threat for idx, threat in enumerate(ALL_THREATS)}

# Canonical symptom order (45 dimensions)
SYMPTOM_ORDER: List[str] = model.ALL_SYMPTOMS
SYMPTOM_TO_IDX: Dict[str, int] = {symptom: idx for idx, symptom in enumerate(SYMPTOM_ORDER)}


def encode_symptoms(symptoms: List[str]) -> np.ndarray:
    """Encodes an iterable of symptom strings into a 45-dimensional binary numpy vector.
    Indices strictly correspond to model.ALL_SYMPTOMS.
    """
    vec = np.zeros(len(SYMPTOM_ORDER), dtype=int)
    s_set = set(symptoms)
    for s in s_set:
        if s in SYMPTOM_TO_IDX:
            vec[SYMPTOM_TO_IDX[s]] = 1
    return vec


def decode_symptoms(vec: np.ndarray) -> List[str]:
    """Inverse mapping: converts a 45-dimensional binary vector back to symptom strings."""
    return [SYMPTOM_ORDER[i] for i in range(len(SYMPTOM_ORDER)) if vec[i] == 1]


def encode_labels(raw_target: Any) -> np.ndarray:
    """Encodes a diagnosis target string or list into a 10-dimensional binary vector.
    'No_Diagnosis' or empty input produces an all-zero vector (not an 11th class).
    Multiple threats joined by ' and ' are each marked with 1.
    """
    vec = np.zeros(len(ALL_THREATS), dtype=int)
    if not raw_target:
        return vec

    if isinstance(raw_target, str):
        if raw_target.strip() == "No_Diagnosis":
            return vec
        threats = [t.strip() for t in raw_target.split(" and ") if t.strip()]
    elif isinstance(raw_target, (list, tuple, set)):
        threats = [t.strip() for t in raw_target if t.strip() and t.strip() != "No_Diagnosis"]
    else:
        return vec

    for t in threats:
        if t in THREAT_TO_IDX:
            vec[THREAT_TO_IDX[t]] = 1
    return vec


def decode_labels(vec: np.ndarray) -> List[str]:
    """Inverse mapping: converts a 10-dimensional binary vector back to a list of threat names.
    An all-zero vector returns an empty list, representing No_Diagnosis.
    """
    return [ALL_THREATS[i] for i in range(len(ALL_THREATS)) if vec[i] == 1]


def load_and_encode_dataset(csv_path: str, split: str = None) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """Loads a benchmark CSV via evaluate.load_data() and encodes features (X) and multi-labels (Y).

    `split` restricts the rows to one dataset split ('dev' or 'eval'); None uses every row.
    Returns (X, Y, raw_cases).
    """
    cases = evaluate.load_data(csv_path, split=split)
    n = len(cases)
    X = np.zeros((n, len(SYMPTOM_ORDER)), dtype=int)
    Y = np.zeros((n, len(ALL_THREATS)), dtype=int)

    for i, case in enumerate(cases):
        X[i] = encode_symptoms(case["symptoms"])
        Y[i] = encode_labels(case.get("raw_target", ""))

    return X, Y, cases


def get_5x2_splits(X: np.ndarray, Y: np.ndarray, random_state: int = 42) -> List[Dict[str, Any]]:
    """Generates stratified 5x2-fold cross-validation splits.
    
    Examines if exact multi-label tuples can be split with StratifiedKFold (requires >=2
    instances per label combination). When rare combinations appear once (n=80 and n=32
    benchmarks), transparently logs and falls back to plain KFold(n_splits=2, shuffle=True),
    recording the split type for honest reporting.
    """
    n_samples = len(X)
    splits = []

    # Map each multi-label row to a string tuple representation
    label_tuples = [tuple(row) for row in Y]
    unique_tuples, counts = np.unique(label_tuples, axis=0, return_counts=True)
    min_count = np.min(counts)

    can_stratify = (min_count >= 2)

    for rep in range(5):
        seed = random_state + rep * 10
        if can_stratify:
            from sklearn.model_selection import StratifiedKFold
            # Encode label tuples into categorical integers for StratifiedKFold
            tuple_to_class = {tuple(t): idx for idx, t in enumerate(unique_tuples)}
            y_cat = np.array([tuple_to_class[tuple(r)] for r in Y])
            splitter = StratifiedKFold(n_splits=2, shuffle=True, random_state=seed)
            split_name = "StratifiedKFold(n_splits=2)"
            fold_pairs = list(splitter.split(X, y_cat))
        else:
            splitter = KFold(n_splits=2, shuffle=True, random_state=seed)
            split_name = f"KFold(n_splits=2) [Fallback: {np.sum(counts < 2)} rare combinations have n=1]"
            fold_pairs = list(splitter.split(X))

        for fold_idx, (train_idx, test_idx) in enumerate(fold_pairs):
            splits.append({
                "iteration": rep + 1,
                "fold": fold_idx + 1,
                "split_name": split_name,
                "train_indices": train_idx,
                "test_indices": test_idx,
            })

    return splits


def get_ml_models(random_state: int = 42) -> Dict[str, Any]:
    """Instantiates the 5 baseline machine learning classifiers with fixed random_state."""
    return {
        "Decision Tree": DecisionTreeClassifier(random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "Multinomial Naive Bayes": OneVsRestClassifier(MultinomialNB()),
        "k-NN": KNeighborsClassifier(n_neighbors=3),
        "Logistic Regression (OvR)": OneVsRestClassifier(LogisticRegression(random_state=random_state, solver="liblinear")),
    }


def compute_multilabel_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes exact match ratio, micro-precision, micro-recall, and micro-F1."""
    n_cases = len(y_true)
    if n_cases == 0:
        return {"exact_match": 0.0, "micro_precision": 0.0, "micro_recall": 0.0, "micro_f1": 0.0}

    exact_matches = np.all(y_true == y_pred, axis=1)
    exact_match_acc = np.mean(exact_matches) * 100.0

    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))

    micro_prec = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
    micro_rec = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
    micro_f1 = (2 * micro_prec * micro_rec / (micro_prec + micro_rec)) if (micro_prec + micro_rec) > 0 else 0.0

    # Separate positive cases (>=1 true threat) from negative controls (0 true threats, No_Diagnosis)
    pos_mask = np.sum(y_true, axis=1) > 0
    pos_cases_count = int(np.sum(pos_mask))
    neg_cases_count = int(np.sum(~pos_mask))

    pos_correct = int(np.sum(exact_matches[pos_mask])) if pos_cases_count > 0 else 0
    pos_recall = float(pos_correct / pos_cases_count * 100.0) if pos_cases_count > 0 else 0.0

    neg_correct = int(np.sum(exact_matches[~pos_mask])) if neg_cases_count > 0 else 0
    neg_accuracy = float(neg_correct / neg_cases_count * 100.0) if neg_cases_count > 0 else 0.0

    return {
        "exact_match": float(exact_match_acc),
        "positive_cases_count": pos_cases_count,
        "positive_cases_correct": pos_correct,
        "positive_case_recall": float(pos_recall),
        "negative_cases_count": neg_cases_count,
        "negative_cases_correct": neg_correct,
        "negative_control_accuracy": float(neg_accuracy),
        "micro_precision": float(micro_prec),
        "micro_recall": float(micro_rec),
        "micro_f1": float(micro_f1),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "exact_matches_bool": exact_matches.tolist()
    }


def evaluate_ml_baselines(csv_path: str, random_state: int = 42) -> Dict[str, Any]:
    """Runs 5x2-fold cross validation for all ML baselines on the specified benchmark dataset.
    Returns detailed fold-level and summary results.
    """
    X, Y, cases = load_and_encode_dataset(csv_path)
    splits = get_5x2_splits(X, Y, random_state=random_state)

    model_names = list(get_ml_models().keys())
    fold_results = {name: [] for name in model_names}
    all_test_preds = {name: [] for name in model_names}
    all_test_trues = {name: [] for name in model_names}

    split_strategy = splits[0]["split_name"]

    for split in splits:
        tr_idx = split["train_indices"]
        te_idx = split["test_indices"]
        X_train, Y_train = X[tr_idx], Y[tr_idx]
        X_test, Y_test = X[te_idx], Y[te_idx]

        models = get_ml_models(random_state=random_state)
        for name, clf in models.items():
            try:
                # Handle single-class edge cases for OvR in sparse training folds
                clf.fit(X_train, Y_train)
                Y_pred = clf.predict(X_test)
                # Ensure binary format (int 0 or 1)
                Y_pred = (Y_pred > 0).astype(int)
            except Exception as e:
                # If a fold has no positive instances for any class, default to 0
                Y_pred = np.zeros_like(Y_test, dtype=int)

            metrics = compute_multilabel_metrics(Y_test, Y_pred)
            fold_results[name].append(metrics)
            all_test_preds[name].extend(Y_pred.tolist())
            all_test_trues[name].extend(Y_test.tolist())

    # Aggregate metrics across 10 folds
    summary = {}
    for name in model_names:
        em_vals = [f["exact_match"] for f in fold_results[name]]
        f1_vals = [f["micro_f1"] for f in fold_results[name]]
        prec_vals = [f["micro_precision"] for f in fold_results[name]]
        rec_vals = [f["micro_recall"] for f in fold_results[name]]

        summary[name] = {
            "mean_exact_match": float(np.mean(em_vals)),
            "std_exact_match": float(np.std(em_vals)),
            "mean_micro_f1": float(np.mean(f1_vals)),
            "std_micro_f1": float(np.std(f1_vals)),
            "mean_micro_precision": float(np.mean(prec_vals)),
            "mean_micro_recall": float(np.mean(rec_vals)),
            "fold_metrics": fold_results[name],
            "pooled_preds": np.array(all_test_preds[name]),
            "pooled_trues": np.array(all_test_trues[name]),
        }

    return {
        "csv_path": _repo_relative(csv_path),
        "n_samples": len(X),
        "n_features": X.shape[1],
        "n_classes": Y.shape[1],
        "split_strategy": split_strategy,
        "splits": splits,
        "summary": summary
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run ML baselines on RiceKG benchmark")
    parser.add_argument("--dataset", choices=["verification", "synthetic", "augmented", "field"], default="verification")
    args = parser.parse_args()

    csv_file = evaluate.FIELD_CSV if args.dataset == "field" else evaluate.DEFAULT_VERIFICATION_CSV
    print(f"Evaluating ML baselines on {args.dataset} ({csv_file})...")
    res = evaluate_ml_baselines(csv_file)
    print(f"Split strategy: {res['split_strategy']}")
    print("-" * 80)
    print(f"{'Model':<30} | {'Exact Match (%)':<18} | {'Micro F1 (%)':<15}")
    print("-" * 80)
    for model_name, s in res["summary"].items():
        print(f"{model_name:<30} | {s['mean_exact_match']:>6.2f} +/- {s['std_exact_match']:>4.2f}    | {s['mean_micro_f1']:>6.2f} +/- {s['std_micro_f1']:>4.2f}")
