import mysql.connector
from datetime import datetime, timedelta
import json
import time

import urllib
import urllib.error
from urllib.request import Request, urlopen
import urllib.parse
import base64
from datetime import datetime, timedelta
import requests
import hashlib
import dateutil.parser

import dbhandler
import demonhandler
import errorhandler as err

# CREDENTIALS
credentials = open('credentials-fitbitapp.data', 'r').read().split('\n')
client_id = credentials[0]
client_secret = credentials[1]


##################################################################
# Retvieve sleep data from fitbit and add to db                  #
##################################################################
def import_sleep(data, cnx, cursor, date=None):
    startdate = ""
    enddate = ""
    
    url = 'https://api.fitbit.com/1.2/user/-/sleep/date/'+ date +'.json'
    
    request = Request(url)
    request.add_header('Authorization', 'Bearer ' + data.get('access_token', ''))
    sleeps = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
    for sleep in sleeps.get('sleep', []):
        night = {}
        night['user_id'] = data.get('user_id','')
        night['uniqueid'] = str(hashlib.sha256(bytes(night.get('user_id', '') + json.dumps(sleep),'utf-8')).hexdigest())
        
        night['data'] = json.dumps(sleep)
        night['datetime'] = sleep.get('dateOfSleep','')
        
        thenight = dbhandler.addSleepdata(night, cnx, cursor)
        
        if(not thenight.get('success', False)):
            return thenight
    return {"success": True}


##################################################################
# Retvieve hr data from fitbit and add to db                  #
##################################################################

def import_detailed_hr(data, cnx, cursor, date):
    
    try:
        url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + date + '/1d/1sec.json'

        request = Request(url)
        
        request.add_header('Authorization', 'Bearer ' + data.get('access_token', ''))
        hrs = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))

        intradata = hrs.get('activities-heart-intraday', '')
        for hr in hrs.get('activities-heart', []):
            day = {}
            day['user_id'] = data.get('user_id','')
            
            day['uniqueid'] = str(hashlib.sha256(bytes(day.get('user_id','') + json.dumps(intradata), 'utf-8')).hexdigest())
            day['data'] = json.dumps(intradata)
            day['datetime'] = hr.get('dateTime','')
            theday = dbhandler.addHrDetailed(day, cnx, cursor)
            
            if(not theday.get('success', False)):
                return theday
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))

##################################################################
# Refresh tokens for user                                        #
##################################################################

def refresh_token(user, cnx, cursor):
    request_params = {
                'grant_type': 'refresh_token',
                'refresh_token' : user.get('refresh_token','')
            }
    url = 'https://api.fitbit.com/oauth2/token'
    try:
        cres = (client_id + ":" + client_secret).encode()
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + base64.b64encode(cres).decode()}
        
        request = Request(url, urllib.parse.urlencode(request_params).encode(), headers=headers)
        print(request_params)
        response = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
        
        dbhandler.updateTokens(response, cnx, cursor)

    except urllib.error.HTTPError as e:
        return err.fail(str(e))
    except urllib.error.URLError as e:
        return err.fail(str(e)) 