import sys
import csv
from itertools import batched

# fieldnames = ['Name', 'Time of Call', 'Duration', 'Direction', 'Answered', 'From', 'To']

def get_file_text(filepath):
    with open(filepath) as f:
        file_contents = f.read()
    return file_contents

def list_groups(long_list, size): # https://realpython.com/how-to-split-a-python-list-into-chunks/
    tuple_list = []
    list_list = []
    for batch in batched(long_list, size):
        tuple_list.append(batch)
    for item in tuple_list:
        list_item = list(item)
        duration = 0
        #duration is a string with m and s        
        if "m" in list_item[2]:
            minutes = list_item[2].split("m")
            seconds = minutes[1].split("s")
            duration = int(minutes[0])*60 + int(seconds[0])
        else:
            seconds = list_item[2].split("s")
            duration = int(seconds[0])
        list_item[2] = duration
        list_list.append(list_item)
    return list_list


def append_to_csv(daily_calls_list):
    with open('NextivaCallData.csv', mode='a', newline='') as f:
        writer = csv.writer(f)
        for row in daily_calls_list:
            writer.writerow(row)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 readfile2.py <path_to_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    file_string = get_file_text(file_path)
    lines_list = file_string.splitlines()
    lines_list.pop()
    print(f"Line 1: '{lines_list[0]}' deleted")
    print(f"Line 2: '{lines_list[1]}' deleted")
    del lines_list[:2] # remove first two items and last item (print them)
    calls_list = list_groups(lines_list, 7)
    print(calls_list[:3])
    append_to_csv(calls_list)
    #append these entries to a running list of entries that I will have made.

main()