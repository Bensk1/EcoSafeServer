import sys
sys.path.append(".env/lib/python2.7/site-packages")

import requests, json, dateutil.parser

def getTrafficEvents(posLat, posLong):
    url = 'https://api.tomtom.com/lbs/services/flowSegmentData/3/absolute/10/json'
    params = dict(
            key = '2uwcvbh9cjt7cqfgqbw9e546',
            point = str(posLat) + ',' + str(posLong),
            unit = 'KMPH')

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    print data
    isSlow = float(data['flowSegmentData']['currentSpeed']) < 0.5 * float(data['flowSegmentData']['freeFlowSpeed'])
    isJammed = float(data['flowSegmentData']['currentSpeed']) < 0.1 * float(data['flowSegmentData']['freeFlowSpeed'])

    return [isSlow, isJammed]

# getTrafficBonus(10, 40.7481665, -73.9949547)

def getAllryderCompare(posLatBegin, posLongBegin, posLatEnd, posLongEnd, timeBegin):
    url = 'http://hack.allryder.com/v1/routes'
    params = {
            'from': str(posLatBegin) + ',' + str(posLongBegin),
            'to': str(posLatEnd) + ',' + str(posLongEnd),
            'at': timeBegin,
            'by': 'departure'
            }

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    routes = data['routes']

    alternatives = []

    for route in routes:
        route_data = []
        time_start = route['segments'][0]['stops'][0]['datetime']
        time_end = route['segments'][-1]['stops'][-1]['datetime']
        duration = (dateutil.parser.parse(time_end) - dateutil.parser.parse(time_start)).total_seconds()

        alternatives += [[route['type'], route['provider'], duration, route['price']['amount']]]

    return alternatives

# getAllryderCompare(52.529990,13.403770,52.481261,13.435235)
