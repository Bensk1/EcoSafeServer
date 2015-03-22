import sys
import time
from math import radians, cos, sin, asin, sqrt
import json

sys.path.append(".env/lib/python2.7/site-packages")

import requests

def dist(longA, latA, longB, latB):
    longA, latA, longB, latB = map(radians, [longA, latA, longB, latB])

    dlon = longB - longA 
    dlat = latB - latA 
    a = sin(dlat/2)**2 + cos(latA) * cos(latB) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    radius = 6371
    return c * radius

NOVERO_URL = 'http://212.23.138.201:8080/mako-ws/public/query'
NOVERO_SIGID_LOCATION = 4608
NOVERO_SIGID_SPEED = 4352
NOVERO_JSON = {
    'sigid': -1,
    'type': 'lastValue',
    'restrict': {
        'type': '=',
        'field': 'carid',
        'value': 214
    }
}

def getLocation():
    NOVERO_JSON['sigid'] = NOVERO_SIGID_LOCATION
    r = requests.post(NOVERO_URL, json.dumps(NOVERO_JSON))
    return json.loads(r.text)

def getSpeed():
    NOVERO_JSON['sigid'] = NOVERO_SIGID_SPEED
    r = requests.post(NOVERO_URL, json.dumps(NOVERO_JSON))
    return json.loads(r.text)[0]['values'][0]['value']

loc = getLocation()
newLatitude = loc[0]['values'][0]['latitude']
newLongitude = loc[0]['values'][0]['longitude']

overallMeters = 0.0

while True:
    oldLatitude = newLatitude
    oldLongitude = newLongitude
    loc = getLocation()
    newLatitude = loc[0]['values'][0]['latitude']
    newLongitude = loc[0]['values'][0]['longitude']
    overallMeters += dist(oldLongitude, oldLatitude, newLongitude, newLatitude) * 1000
    print overallMeters
    time.sleep(1)