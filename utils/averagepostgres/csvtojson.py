import csv
import json

CSV_FILE = "sample.csv"

jsonl = []

with open(CSV_FILE, 'rb') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    firstLine = True
    temp = {}
    for col in lines:
        if firstLine:
            firstLine = False
            continue
        subtemp = {}
        subtemp[col[1]] = {'count' : col[2] , 'per_hour' : col[3], 'avg_time' : col[4], 'max_time' : col[5], 'min_time' : col[6], 'lines' : col[7]}
        if not col[0] in temp:
            temp[col[0]] = [subtemp]
        else:
            temp[col[0]].append(subtemp)
    jsonl.append(temp)
    with open('average-color.json', 'w') as outfile:
        json.dump(jsonl, outfile)