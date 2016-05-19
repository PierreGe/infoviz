import requests
from tqdm import tqdm
from time import sleep
from HTMLParser import HTMLParser


class STIBLineParser(HTMLParser):
    """
    Parse a STIB Line from the mobile API
    """
    URL = 'http://m.stib.be/api/getitinerary.php?line={line}&iti={direction}'

    def __init__(self):
        HTMLParser.__init__(self)
        self.stops = []
        self.in_stop = False

    def handle_starttag(self, tag, attrs):
        self.record = (tag == 'id')

    def handle_data(self, data):
        if self.record:
            self.stops.append(data.strip())

    @classmethod
    def get(cls, line, direction, retry=5):
        """
        Get stops for a STIB line
        """
        url = cls.URL.format(line=line, direction=direction)
        r = requests.get(url)
        while r.status_code != 200 and retry > 0:
            r = requests.get(url)
            retry -= 1
            sleep(1)
        assert r.status_code == 200
        parser = cls()
        parser.feed(r.content)
        return parser.stops


def get_stops_data():
    """
    Grab stops database from Brussels Open Data portal
    """
    url = "http://opendata.bruxelles.be/explore/dataset/stib-stops/download/?format=json&timezone=Europe/Brussels&use_labels_for_header=true"
    stops_by_id = {
        x['fields']['id']: {
            'latitude': float(x['fields']['latitude']),
            'longitude': float(x['fields']['longitude']),
            'name': x['fields']['name'].capitalize(),
            'id': x['fields']['id'],
        } for x in requests.get(url).json()
    }

    duplicates, suffixed = {}, {}
    for i in stops_by_id.keys():
        stop_id = i[:4]
        if stop_id not in duplicates:
            if stop_id in stops_by_id:
                siblings = filter(lambda x: x.startswith(stop_id) and len(x) > 4, stops_by_id.keys())
                if siblings:
                    name = None
                    for s in [stops_by_id[x] for x in siblings]:
                        assert name is None or name == s['name']
                        name = s['name']
                    duplicates[stop_id] = siblings
            else:
                suffixed[stop_id] = i

    cleaned = {k: v for k, v in stops_by_id.iteritems()}
    for stop_id, dup in duplicates.iteritems():
        map(cleaned.pop, dup)

    for stop_id, k in suffixed.iteritems():
        cleaned[stop_id] = cleaned[k]
        cleaned.pop(k)

    return cleaned


def get_all_lines_stops():
    def get_line(line):
        d1 = STIBLineParser.get(line, 1)
        d2 = STIBLineParser.get(line, 2)
        d1.append(d2[0])
        d2.append(d1[0])
        return {
            1: d1,
            2: d2,
            'from': d1[0],
            'to': d2[0],
            'lineNo': line,
        }
    return [get_line(l) for l in tqdm(STIB_LINES, "Retrieving lines")]

if __name__ == "__main__":
    from extract_trajects_time import STIB_LINES
    import json

    stops = get_stops_data()
    lines = get_all_lines_stops()

    with open('stib-lines.json', 'w') as out:
        json.dump(lines, out)

    with open('stib-stops.json', 'w') as out:
        json.dump(stops, out)

    with open('app/src/data.js', 'w') as out:
        print >>out, "export const STIB_LINES = {}".format(json.dumps(lines))
        print >>out, "export const STIB_STOPS = {}".format(json.dumps(stops))
