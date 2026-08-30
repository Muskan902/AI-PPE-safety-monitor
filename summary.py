import csv
from collections import defaultdict

log_file = "violation_log.csv"

violations = defaultdict(lambda: defaultdict(int))

with open(log_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        worker = row["Worker"]
        missing_items = row["Missing PPE"].split(", ")

        for item in missing_items:
            violations[worker][item] += 1


print("\n================================")
print("       PPE SAFETY SUMMARY")
print("================================")

for worker, items in violations.items():

    print(f"\n{worker}")

    total = 0

    for ppe, count in items.items():
        print(f"  {ppe}: {count}")
        total += count

    print(f"  Total violations: {total}")

print("\n================================")