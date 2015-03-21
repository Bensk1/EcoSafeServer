import sys
sys.path.append(".env/lib/python2.7/site-packages")

from flask import Flask, request, json, abort, g
import requests
import random
import json
import sqlite3
import database
import api_calls
from threading import Thread
import time
import api_calls

import user
import ride

app = Flask(__name__)

app.EVENT_ACCELERATION = False
app.EVENT_BREAK = False
app.EVENT_IDLE = False
app.EVENT_DISTANCE = False
app.EVENT_TURN = False
app.EVENT_SPEEDING = False
app.EVENT_JAM = False
app.EVENT_SLOW = False

app.EVENT_PEBBLE_ACCELERATION = False
app.EVENT_PEBBLE_BREAK = False
app.EVENT_PEBBLE_IDLE = False
app.EVENT_PEBBLE_DISTANCE = False
app.EVENT_PEBBLE_TURN = False
app.EVENT_PEBBLE_SPEEDING = False
app.EVENT_PEBBLE_JAM = False
app.EVENT_PEBBLE_SLOW = False

CURRENT_LAT = 40.7481665
CURRENT_LONG = -73.9949547

FAKE_DATA = True

HARD_BRAKING = 10
HARD_ACCELERATION = 11

NOVERO_URL = 'http://212.23.138.201:8080/mako-ws/public/query'
NOVERO_SIGID_LOCATION = 4608
NOVERO_SIGID_FUEL = 8704
NOVERO_JSON = {
    'sigid': -1,
    'type': 'lastValue',
    'restrict': {
        'type': '=',
        'field': 'carid',
        'value': 214
    }
}

background_tomtom = None

payload = {
    'access_token': '08beec989bccb333439ee3588583f19f02dd6b7e',
    'asset': '357322040163096',
    'filter': 'BEHAVE_ID'
}

behaviourEvent = {
    u'engine': [],
    u'loc': {
        u'latitude': 48.18035,
        u'longitude': 11.58489
    },
    u'car': [],
    u'pid': [],
    u'journey': [],
    u'meta': {
        u'asset': u'357322040163096'
    },
    u'behave': {
        u'BEHAVE_ID': -1
    },
    u'time': {
        u'recorded_at': u'2015-03-20T19:04:29Z'
    },
    u'gps': []
}

startLocation = {
    'longitude': 0.0,
    'latitude': 0.0
}

endLocation = {
    'longitude': 0.0,
    'latitude': 0.0
}


def getLocation():
    NOVERO_JSON['sigid'] = NOVERO_SIGID_LOCATION
    r = requests.post(NOVERO_URL, json.dumps(NOVERO_JSON))
    return json.loads(r.text)


@app.teardown_appcontext
def closeConnection(exception):
    database.closeConnection(exception)

@app.route("/db/init")
def initDb():
    return database.initDb(app)


@app.route("/db/drop")
def dropDb():
    return database.dropDb()

@app.route("/ride/start")
def startRide():
    background_tomtom.start()
    loc = getLocation()
    startLocation['longitude'] = loc[0]['values'][0]['longitude']
    startLocation['latitude'] = loc[0]['values'][0]['latitude']
    return json.dumps(startLocation)


@app.route("/ride/end")
def stopRide():
    background_tomtom.stop();
    loc = getLocation()
    endLocation['longitude'] = loc[0]['values'][0]['longitude']
    endLocation['latitude'] = loc[0]['values'][0]['latitude']
    return json.dumps(endLocation)

def background_update_tomtom():
    while True:
        time.sleep(15)
        print("Querying TomTom...")
        try:
            if not FAKE_DATA:
                res = api_calls.getTrafficEvents(CURRENT_LAT, CURRENT_LONG)
                app.EVENT_JAM = res[1]
                app.EVENT_SLOW = res[0]
        except Exception as inst:
            print("Error in TomTom update: " + str(inst))

@app.route("/events")
def events():
    value = json.dumps([app.EVENT_ACCELERATION, app.EVENT_BREAK, app.EVENT_IDLE, app.EVENT_DISTANCE, app.EVENT_TURN, app.EVENT_SPEEDING, app.EVENT_JAM, app.EVENT_SLOW])

    app.EVENT_BREAK = False
    app.EVENT_ACCELERATION = False
    app.EVENT_TURN = False

    return value

@app.route("/")
def hello():
    # print payload['filter']
    # r = requests.post('http://api.mycarcloud.de/resource.php', data=payload)
    # print json.loads(r.text)[0]
    return "hello"

@app.route("/getBehaviourEvent/current")
def getCurrentBehaviourEvent():
    if FAKE_DATA:
        hasNewEvent = True if random.randint(1, 5) == 5 else False

        if hasNewEvent:
            eventType = random.randint(HARD_BRAKING, HARD_ACCELERATION)
            behaviourEvent['behave']['BEHAVE_ID'] = eventType
            return json.dumps(behaviourEvent)
        else:
            return json.dumps({})


@app.route("/user/<username>", methods=['GET', 'POST', 'DELETE'])
def routeUser(username):
    if request.headers['Content-Type'] == 'application/json':
        if request.method == 'GET':
            return user.getUser(username)
        elif request.method == 'POST':
            return user.createUser(username, request.json)
        elif request.method == 'DELETE':
            return user.deleteUser(username)
    else:
        abort(415)

@app.route("/trigger/accelerate")
def triggerAcclerate():
    """BEHAVE_ID = 11"""
    app.EVENT_ACCELERATION = True
    app.EVENT_PEBBLE_ACCELERATION = True
    return "1"

@app.route("/trigger/break")
def triggerBrake():
    """BEHAVE_ID = 12"""
    app.EVENT_BRAKE = True
    app.EVENT_PEBBLE_BREAK = True
    return "1"

@app.route("/trigger/slow/<state>")
def triggerSlow(state):
    app.EVENT_SLOW = bool(int(state))
    app.EVENT_PEBBLE_SLOW = app.EVENT_SLOW
    return "1"

@app.route("/trigger/jam/<state>")
def triggerJam():
    app.EVENT_JAM = bool(int(state))
    app.EVENT_PEBBLE_JAM = app.EVENT_JAM
    return "1"

@app.route("/trigger/turn")
def triggerTurn():
    """BEHAVE_ID = 12 / 13 (schnell um die Kurve fahren)"""
    app.EVENT_TURN = True
    app.EVENT_ACCELERATION = True
    app.EVENT_PEBBLE_TURN = True
    app.EVENT_PEBBLE_ACCELERATION = True
    return "1"

@app.route("/user/")
def listUser():
    if request.headers['Content-Type'] == 'application/json':
        return user.listUser()
    else:
        abort(415)


def resetPebble():
    app.EVENT_PEBBLE_BREAK = False
    app.EVENT_PEBBLE_ACCELERATION = False
    app.EVENT_PEBBLE_TURN = False

@app.route("/shouldVibrate")
def shouldVibrate():
    #hasNewEvent = True if random.randint(1, 5) == 5 else False
    value = json.dumps([app.EVENT_PEBBLE_ACCELERATION, app.EVENT_PEBBLE_BREAK, app.EVENT_PEBBLE_IDLE, app.EVENT_PEBBLE_DISTANCE, app.EVENT_PEBBLE_TURN, app.EVENT_PEBBLE_SPEEDING, app.EVENT_PEBBLE_JAM, app.EVENT_PEBBLE_SLOW])

    resetPebble()
    return value

if __name__ == "__main__":
    background_tomtom = Thread(target = background_update_tomtom)
    background_tomtom.setDaemon(True)
    app.debug = True
    app.run(host="0.0.0.0")
