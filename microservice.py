from urllib2 import urlopen, URLError
import os
import time
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def getCurrentData():
    location = queryGoogleGeocode(request.args.get('location'))
    if (location.startswith('error')):
        return location
    date = str(request.args.get('date'))
    if (date):
        hour = time.gmtime().tm_hour
        minu = time.gmtime().tm_min
        sec = time.gmtime().tm_sec
        if (hour < 10):
            h = '0' + str(hour)
        else: 
            h = str(hour)
        if (minu < 10):
            m = '0' + str(minu)
        else: 
            m = str(minu)
        if (sec < 10):
            s = '0' + str(sec)
        else: 
            s = str(sec)
        date = date + 'T' + h + ':' + m + ':' + s +'Z'
        jsonResponse = queryDarkSkyTimeMachine(location, date)
    else:
        jsonResponse = queryDarkSkyForecast(location)
    data = json.loads(jsonResponse)
    return data['currently']['summary']

def queryDarkSkyForecast(latLongString):
    request = 'https://api.darksky.net/forecast/4a21043802f4364273e7fe25ba29c92b/'+latLongString
    try:
	    response = urlopen(request)
	    return response.read()
    except:
        return 'error'

def queryDarkSkyTimeMachine(latLongString, time):
    request = 'https://api.darksky.net/forecast/4a21043802f4364273e7fe25ba29c92b/'+latLongString+','+time
    print(request)
    try:
	    response = urlopen(request)
	    return response.read()
    except:
        return 'error'

def queryGoogleGeocode(address):
    print(address)
    request = 'https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyBV5UxMqteJE2foIpiTA9AMlvObe67ZUso'
    try:
	    response = urlopen(request)
	    data = json.loads(response.read())
    except:
        return 'error: url wont open'
    try:
        latlong = str(data['results'][0]['geometry']['location']['lat'])+','+str(data['results'][0]['geometry']['location']['lng'])
        return latlong
    except: 
        return 'error: location does not exist'

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
