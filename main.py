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
import datetime
import time
import serial
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from twitter import *
from twython import Twython

import user
import ride

app = Flask(__name__)

app.EVENT_ACCELERATION = False
app.EVENT_BRAKE = False
app.EVENT_IDLE = False
app.EVENT_DISTANCE = False
app.EVENT_TURN = False
app.EVENT_SPEEDING = False
app.EVENT_JAM = False
app.EVENT_SLOW = False
app.FUEL_USAGE = 0
app.FUEL_EFFICIENCY = 1

app.EVENT_PEBBLE_ACCELERATION = False
app.EVENT_PEBBLE_BRAKE = False
app.EVENT_PEBBLE_IDLE = False
app.EVENT_PEBBLE_DISTANCE = False
app.EVENT_PEBBLE_TURN = False
app.EVENT_PEBBLE_SPEEDING = False
app.EVENT_PEBBLE_JAM = False
app.EVENT_PEBBLE_SLOW = False

app.COUNTER_ACCELERATION = 0;
app.COUNTER_BRAKE = 0;
app.TIME_IDLE = 0;
app.COUNTER_DISTANCE = 0;
app.COUNTER_TURN = 0;
app.COUNTER_SPEEDING = 0;
app.TIME_JAM = 0;
app.TIME_SLOW = 0;

app.START_TIME_IDLE = None;
app.START_TIME_JAM = None;
app.START_TIME_SLOW = None;

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

app.pastRideScores = [0.54, 0.61, 0.71]
app.pastRideDurations = [20, 18, 38]

background_tomtom = None
background_thread_fuel = None

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

app.start = {
    'location': {
        'longitude': 0.0,
        'latitude': 0.0
    },
    'time': ""
}

app.end = {
    'location': {
        'longitude': 0.0,
        'latitude': 0.0
    },
    'time': ""
}

MARKGRAFENSTR = "52.505236, 13.394680"
FRANKFURTER_TOR = "52.515746, 13.454031"

@app.route("/tweet")
def tweetRide():
    try:
        #t = Twitter(auth=OAuth('3103869543-RNxiuTTiG72vgYVF7ZC62GU4Dr0nHQvNmwXASdF', '3PJZ3PX6haaGxDpRLOMSUW24f8UP8aIoIkxepE0B93Zdw', 'LIGCZFGC1olDPrBzax5bXFajX' ,'dDzlBjv77s7NNCaxjxEHSKYKaTZq9cGrL2biPKC1B6LQNDU17C'))
        twitter = Twython(
            'LIGCZFGC1olDPrBzax5bXFajX',
            'dDzlBjv77s7NNCaxjxEHSKYKaTZq9cGrL2biPKC1B6LQNDU17C',
            '3103869543-RNxiuTTiG72vgYVF7ZC62GU4Dr0nHQvNmwXASdF',
            '3PJZ3PX6haaGxDpRLOMSUW24f8UP8aIoIkxepE0B93Zdw')

        image_ids = twitter.upload_media(media=open(app.overAllGrade + ".png"))
        #twitter.update_status(status='hello this is an status',media_ids=image_ids['media_id'])

        val = "I just scored " + app.grade + " on #GREENtire! I'm a " + app.overAllGrade + " now!"
        twitter.update_status(status=val, media_ids=image_ids['media_id'])
    except Exception as excp:
        print("Twitter failed: " + str(excp))
    return "1"

def getLocation():
    NOVERO_JSON['sigid'] = NOVERO_SIGID_LOCATION
    r = requests.post(NOVERO_URL, json.dumps(NOVERO_JSON))
    return json.loads(r.text)

def background_fuel_usage():
    while True:
        NOVERO_JSON['sigid'] = NOVERO_SIGID_FUEL
        r = requests.post(NOVERO_URL, json.dumps(NOVERO_JSON))
        app.FUEL_USAGE = float(json.loads(r.text)[0]['values'][0]['liters'])
        if app.FUEL_USAGE <= 10:
            app.FUEL_EFFICIENCY = 0
        elif app.FUEL_USAGE <= 14:
            app.FUEL_EFFICIENCY = 1
        else:
            app.FUEL_EFFICIENCY = 2
        print("FUEL USAGE: " + str(app.FUEL_USAGE))
        time.sleep(10)

@app.teardown_appcontext
def closeConnection(exception):
    database.closeConnection(exception)

@app.route("/db/init")
def initDb():
    return database.initDb(app)


@app.route("/db/drop")
def dropDb():
    return database.dropDb()

