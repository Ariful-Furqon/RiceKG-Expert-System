import csv

cases_to_remove = {
    # 7 disease-insect co-infections
    "Rice_Blast and Rice_Stem_Borer",
    "Brown_Planthopper and False_Smut",
    "False_Smut and Rice_Stem_Borer",
    "Grasshopper and Rice_Blast",
    "Brown_Planthopper and Rice_Tungro_Virus",
    "Bacterial_Leaf_Blight and Rice_Stem_Borer",
    "Rice_Root_Nematode and Rice_Stem_Borer",
}

insect_singles_and_pairs = {
    "Grasshopper",
    "Rice_Stem_Borer",
    "Rice_Bug",
    "Brown_Planthopper",
    "Grasshopper and Rice_Stem_Borer",
    "Grasshopper and Rice_Bug",
}

with open("data/verification_suite.csv", "r", encoding="utf-8") as f:
    reader = list(csv.reader(f))

header = reader[0]
rows = reader[1:]

diag_idx = header.index("diagnosis")

new_rows = []
removed_count = 0
converted_count = 0

for r in rows:
    if not r or not any(x.strip() for x in r):
        continue
    diag = r[diag_idx].strip()
    if diag in cases_to_remove:
        removed_count += 1
        continue
    elif diag in insect_singles_and_pairs:
        r[diag_idx] = "insect damage, out of scope"
        converted_count += 1
        new_rows.append(r)
    else:
        new_rows.append(r)

print(f"Original rows: {len(rows)}")
print(f"Removed: {removed_count}")
print(f"Converted to out of scope: {converted_count}")
print(f"New total rows: {len(new_rows)}")

with open("data/verification_suite.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(new_rows)

print("Updated data/verification_suite.csv successfully.")

