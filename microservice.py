from urllib2 import urlopen, URLError
import os
import time
import json
from flask import Flask, jsonify, request, render_template
from cloudant import Cloudant
import cf_deployment_tracker
import atexit
from cloudant.result import Result, ResultByKey

# Emit Bluemix deployment event
cf_deployment_tracker.track()

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'cache'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
        if db.exists():
            print "'{0}' successfully created.\n".format(db_name)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

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

    date = str(int(int(int(request.json['datetime'])/60000)*60))

    docId = location+date 

    result_collection = list(Result(db.all_docs))

    for x in range(0, len(result_collection)-1):
        if (docId == result_collection[x]['id']):
            print('cached')
            document = db[docId]
            return json.loads(document['doc'])
        
    locationMap = queryDarkSkyTimeMachine(location, date)

    if (str(locationMap).startswith('error')):
        return locationMap

    document = {} 
    if client:
        document['doc'] = json.dumps(locationMap)
        document['_id'] = docId
        db.create_document(document)
    
    return json.dumps(locationMap[docId])


def getLocation(jsonRequest):
    if ('name' in request.json):
        location = queryGoogleGeocode(request.json['name'])
        return location
    return 'error: No Address Given'

def queryDarkSkyTimeMachine(latLongString, time):
    request = 'https://api.darksky.net/forecast/4a21043802f4364273e7fe25ba29c92b/'+latLongString+','+time
    try: 
        locTimeMap = {}
        response = urlopen(request)
        data = json.loads(response.read())
        currently = data['currently']
        #currently['minutely'] = data['minutely']['summary']
        hourly = data['hourly']
        daily = data['daily']

        for i in range(0, len(daily['data'])-1):
            locTimeMap[latLongString + str(daily['data'][i]['time'])] = daily['data'][i]
        
        for i in range(0, len(hourly['data'])-1):
            locTimeMap[latLongString + str(hourly['data'][i]['time'])] = hourly['data'][i]
        
        locTimeMap[latLongString + time] = currently

        return locTimeMap
    except Exception as e:
        print(e) 
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

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
