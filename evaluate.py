import os
import sys
import csv
import argparse
from collections import defaultdict
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LinearRegression

import model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VERIFICATION_CSV = os.path.join(BASE_DIR, "data", "verification_suite.csv")
DEFAULT_VERIFICATION_CSV = DEFAULT_VERIFICATION_CSV  # alias for backwards compatibility
FIELD_CSV = os.path.join(BASE_DIR, "data", "benchmark_field.csv")

ALL_DIAGNOSES = [
    "Rice_Root_Nematode",
    "Bacterial_Leaf_Blight",
    "False_Smut",
    "Rice_Blast",
    "Rice_Grassy_Stunt",
    "Rice_Tungro_Virus",
]

PEST_CLASSES = {
    "Rice_Root_Nematode",
}


def load_data(csv_path, split=None, tier=None):
    """
    Loads diagnostic benchmark dataset.
    Supports verification_suite.csv and benchmark_field.csv.
    Optional split parameter filters by dataset split (e.g. 'dev', 'eval', 'holdout', or ('dev', 'eval')).
    Optional tier parameter filters by evidence tier (e.g. 'A', 'B', 'C', or {'A', 'B'}).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    dataset = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return dataset

        header_lower = [h.strip().lower() for h in header]

        diag_idx = -1
        if "diagnosis" in header_lower:
            diag_idx = header_lower.index("diagnosis")
        else:
            diag_idx = 6  # standard position in legacy dataText.csv

        provenance_idx = header_lower.index("provenance") if "provenance" in header_lower else -1
        method_idx = header_lower.index("ground_truth_method") if "ground_truth_method" in header_lower else -1
        citation_idx = header_lower.index("citation") if "citation" in header_lower else -1
        case_id_idx = header_lower.index("case_id") if "case_id" in header_lower else -1

        raw_symptom_idx = header_lower.index("raw_symptom_text") if "raw_symptom_text" in header_lower else -1
        doi_idx = header_lower.index("doi") if "doi" in header_lower else -1
        split_idx = header_lower.index("split") if "split" in header_lower else -1
        tier_idx = header_lower.index("evidence_tier") if "evidence_tier" in header_lower else -1
        tier_note_idx = header_lower.index("tier_note") if "tier_note" in header_lower else -1
        url_idx = header_lower.index("source_url") if "source_url" in header_lower else -1
        archive_idx = header_lower.index("archive_url") if "archive_url" in header_lower else -1

        for row_idx, row in enumerate(reader, 2):
            if not row or not any(field.strip() for field in row):
                continue

            raw_target = row[diag_idx].strip() if len(row) > diag_idx else ""
            if not raw_target:
                # fallback for ragged rows
                fields = [c.strip() for c in row if c.strip()]
                raw_target = fields[-1].strip() if fields else ""

            if not raw_target:
                continue

            # Extract symptoms from columns prior to diagnosis or columns named symptom_*
            symptoms = []
            for col_i, col in enumerate(row[:diag_idx]):
                if header_lower and col_i < len(header_lower):
                    col_name = header_lower[col_i]
                    if col_name in ("case_id", "raw_symptom_text", "split"):
                        continue
                val = col.strip()
                if val and val != raw_target:
                    symptoms.append(val)

            # Handle negative test cases and out-of-scope controls
            if raw_target == "No_Diagnosis":
                targets = []
            elif raw_target == model.INSECT_OUT_OF_SCOPE_TARGET:
                targets = [model.INSECT_OUT_OF_SCOPE_TARGET]
            else:
                targets = [t.strip() for t in raw_target.split(" and ") if t.strip()]

            prov = row[provenance_idx].strip() if provenance_idx >= 0 and len(row) > provenance_idx else "rule_derived"
            citation = row[citation_idx].strip() if citation_idx >= 0 and len(row) > citation_idx else "Internal RiceKG SWRL Rule Base"
            case_id = row[case_id_idx].strip() if case_id_idx >= 0 and len(row) > case_id_idx else f"CASE_{len(dataset)+1:02d}"
            raw_symptom_text = row[raw_symptom_idx].strip() if raw_symptom_idx >= 0 and len(row) > raw_symptom_idx else ""
            doi = row[doi_idx].strip() if doi_idx >= 0 and len(row) > doi_idx else ""
            case_split = row[split_idx].strip() if split_idx >= 0 and len(row) > split_idx else "eval"
            evidence_tier = row[tier_idx].strip() if tier_idx >= 0 and len(row) > tier_idx else "A"
            tier_note = row[tier_note_idx].strip() if tier_note_idx >= 0 and len(row) > tier_note_idx else ""
            source_url = row[url_idx].strip() if url_idx >= 0 and len(row) > url_idx else ""
            archive_url = row[archive_idx].strip() if archive_idx >= 0 and len(row) > archive_idx else ""

            if split is not None:
                if isinstance(split, (list, tuple, set)):
                    if case_split not in split:
                        continue
                elif split != "all" and case_split != split:
                    continue

            if tier is not None:
                if isinstance(tier, (list, tuple, set)):
                    if evidence_tier not in tier:
                        continue
                elif tier != "all" and evidence_tier != tier:
                    continue

            dataset.append({
                "id": len(dataset) + 1,
                "case_id": case_id,
                "row_csv": row_idx,
                "raw_symptom_text": raw_symptom_text,
                "doi": doi,
                "split": case_split,
                "evidence_tier": evidence_tier,
                "tier_note": tier_note,
                "source_url": source_url,
                "archive_url": archive_url,
                "symptoms": symptoms,
                "expected": targets,
                "raw_target": raw_target,
                "provenance": prov,
                "citation": citation
            })
    return dataset


def run_evaluation(csv_path=None, dataset_name="verification", split=None, tier=None):
    if csv_path is None:
        if dataset_name == "field":
            csv_path = FIELD_CSV
            if split is None:
                split = ("dev", "eval")
        else:
            csv_path = DEFAULT_VERIFICATION_CSV

    print("=" * 80)
    print("PERFORMANCE EVALUATION: RICE PEST & DISEASE DIAGNOSTIC EXPERT SYSTEM (SWRL)")
    print("=" * 80)
    print(f"Dataset Name       : {dataset_name.upper()}")
    print(f"Dataset File       : {csv_path}")
    if split is not None:
        split_desc = ", ".join(split) if isinstance(split, (list, tuple, set)) else str(split)
        print(f"Split Filter       : {split_desc}")
    if tier is not None:
        tier_desc = ", ".join(tier) if isinstance(tier, (list, tuple, set)) else str(tier)
        print(f"Tier Filter        : {tier_desc}")

    dataset = load_data(csv_path, split=split, tier=tier)
    if not dataset:
        print(f"[STATUS] Dataset '{csv_path}' contains 0 test records.")
        return 0

    provenance_types = sorted(list(set(d.get("provenance", "unknown") for d in dataset)))
    print(f"Provenance Label   : {', '.join(provenance_types)}")
    print(f"Total Test Cases   : {len(dataset)} evaluated cases")
    print("-" * 80)

    per_class_matrix = {
        cls_name: {"TP": 0, "FP": 0, "FN": 0, "TN": 0} for cls_name in ALL_DIAGNOSES
    }

    detailed_results = []
    false_positives_log = []
    case_predictions = []

    tp_conf = fp_conf = 0
    tp_susp = fp_susp = 0

    for item in dataset:
        graded_preds = model.predict_diseases(item["symptoms"])
        predicted = [p["threat"] for p in graded_preds]
        pred_map = {p["threat"]: p for p in graded_preds}
        predicted_set = set(predicted)
        expected_set = set(item["expected"])

        is_exact_match = (predicted_set == expected_set)

        # Grade-aware precision tracking (in-sample counts)
        for p in graded_preds:
            t = p["threat"]
            g = p["grade"]
            if t in expected_set:
                if g == "confirmed":
                    tp_conf += 1
                else:
                    tp_susp += 1
            else:
                if g == "confirmed":
                    fp_conf += 1
                else:
                    fp_susp += 1

        for cls_name in ALL_DIAGNOSES:
            pred_has = cls_name in predicted_set
            exp_has = cls_name in expected_set

            if pred_has and exp_has:
                per_class_matrix[cls_name]["TP"] += 1
            elif pred_has and not exp_has:
                per_class_matrix[cls_name]["FP"] += 1
            elif not pred_has and exp_has:
                per_class_matrix[cls_name]["FN"] += 1
            else:
                per_class_matrix[cls_name]["TN"] += 1

        extra_preds = predicted_set - expected_set
        if extra_preds:
            false_positives_log.append({
                "case_id": item["case_id"],
                "symptoms": item["symptoms"],
                "expected": item["expected"],
                "predicted": predicted,
                "false_positive": list(extra_preds)
            })

        detailed_results.append({
            "id": item["id"],
            "case_id": item["case_id"],
            "symptoms": item["symptoms"],
            "expected": item["expected"],
            "predicted": predicted,
            "match": is_exact_match
        })

        case_predictions.append({
            "id": item["id"],
            "case_id": item["case_id"],
            "raw_target": item["raw_target"],
            "expected": expected_set,
            "pred_map": {p["threat"]: p["grade"] for p in graded_preds},
        })

    print("--- INFERENCE RESULTS SAMPLE (FIRST 10 CASES) ---")
    for res in detailed_results[:10]:
        status = "[MATCH]" if res["match"] else "[MISMATCH]"
        print(f"Case {res['case_id']} {status}")
        print(f"  Symptoms  : {', '.join(res['symptoms'])}")
        print(f"  Target    : {', '.join(res['expected']) if res['expected'] else '(No Diagnosis)'}")
        print(f"  Predicted : {', '.join(res['predicted']) if res['predicted'] else '(No diagnosis inferred)'}")
        print()

    print("=" * 80)
    print(f"{'DIAGNOSIS (CLASS)':<25} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'TN':<4} | {'Prec (%)':<8} | {'Rec (%)':<8} | {'F1 (%)':<8}")
    print("-" * 80)

    total_tp = total_fp = total_fn = total_tn = 0

    for cls_name in ALL_DIAGNOSES:
        m = per_class_matrix[cls_name]
        tp, fp, fn, tn = m["TP"], m["FP"], m["FN"], m["TN"]
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn

        prec = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
        rec = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        print(f"{cls_name:<25} | {tp:<4} | {fp:<4} | {fn:<4} | {tn:<4} | {prec:>8.1f} | {rec:>8.1f} | {f1:>8.1f}")

    print("-" * 80)
    micro_prec = (total_tp / (total_tp + total_fp) * 100) if (total_tp + total_fp) > 0 else 0.0
    micro_rec = (total_tp / (total_tp + total_fn) * 100) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = (2 * micro_prec * micro_rec / (micro_prec + micro_rec)) if (micro_prec + micro_rec) > 0 else 0.0
    accuracy_overall = ((total_tp + total_tn) / (total_tp + total_fp + total_fn + total_tn) * 100) if (total_tp + total_fp + total_fn + total_tn) > 0 else 0.0
    exact_match_acc = (sum(1 for r in detailed_results if r["match"]) / len(detailed_results) * 100) if detailed_results else 0.0

    print(f"{'TOTAL (MICRO AVG)':<25} | {total_tp:<4} | {total_fp:<4} | {total_fn:<4} | {total_tn:<4} | {micro_prec:>8.1f} | {micro_rec:>8.1f} | {micro_f1:>8.1f}")
    print(f"\nOverall Multi-Label Accuracy ((TP+TN)/Total): {accuracy_overall:.2f}%")
    print(f"Exact-Match Case Accuracy: {exact_match_acc:.2f}%")

    # =========================================================================
    # OUT-OF-SAMPLE STRATIFIED K-FOLD CALIBRATION & RELIABILITY DIAGRAM
    # =========================================================================
    print("\n" + "=" * 80)
    print("OUT-OF-SAMPLE STRATIFIED CALIBRATION & RELIABILITY ANALYSIS (TIER 1 vs TIER 2)")
    print("=" * 80)

    n_cases = len(case_predictions)
    k_splits = min(5, n_cases // 4) if n_cases >= 12 else 0

    if k_splits >= 2:
        # Form stratification labels
        strata_labels = []
        for c in case_predictions:
            exp = c["expected"]
            if not exp:
                strata_labels.append("negative")
            elif len(exp) > 1:
                strata_labels.append("composite")
            else:
                first_target = list(exp)[0]
                strata_labels.append("pest" if first_target in PEST_CLASSES else "disease")

        skf = StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=42)

        oos_y = []
        oos_p_flat = []
        oos_p_graded = []
        oos_grades = []

        for fold, (train_idx, test_idx) in enumerate(skf.split(case_predictions, strata_labels)):
            train_cases = [case_predictions[i] for i in train_idx]
            test_cases = [case_predictions[i] for i in test_idx]

            # Compute out-of-sample precision rates on training folds ONLY
            tr_conf_tp, tr_conf_fp = 0, 0
            tr_susp_tp, tr_susp_fp = 0, 0
            for tc in train_cases:
                exp = tc["expected"]
                for t, g in tc["pred_map"].items():
                    if t in exp:
                        if g == "confirmed":
                            tr_conf_tp += 1
                        else:
                            tr_susp_tp += 1
                    else:
                        if g == "confirmed":
                            tr_conf_fp += 1
                        else:
                            tr_susp_fp += 1

            p_conf_fold = (tr_conf_tp / (tr_conf_tp + tr_conf_fp)) if (tr_conf_tp + tr_conf_fp) > 0 else 1.0
            p_susp_fold = (tr_susp_tp / (tr_susp_tp + tr_susp_fp)) if (tr_susp_tp + tr_susp_fp) > 0 else 0.5

            # Score out-of-sample on held-out test fold
            for tc in test_cases:
                exp = tc["expected"]
                pred_map = tc["pred_map"]
                for cls_name in ALL_DIAGNOSES:
                    y_val = 1.0 if cls_name in exp else 0.0
                    p_fl = 1.0 if cls_name in pred_map else 0.0

                    if cls_name in pred_map:
                        g = pred_map[cls_name]
                        p_gr = p_conf_fold if g == "confirmed" else p_susp_fold
                        stratum_name = "confirmed" if g == "confirmed" else "suspected"
                    else:
                        p_gr = 0.0
                        stratum_name = "negative"

                    oos_y.append(y_val)
                    oos_p_flat.append(p_fl)
                    oos_p_graded.append(p_gr)
                    oos_grades.append(stratum_name)

        oos_y = np.array(oos_y)
        oos_p_flat = np.array(oos_p_flat)
        oos_p_graded = np.array(oos_p_graded)

        brier_flat_oos = float(np.mean((oos_p_flat - oos_y) ** 2))
        brier_graded_oos = float(np.mean((oos_p_graded - oos_y) ** 2))
        brier_diff_oos = brier_flat_oos - brier_graded_oos

        # Non-parametric bootstrap (1000 iterations) for confidence intervals
        rng = np.random.RandomState(42)
        boot_conf_prec = []
        boot_susp_prec = []
        boot_brier_diffs = []

        for _ in range(1000):
            b_idx = rng.choice(n_cases, size=n_cases, replace=True)
            b_cases = [case_predictions[i] for i in b_idx]
            b_c_tp = b_c_fp = b_s_tp = b_s_fp = 0
            for bc in b_cases:
                exp = bc["expected"]
                for t, g in bc["pred_map"].items():
                    if t in exp:
                        if g == "confirmed":
                            b_c_tp += 1
                        else:
                            b_s_tp += 1
                    else:
                        if g == "confirmed":
                            b_c_fp += 1
                        else:
                            b_s_fp += 1

            if (b_c_tp + b_c_fp) > 0:
                boot_conf_prec.append(b_c_tp / (b_c_tp + b_c_fp))
            if (b_s_tp + b_s_fp) > 0:
                boot_susp_prec.append(b_s_tp / (b_s_tp + b_s_fp))

        conf_ci_low = float(np.percentile(boot_conf_prec, 2.5)) if boot_conf_prec else 1.0
        conf_ci_high = float(np.percentile(boot_conf_prec, 97.5)) if boot_conf_prec else 1.0
        susp_ci_low = float(np.percentile(boot_susp_prec, 2.5)) if boot_susp_prec else 0.5
        susp_ci_high = float(np.percentile(boot_susp_prec, 97.5)) if boot_susp_prec else 1.0

        # Linear calibration regression on out-of-sample predictions: y = a + b * p
        calib_reg = LinearRegression().fit(oos_p_graded.reshape(-1, 1), oos_y)
        calib_slope = float(calib_reg.coef_[0])
        calib_intercept = float(calib_reg.intercept_)

        print("RELIABILITY DIAGRAM & CALIBRATION TABLE (OUT-OF-SAMPLE CROSS-VALIDATION):")
        print(f"{'DIAGNOSTIC STRATUM':<20} | {'COUNT (N)':<10} | {'MEAN PRED P':<14} | {'OBSERVED RATE':<14} | {'CALIB ERROR':<12}")
        print("-" * 80)

        for s_name in ["negative", "suspected", "confirmed"]:
            mask = [g == s_name for g in oos_grades]
            sub_preds = oos_p_graded[mask]
            sub_y = oos_y[mask]
            mean_p = float(np.mean(sub_preds)) if len(sub_preds) > 0 else 0.0
            obs_rate = float(np.mean(sub_y)) if len(sub_y) > 0 else 0.0
            cal_err = abs(mean_p - obs_rate)
            label = "Tier 1: Confirmed" if s_name == "confirmed" else ("Tier 2: Suspected" if s_name == "suspected" else "Negative Stratum")
            print(f"{label:<20} | {len(sub_preds):<10} | {mean_p:>14.4f} | {obs_rate:>14.4f} | {cal_err:>12.4f}")

        print("-" * 80)
        print("EMPIRICAL CONFIDENCE ESTIMATES (WITH BOOTSTRAP 95% CIs):")
        emp_prec_conf = (tp_conf / (tp_conf + fp_conf)) if (tp_conf + fp_conf) > 0 else 1.0
        emp_prec_susp = (tp_susp / (tp_susp + fp_susp)) if (tp_susp + fp_susp) > 0 else 0.0
        print(f"  - p(Confirmed | Tier-1 Fire) : {emp_prec_conf:.4f}  [95% Bootstrap CI: {conf_ci_low:.4f} - {conf_ci_high:.4f}]")
        print(f"  - p(Suspected | Tier-2 Fire) : {emp_prec_susp:.4f}  [95% Bootstrap CI: {susp_ci_low:.4f} - {susp_ci_high:.4f}]")

        print("\nCALIBRATION METRICS (OUT-OF-SAMPLE):")
        print(f"  - Calibration Slope          : {calib_slope:.4f} (Ideal: 1.0000)")
        print(f"  - Calibration Intercept      : {calib_intercept:.4f} (Ideal: 0.0000)")
        print(f"  - Out-of-Sample Brier (Flat) : {brier_flat_oos:.6f}")
        print(f"  - Out-of-Sample Brier (Grade): {brier_graded_oos:.6f}")
        pct_red = (brier_diff_oos / brier_flat_oos * 100) if brier_flat_oos > 0 else 0.0
        print(f"  - Out-of-Sample Brier Change : {brier_diff_oos:+.6f} ({pct_red:+.2f}%)")

        print("\nMETHODOLOGICAL ASSESSMENT:")
        if susp_ci_high >= 1.0 or abs(brier_diff_oos) < 0.0001:
            print("  > [LIMITATION CONFIRMED] The bootstrap 95% CI for p(suspected) covers 1.0000, and out-of-sample")
            print(f"    Brier reduction is negligible ({brier_diff_oos:.6f}, {pct_red:.2f}%). As documented in docs/LIMITATIONS.md,")
            print("    multi-tier stratification provides NO statistically significant probabilistic calibration improvement")
            print("    over flat binary reasoning. Its value is purely qualitative (pathognomonic specificity vs screening sensitivity).")
        else:
            print(f"  > Stratified calibration shows statistically distinct out-of-sample precision bands.")

    else:
        print(f"[NOTE] Dataset size (N={n_cases}) insufficient for 5-fold cross-validation. Reporting in-sample precision.")
        prec_conf = (tp_conf / (tp_conf + fp_conf) * 100) if (tp_conf + fp_conf) > 0 else 0.0
        prec_susp = (tp_susp / (tp_susp + fp_susp) * 100) if (tp_susp + fp_susp) > 0 else 0.0
        print(f"  - Precision@Confirmed : {prec_conf:.2f}% (TP={tp_conf}, FP={fp_conf})")
        print(f"  - Precision@Suspected : {prec_susp:.2f}% (TP={tp_susp}, FP={fp_susp})")

    if false_positives_log:
        print("\n" + "=" * 80)
        print("FALSE POSITIVE DIAGNOSTIC ANALYSIS")
        print("=" * 80)
        for fp_info in false_positives_log:
            print(f"Case {fp_info['case_id']}:")
            print(f"  Target Diagnoses  : {fp_info['expected']}")
            print(f"  System Predictions: {fp_info['predicted']}")
            print(f"  False Positive(s) : {fp_info['false_positive']}")
            print(f"  Input Symptoms    : {fp_info['symptoms']}")
            print("-" * 50)

    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RiceKG expert system with out-of-sample calibration.")
    parser.add_argument("--dataset", choices=["verification", "synthetic", "augmented", "field"], default="verification",
                        help="Dataset to evaluate: 'verification' (rule-derived deductive suite) or 'field' (independent literature cases). 'synthetic' and 'augmented' are deprecated aliases for 'verification'.")
    parser.add_argument("--csv-path", default=None, help="Explicit path to benchmark CSV file.")
    parser.add_argument("--split", choices=["dev", "eval", "holdout", "all"], default=None, help="Filter dataset by split (e.g. 'dev', 'eval', 'holdout', 'all').")
    parser.add_argument("--tier", choices=["A", "B", "C", "A+B", "all"], default=None, help="Filter dataset by evidence tier.")
    args = parser.parse_args()

    split_arg = args.split
    tier_arg = None
    if args.tier == "A+B":
        tier_arg = {"A", "B"}
    elif args.tier and args.tier != "all":
        tier_arg = {args.tier}

    sys.exit(run_evaluation(csv_path=args.csv_path, dataset_name=args.dataset, split=split_arg, tier=tier_arg))
