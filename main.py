import sys
sys.path.append(".env/lib/python2.7/site-packages")

from flask import Flask
import requests
import json
import random

import user

app = Flask(__name__)

FAKE_DATA = True

HARD_BRAKING = 10
HARD_ACCELERATION = 11

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
    if request.method == 'GET':
        return user.getUser(username)
    elif request.method == 'POST':
        return user.createUser(username)
    elif request.method == 'DELETE':
        return user.deleteUser(username)


if __name__ == "__main__":
    app.debug = True
    app.run()
