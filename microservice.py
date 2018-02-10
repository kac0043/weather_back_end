from urllib2 import Request, urlopen, URLError
import os
import time
import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/?location=<address>&submit=submit')
def getCurrentData(address):
    location = queryGoogleGeocode(address)
    if (location.startswith('error')):
        return location
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

def queryGoogleGeocode(address):
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
