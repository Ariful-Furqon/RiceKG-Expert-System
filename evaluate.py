"""
Evaluation Script for Rice Pest and Disease Diagnostic Expert System.
Calculates multi-label Confusion Matrix (TP, FP, FN, TN), Precision, Recall, F1-Score, and Accuracy.
"""

import os
import csv
from collections import defaultdict
import model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "dataText.csv")

ALL_DIAGNOSES = [
    "Grasshopper",
    "Rice_Root_Nematode",
    "Rice_Stem_Borer",
    "Rice_Bug",
    "Brown_Planthopper",
    "Bacterial_Leaf_Blight",
    "False_Smut",
    "Rice_Blast",
    "Rice_Grassy_Stunt",
    "Rice_Tungro_Virus",
]

def load_data(csv_path):
    dataset = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row_idx, row in enumerate(reader, 2):
            if not row or not any(field.strip() for field in row):
                continue
            fields = [c.strip() for c in row if c.strip()]
            if len(fields) < 2:
                continue

            raw_target = row[6].strip() if len(row) > 6 else ""
            if not raw_target and len(fields) >= 2:
                raw_target = fields[-1].strip()

            if not raw_target:
                continue

            symptoms = []
            for col in row[:6]:
                val = col.strip()
                if val and val != raw_target:
                    symptoms.append(val)

            targets = [t.strip() for t in raw_target.split(" and ") if t.strip()]

            dataset.append({
                "id": len(dataset) + 1,
                "row_csv": row_idx,
                "symptoms": symptoms,
                "expected": targets,
                "raw_target": raw_target
            })
    return dataset

def run_evaluation():
    print("=" * 80)
    print("PERFORMANCE EVALUATION: RICE PEST & DISEASE DIAGNOSTIC EXPERT SYSTEM (SWRL)")
    print("=" * 80)

    dataset = load_data(CSV_FILE)
    print(f"Total evaluated test instances: {len(dataset)} cases\n")

    per_class_matrix = {
        cls_name: {"TP": 0, "FP": 0, "FN": 0, "TN": 0} for cls_name in ALL_DIAGNOSES
    }

    detailed_results = []
    false_positives_log = []

    for item in dataset:
        predicted = model.predict_diseases(item["symptoms"])
        predicted_set = set(predicted)
        expected_set = set(item["expected"])

        is_exact_match = (predicted_set == expected_set)

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
                "case_id": item["id"],
                "symptoms": item["symptoms"],
                "expected": item["expected"],
                "predicted": predicted,
                "false_positive": list(extra_preds)
            })

        detailed_results.append({
            "id": item["id"],
            "symptoms": item["symptoms"],
            "expected": item["expected"],
            "predicted": predicted,
            "match": is_exact_match
        })

    print("--- DETAILED INFERENCE RESULTS PER TEST CASE ---")
    for res in detailed_results:
        status = "[MATCH]" if res["match"] else "[MISMATCH]"
        print(f"Case #{res['id']:02d} {status}")
        print(f"  Symptoms  : {', '.join(res['symptoms'])}")
        print(f"  Target    : {', '.join(res['expected'])}")
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

    if false_positives_log:
        print("\n" + "=" * 80)
        print("FALSE POSITIVE ANALYSIS (For Reviewer Comment #5)")
        print("=" * 80)
        for fp_info in false_positives_log:
            print(f"Case #{fp_info['case_id']}:")
            print(f"  Target Diagnoses  : {fp_info['expected']}")
            print(f"  System Predictions: {fp_info['predicted']}")
            print(f"  False Positive(s) : {fp_info['false_positive']}")
            print(f"  Input Symptoms    : {fp_info['symptoms']}")
            print("-" * 50)

if __name__ == "__main__":
    run_evaluation()
