#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import subprocess
import json

CURL_REQ = ["curl", "--get", "https://api.twitter.com/1.1/statuses/user_timeline.json", "--data", 'count=3000&exclude_replies=true&screen_name=STIBMIVB', "--header", 'Authorization: OAuth oauth_consumer_key="j6WmMlniNZXzsDMianvepnOiE", oauth_nonce="63dbb02a73946dc70e85f5c94be983bc", oauth_signature="MldIEgFpDdiZEahWU5h8fJpw7TM%3D", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1457799421", oauth_version="1.0"']


def isIn(l1,l2):
    for e in l1:
        if e in l2:
            return True 
    return False

def getStibJson():
    process = subprocess.Popen(CURL_REQ, stdout=subprocess.PIPE)
    out, err = process.communicate()
    jon = json.loads(out)
    return jon

def findLine(text):
    spl = text.split()
    lsol = []
    for e in spl:
        if e.startswith("#stibT"):
            e = e.replace("#stibT","")
            lsol.append(int(e))
    return lsol


def findStop(text):
    if "#stib" in text:
        spl = text.split()
        ssol = []
        for i,e in enumerate(spl):
            if not "#stib" in e and not e.startswith("#stibT") and e.startswith("#"):
                if not (i>0 and spl[i-1].lower()=="direction"):
                    ssol.append(e[1:])
        return ssol



def getEvents():
    jon = getStibJson()
    events = []
    # start update end
    for tweet in jon[::-1]:
        text = tweet["text"].encode("utf-8")
        if isIn(["#stibT","#stibM"], text):
            if isIn(["Pas de circulation", "Collision", "Accident"], text):
                line = findLine(text) 
                time = tweet["created_at"]
                stops = findStop(text) 
                events.append({"type": "began", "lines":line, "stops":stops, "timestamp":time})

            elif isIn(["rétablie","#stibM"], text):
                line = findLine(text)
                time = tweet["created_at"]
                stops = findStop(text) 
                events.append({"type": "ended", "lines":line, "stops":stops, "timestamp":time})

    return json.dumps(events)



def main():
    print(getEvents())


if __name__ == '__main__':
    main()