import sys
import csv

for row in csv.reader(sys.stdin):
    if len(row) < 2:
        continue

    if row[0].strip().lower() == "title":
        continue

    company = row[1].strip()

    if company:
        print(f"{company}\t1")