import csv

insects = {"Grasshopper", "Rice_Stem_Borer", "Rice_Bug", "Brown_Planthopper"}
with open("data/verification_suite.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

insect_cases = []
for idx, r in enumerate(rows, 1):
    diag = r["diagnosis"]
    targets = [t.strip() for t in diag.split(" and ")]
    has_insect = any(t in insects for t in targets)
    if has_insect:
        symptoms = [r[f"symptom_{i}"] for i in range(1, 7) if r.get(f"symptom_{i}")]
        insect_cases.append((idx, diag, targets, symptoms, r))

print(f"Total insect cases found: {len(insect_cases)}")
for idx, diag, targets, symptoms, r in insect_cases:
    print(f"Row {idx:02d}: diag='{diag}' | symptoms={symptoms}")

