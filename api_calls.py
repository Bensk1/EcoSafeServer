import requests, json, dateutil.parser

MAX_BONUS = 10.0
MULTIPLIER = 1.25

def getTrafficBonus(speed, posLat, posLong):
    url = 'https://api.tomtom.com/lbs/services/flowSegmentData/3/absolute/10/json'
    params = dict(
            key = '2uwcvbh9cjt7cqfgqbw9e546',
            point = str(posLat) + ',' + str(posLong),
            unit = 'KMPH')

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)

    value = max(0, min(1, float(speed) * MULTIPLIER / float(data['flowSegmentData']['freeFlowSpeed'])))
    return value * MAX_BONUS

# getTrafficBonus(10, 40.7481665, -73.9949547)

def getAllryderCompare(posLatBegin, posLongBegin, posLatEnd, posLongEnd):
    url = 'http://hack.allryder.com/v1/routes'
    params = {
            'from': str(posLatBegin) + ',' + str(posLongBegin),
            'to': str(posLatEnd) + ',' + str(posLongEnd)
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
