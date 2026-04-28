import sys
import csv
import re
from itertools import batched

def parse_duration(duration_str):
    total_seconds = 0
    parts = re.findall(r'(\d+)([hms])', duration_str)
    for value, unit in parts:
        if unit == 'h': total_seconds += int(value) * 3600
        elif unit == 'm': total_seconds += int(value) * 60
        elif unit == 's': total_seconds += int(value)
    return total_seconds

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_old_data.py <filename.txt>")
        return

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    # Standard cleanup for your manual copy-pastes
    if len(lines) > 3:
        lines.pop() 
        del lines[:2] 

    processed_data = []
    for batch in batched(lines, 7):
        if len(batch) < 7: continue
        row = list(batch)
        row[2] = parse_duration(row[2])
        processed_data.append(row)

    with open('NextivaCallData.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(processed_data)
    
    print(f"Imported {len(processed_data)} records from {filename}.")

if __name__ == "__main__":
    main()