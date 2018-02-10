from urllib2 import Request, urlopen, URLError
import os
import time
import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/zip/<zipcode>')
def getDataByZip(zipcode):
    #TODO: query db for zipcode
    jsonResponse = queryDarkSkyForecast('32.6099,85.4808')
    data = json.loads(jsonResponse)
    print data['timezone']
    return data['timezone']

@app.route('/city/<citystate>')
def getDataByCity(citystate):
    #TODO: query db for city and state
    jsonResponse = queryDarkSkyForecast('32.6099,85.4808')
    data = json.loads(jsonResponse)
    print data['timezone']
    return data['timezone']

def queryDarkSkyForecast(latLongString):
    request = 'https://api.darksky.net/forecast/4a21043802f4364273e7fe25ba29c92b/'+latLongString
    try:
	    response = urlopen(request)
	    return response.read()
    except:
        return 'error'

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