@app.route("/fuel")
def getFuelStatus():
    return app.FUEL_EFFICIENCY

@app.route("/stats")
def stats():
    return json.dumps([app.COUNTER_ACCELERATION, app.COUNTER_BRAKE, app.TIME_IDLE, app.COUNTER_DISTANCE, app.COUNTER_TURN, app.COUNTER_SPEEDING, app.TIME_JAM, app.TIME_SLOW])

@app.route("/ride/start")
def startRide():
    # background_tomtom.start()
    if not FAKE_DATA:
        loc = getLocation()
        app.end['location']['latitude'] = loc[0]['values'][0]['latitude']
        app.start['location']['longitude'] = loc[0]['values'][0]['longitude']
    else:
        app.start['location']['latitude'] = 52.505236
        app.start['location']['longitude'] = 13.394680

    app.start['time'] = datetime.datetime.now() - datetime.timedelta(minutes=10)

    return json.dumps(app.start['location'])


@app.route("/ride/end")
def stopRide():
    # background_tomtom.stop();
    if not FAKE_DATA:
        loc = getLocation()
        app.end['location']['latitude'] = loc[0]['values'][0]['latitude']
        app.end['location']['longitude'] = loc[0]['values'][0]['longitude']
    else:
        app.end['location']['latitude'] = 52.515746
        app.end['location']['longitude'] = 13.454031

    app.end['time'] = datetime.datetime.now()

    allRyderCompare = api_calls.getAllryderCompare(app.start['location']['latitude'], app.start['location']['longitude'], app.end['location']['latitude'], app.end['location']['longitude'], datetime.datetime.strftime(app.start['time'], '%Y-%m-%dT%H:%M:%S+00:00'))

    app.grade = calculateScore()
    app.overAllGrade = calculateOverallScore()

    report = {
        'currentGrade': app.grade,
        'overallGrade': app.overAllGrade,
        'allRyderCompare': allRyderCompare,
        'fuelEfficiency': app.FUEL_EFFICIENCY
    }

    return json.dumps(report)
    # return NOVERO_JSONn.dumps([app.COUNTER_ACCELERATION, app.COUNTER_BRAKE, app.TIME_IDLE, app.COUNTER_DISTANCE, app.COUNTER_TURN, app.COUNTER_SPEEDING, app.TIME_JAM, app.TIME_SLOW])
    #return json.dumps(app.end['location'])

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

def background_update_proximity():
    print "PREPARE TO READ PROXIMITY"
    SERIAL_PORT = "/dev/cu.usbmodem1421"
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )
    ser.close()
    ser.open()
    line = ser.readline()
    print "WE ARE READY"
    while True:
        line = ser.readline()
        app.EVENT_DISTANCE = True
        app.EVENT_PEBBLE_DISTANCE = True


@app.route("/events")
def events():
    value = json.dumps([app.EVENT_ACCELERATION, app.EVENT_BRAKE, app.EVENT_IDLE, app.EVENT_DISTANCE, app.EVENT_TURN, app.EVENT_SPEEDING, app.EVENT_JAM, app.EVENT_SLOW])

    app.EVENT_ACCELERATION = False
    app.EVENT_BRAKE = False
    app.EVENT_IDLE = False
    app.EVENT_DISTANCE = False
    app.EVENT_TURN = False
    app.EVENT_SPEEDING = False

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
    app.COUNTER_ACCELERATION += 1
    return "1"

@app.route("/trigger/break")
def triggerBrake():
    """BEHAVE_ID = 12"""
    app.EVENT_BRAKE = True
    app.EVENT_PEBBLE_BRAKE = True
    app.COUNTER_BRAKE += 1
    return "1"

@app.route("/trigger/speeding")
def triggerSpeeding():
    app.EVENT_SPEEDING = True
    app.EVENT_PEBBLE_SPEEDING = True
    app.COUNTER_SPEEDING += 1
    return "1"

@app.route("/trigger/slow/<state>")
def triggerSlow(state):
    app.EVENT_SLOW = bool(int(state))
    app.EVENT_PEBBLE_SLOW = app.EVENT_SLOW

    if app.EVENT_SLOW:
        app.START_TIME_SLOW = datetime.datetime.now()
    else:
        app.TIME_SLOW += (datetime.datetime.now() - app.START_TIME_SLOW).seconds

    return "1"

@app.route("/trigger/jam/<state>")
def triggerJam(state):
    app.EVENT_JAM = bool(int(state))
    app.EVENT_PEBBLE_JAM = app.EVENT_JAM

    if app.EVENT_JAM:
        app.START_TIME_JAM = datetime.datetime.now()
    else:
        app.TIME_JAM += (datetime.datetime.now() - app.START_TIME_JAM).seconds

    return "1"

