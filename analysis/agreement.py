"""
Inter-Annotator Agreement Analysis (Cohen's Kappa & Fleiss' Kappa)

Computes chance-corrected inter-rater agreement over independent expert diagnoses
with non-parametric bootstrap confidence intervals. Refuses to run on empty
or missing annotation data.
"""

import os
import sys
import csv
import argparse
import numpy as np
from collections import Counter


def compute_cohens_kappa(r1, r2, categories):
    """Computes Cohen's kappa for two raters over categorical diagnoses."""
    n = len(r1)
    if n == 0:
        return 0.0, 0.0, 0.0

    # Observed agreement
    po = sum(1 for a, b in zip(r1, r2) if a == b) / n

    # Marginal frequencies
    c1 = Counter(r1)
    c2 = Counter(r2)
    pe = sum((c1[cat] / n) * (c2[cat] / n) for cat in categories)

    if pe == 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1.0 - pe)
    return kappa, po, pe


def compute_fleiss_kappa(ratings_matrix, categories):
    """
    Computes Fleiss' kappa for 3 or more raters.
    ratings_matrix: list of lists, where row i is ratings by m raters for item i.
    """
    N = len(ratings_matrix)  # number of subjects
    if N == 0:
        return 0.0, 0.0, 0.0
    n = len(ratings_matrix[0])  # number of raters per subject
    k = len(categories)  # number of categories
    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}

    # Table of counts: n_ij is number of raters who assigned item i to category j
    table = np.zeros((N, k), dtype=float)
    for i, row in enumerate(ratings_matrix):
        for val in row:
            if val in cat_to_idx:
                table[i, cat_to_idx[val]] += 1

    # p_j is the proportion of all assignments which were to the j-th category
    p_j = np.sum(table, axis=0) / (N * n)
    P_e = np.sum(p_j ** 2)

    # P_i is the extent to which raters agree on the i-th subject
    P_i = (np.sum(table ** 2, axis=1) - n) / (n * (n - 1))
    P_o = np.mean(P_i)

    if P_e == 1.0:
        kappa = 1.0
    else:
        kappa = (P_o - P_e) / (1.0 - P_e)
    return kappa, P_o, P_e


def interpret_kappa(kappa):
    if kappa < 0.0:
        return "Poor (Less than chance)"
    elif kappa <= 0.20:
        return "Slight agreement"
    elif kappa <= 0.40:
        return "Fair agreement"
    elif kappa <= 0.60:
        return "Moderate agreement"
    elif kappa <= 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


def run_agreement_analysis(input_path, n_bootstrap=1000, random_seed=42):
    if not os.path.exists(input_path):
        print(f"[STATUS] Annotation file '{input_path}' does not exist.")
        print("[NOTICE] No multi-rater annotation data collected yet. Exiting cleanly without fabricating responses.")
        return 0

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if any(v.strip() for v in r.values())]

    if not rows:
        print(f"[STATUS] Annotation file '{input_path}' has headers but 0 data rows.")
        print("[NOTICE] No field rater responses collected yet. Exiting cleanly as per anti-fabrication protocol.")
        return 0

    rater_cols = [col for col in rows[0].keys() if col.lower().startswith("annotator") or col.lower().startswith("rater")]
    if len(rater_cols) < 2:
        print(f"[ERROR] At least 2 annotator columns required (found: {rater_cols}).")
        return 1

    # Extract ratings
    all_categories = sorted(list(set(r[c].strip() for r in rows for c in rater_cols if r[c].strip())))
    print("=" * 80)
    print("INTER-ANNOTATOR AGREEMENT ANALYSIS (RICE DIAGNOSTIC SCOUTING)")
    print("=" * 80)
    print(f"Dataset File   : {input_path}")
    print(f"Sample Size (N): {len(rows)} evaluated field cases")
    print(f"Annotator Count: {len(rater_cols)} independent raters ({', '.join(rater_cols)})")
    print(f"Target Classes : {len(all_categories)} categories ({', '.join(all_categories)})")
    print("-" * 80)

    rng = np.random.RandomState(random_seed)

    if len(rater_cols) == 2:
        r1 = [r[rater_cols[0]].strip() for r in rows]
        r2 = [r[rater_cols[1]].strip() for r in rows]
        kappa, po, pe = compute_cohens_kappa(r1, r2, all_categories)

        # Bootstrap CIs
        boot_kappas = []
        n = len(rows)
        for _ in range(n_bootstrap):
            idx = rng.choice(n, size=n, replace=True)
            b_r1 = [r1[i] for i in idx]
            b_r2 = [r2[i] for i in idx]
            k_b, _, _ = compute_cohens_kappa(b_r1, b_r2, all_categories)
            boot_kappas.append(k_b)

        ci_low = np.percentile(boot_kappas, 2.5)
        ci_high = np.percentile(boot_kappas, 97.5)

        print(f"Metric         : Cohen's Kappa (κ)")
        print(f"Observed Agree : {po * 100:.2f}% (P_o = {po:.4f})")
        print(f"Chance Agree   : {pe * 100:.2f}% (P_e = {pe:.4f})")
        print(f"Cohen's Kappa  : {kappa:.4f} [95% CI: {ci_low:.4f} - {ci_high:.4f}]")
        print(f"Interpretation : {interpret_kappa(kappa)} (Landis & Koch, 1977)")

    else:
        matrix = [[r[c].strip() for c in rater_cols] for r in rows]
        kappa, po, pe = compute_fleiss_kappa(matrix, all_categories)

        # Bootstrap CIs
        boot_kappas = []
        n = len(rows)
        for _ in range(n_bootstrap):
            idx = rng.choice(n, size=n, replace=True)
            b_matrix = [matrix[i] for i in idx]
            k_b, _, _ = compute_fleiss_kappa(b_matrix, all_categories)
            boot_kappas.append(k_b)

        ci_low = np.percentile(boot_kappas, 2.5)
        ci_high = np.percentile(boot_kappas, 97.5)

        print(f"Metric         : Fleiss' Kappa (κ)")
        print(f"Observed Agree : {po * 100:.2f}% (P_o = {po:.4f})")
        print(f"Chance Agree   : {pe * 100:.2f}% (P_e = {pe:.4f})")
        print(f"Fleiss' Kappa  : {kappa:.4f} [95% CI: {ci_low:.4f} - {ci_high:.4f}]")
        print(f"Interpretation : {interpret_kappa(kappa)} (Landis & Koch, 1977)")

    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inter-annotator agreement analysis.")
    parser.add_argument("--input", default=os.path.join(os.path.dirname(__file__), "..", "data", "annotations_multirater.csv"),
                        help="Path to CSV file with rater annotations.")
    parser.add_argument("--bootstrap", type=int, default=1000, help="Number of bootstrap iterations.")
    args = parser.parse_args()

    sys.exit(run_agreement_analysis(args.input, n_bootstrap=args.bootstrap))

