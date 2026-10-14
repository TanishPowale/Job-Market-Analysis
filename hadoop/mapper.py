import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if len(row) < 5:
        continue

    title = row[0].strip().strip('"').strip().lstrip("#").strip()   
    if title.lower() == "title" or not title:
        continue

    print(f"{title}\t1")