@app.route("/trigger/idle/<state>")
def triggerIdle(state):
    app.EVENT_IDLE = bool(int(state))
    app.EVENT_PEBBLE_IDLE = app.EVENT_IDLE

    if app.EVENT_IDLE:
        app.START_TIME_IDLE = datetime.datetime.now()
    else:
        app.TIME_IDLE += (datetime.datetime.now() - app.START_TIME_IDLE).seconds

    return "1"

@app.route("/trigger/turn")
def triggerTurn():
    """BEHAVE_ID = 12 / 13 (schnell um die Kurve fahren)"""
    app.EVENT_TURN = True
    #app.EVENT_ACCELERATION = True
    app.EVENT_PEBBLE_TURN = True
    #app.EVENT_PEBBLE_ACCELERATION = True
    app.COUNTER_TURN += 1
    #app.COUNTER_ACCELERATION += 1
    return "1"

@app.route("/user/")
def listUser():
    if request.headers['Content-Type'] == 'application/json':
        return user.listUser()
    else:
        abort(415)


def resetPebble():
    app.EVENT_PEBBLE_ACCELERATION = False
    app.EVENT_PEBBLE_BRAKE = False
    app.EVENT_PEBBLE_IDLE = False
    app.EVENT_PEBBLE_DISTANCE = False
    app.EVENT_PEBBLE_TURN = False
    app.EVENT_PEBBLE_SPEEDING = False

@app.route("/shouldVibrate")
def shouldVibrate():
    #hasNewEvent = True if random.randint(1, 5) == 5 else False
    value = json.dumps([app.EVENT_PEBBLE_ACCELERATION, app.EVENT_PEBBLE_BRAKE, app.EVENT_PEBBLE_IDLE, app.EVENT_PEBBLE_DISTANCE, app.EVENT_PEBBLE_TURN, app.EVENT_PEBBLE_SPEEDING, app.EVENT_PEBBLE_JAM, app.EVENT_PEBBLE_SLOW])

    resetPebble()
    return value

def calculateScore():
    mistakes =  app.COUNTER_ACCELERATION + app.COUNTER_BRAKE + app.TIME_IDLE + app.COUNTER_DISTANCE + app.COUNTER_TURN + app.COUNTER_SPEEDING + app.TIME_JAM + app.TIME_SLOW
    duration = time.mktime(app.end['time'].timetuple()) - time.mktime(app.start['time'].timetuple())
    duration = duration / 60
    score = (duration - mistakes * 5) / duration
    grade = ""
    if score == 1:
        grade = "Excellent"
    elif score < 1 and score >= 0.95:
        grade = "Very Good"
    elif score < 0.95 and score >= 0.9:
        grade = "Good"
    elif score < 0.9 and score >= 0.7:
        grade = "Okay"
    elif score < 0.7 and score >= 0.5:
        grade = "Satisfactory"
    elif score < 0.5 and score >= 0.25:
        grade = "Worst driver"
    else:
        grade = "Take the bus!"

    app.pastRideDurations.append(duration)
    app.pastRideScores.append(score)

    return grade

def calculateOverallScore():
    overAllScore = 0.0
    overAllTime = 0.0
    i = 0
    for pastRideDuration in app.pastRideDurations:
        overAllScore += pastRideDuration * app.pastRideScores[i]
        overAllTime += pastRideDuration
        i += 1

    overAllScore = overAllScore / overAllTime

    if overAllScore <= 1 and overAllScore >= 0.9:
        overAllGrade = "Driving School Teacher"
    elif overAllScore < 0.9 and overAllScore >= 0.7:
        overAllGrade = "Experienced Driver"
    elif overAllScore < 0.7 and overAllScore >= 0.5:
        overAllGrade = "Amateur"
    elif overAllScore < 0.5 and overAllScore >= 0.25:
        overAllGrade = "Blind granny"
    else:
        overAllGrade = "Rowdy"

    return overAllGrade


if __name__ == "__main__":
    background_tomtom = Thread(target = background_update_tomtom)
    background_tomtom.setDaemon(True)
    background_thread_fuel = Thread(target = background_fuel_usage)
    background_thread_fuel.setDaemon(True)
    background_thread_fuel.start()
    app.debug = True
    background_proximity = Thread(target = background_update_proximity)
    background_proximity.setDaemon(True)
    background_proximity.start();

    app.debug = False
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
