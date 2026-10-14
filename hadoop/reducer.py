
import sys

current_title = None
count = 0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    try:
        title, value = line.rsplit("\t", 1)
        value = int(value)
    except ValueError:
        continue

    if title == current_title:
        count += value
    else:
        if current_title is not None:
            print(f"{current_title}\t{count}")

        current_title = title
        count = value

if current_title is not None:
    print(f"{current_title}\t{count}")
