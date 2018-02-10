from urllib2 import urlopen, URLError
import os
import time
import json
from flask import Flask, jsonify, request, render_template
from cloudant import Cloudant
import cf_deployment_tracker

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET', 'POST'])
def getCurrentData():
    if (request.json is None):
        return 'error: No Address Given'
        
    location = getLocation(request.json) 
    if (location.startswith('error')):
        return location

    date = getDate(request.json)
    if (date):
        jsonResponse = queryDarkSkyTimeMachine(location, date)
    else:
        jsonResponse = queryDarkSkyForecast(location)

    print(jsonResponse) 

    return jsonResponse

def getLocation(jsonRequest):
    if ('name' in request.json):
        location = queryGoogleGeocode(request.json['name'])
        return location
    return 'error: No Address Given'
    
def getDate(jsonRequest):
    if ('date' in request.json):
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
        date = request.json['date'] + 'T' + h + ':' + m + ':' + s +'Z'
        return date

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
    address = address.replace(',', '')
    address = address.replace(' ', '')
    print(address)
    if (address):
        request = 'https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyBV5UxMqteJE2foIpiTA9AMlvObe67ZUso'
    else: 
        return 'error: no address'
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
