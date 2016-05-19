"""
Tool to convert dumps of the trajects table from C4ptainCrunch's database,
and insert them as legs in our database (in a separate table for atomic
updates of the application API database).
"""

import json
import re
import psycopg2 as pg
from sys import stdout

body_regexp = re.compile(r"COPY traject \(.+\) FROM stdin;\n")
regexp = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+\{([^}]+)\}\s+(.+)\n")
stib_lines = {x['lineNo']: x for x in json.load(open("stib-lines.json"))}

conn = pg.connect(database='delay')
cursor = conn.cursor()


def SIformat(n, decimals=3):
    prefix_higher = ['', 'k', 'M', 'G', 'T', 'P']
    for p in prefix_higher:
        if n < 1000:
            n = round(n, decimals)
            return '{} {}'.format(n, p)
        n /= 1000.


def insert_legs(rows):
    cursor.executemany("""
    INSERT INTO legs_wip (line, departure, arrival, from_stop_id, to_stop_id)
    VALUES (%(line)s, %(departure)s, %(arrival)s, %(from_stop_id)s, %(to_stop_id)s)
    """, rows)
    return len(rows)


def extract_traject(id, line, way, stops, departure):
    line_stops = stib_lines.get(int(line), {}).get(way, None)[1:]
    if not line_stops:
        return
    stop_times = filter(lambda x: x != '"', stops).split(',')

    legs = zip(line_stops[:-1], line_stops[1:])
    times = zip(stop_times[:-1], stop_times[1:])

    rows = []
    for leg, time in zip(legs, times):
        if 'NULL' in time:
            continue
        rows.append({
            'line': line,
            'from_stop_id': leg[0],
            'to_stop_id': leg[1],
            'departure': time[0],
            'arrival': time[1],
        })
    return insert_legs(rows)


def main(in_file):
    in_body = False
    inserted = 0
    current_k = None

    for line in in_file:
        if not in_body:
            if body_regexp.match(line):
                in_body = True
        else:
            m = regexp.match(line)
            if m:
                inserted += extract_traject(*m.groups())
                k = (m.group(2), m.group(3))
                if k != current_k:
                    stdout.write("\rInserted %s rows [%s]" % (
                        SIformat(inserted, 1), k))
                    current_k = k
                    conn.commit()
    conn.commit()

if __name__ == "__main__":
    from sys import argv, stdin
    main(open(argv[1]) if len(argv) > 1 else stdin)
