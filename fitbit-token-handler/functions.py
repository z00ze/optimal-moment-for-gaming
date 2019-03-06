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


import dbhandler
import demonhandler
import errorhandler as err

# CREDENTIALS
credentials = open('credentials-fitbitapp.data', 'r').read().split('\n')
client_id = credentials[0]
client_secret = credentials[1]


##################################################################
# Retvieve sleep data                                            #
##################################################################
def import_sleep(data, date=None):
    
    startdate = ""
    enddate = ""
    url = ""
    
    if(date == None):
        startdate = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        enddate = datetime.today().strftime('%Y-%m-%d')

        url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/'+ enddate +'.json'
    else:
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
        
        thenight = dbhandler.addSleepdata(night)
        if(not thenight.get('success', False)):
            return thenight
    return {"success": True}

##################################################################
# Retvieve HR data                                            #
##################################################################
def import_hr(data, date=None):
    
    try:
        startdate = ""
        enddate = ""
        url = ""
        if(date == None):
            startdate = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
            enddate = datetime.today().strftime('%Y-%m-%d')

            url = 'https://api.fitbit.com/1/user/-/heart/date/' + startdate + '/'+ enddate +'/1d.json'
        else:
            
            url = 'https://api.fitbit.com/1/user/-/activities/heart/date/'+date+'/1d.json'


        request = Request(url)
        
        request.add_header('Authorization', 'Bearer ' + data.get('access_token', ''))
        hrs = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
        for hr in hrs.get('activities-heart', []):
            day = {}
            day['user_id'] = data.get('user_id','')
            day['uniqueid'] = str(hashlib.sha256(bytes(day.get('user_id','') + json.dumps(hr),'utf-8')).hexdigest())

            day['data'] = json.dumps(hr)
            day['datetime'] = hr.get('dateTime','')

            theday = dbhandler.addHRdata(day)
            if(not theday.get('success', False)):
                return theday
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))


##################################################################
# Retvieve detailed HR data                                      #
##################################################################
# Date range does not work in here, https://community.fitbit.com/t5/Web-API-Development/Intra-Day-Activity-Time-Series-for-Date-Range/m-p/2323035
def import_detailed_hr(data, date):
    
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
            
            theday = dbhandler.addHrDetailed(day)
            
            if(not theday.get('success', False)):
                return theday
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))

##################################################################
# Refresh tokens for user                                        #
##################################################################

def refresh_token(user):
    request_params = {
                'grant_type': 'refresh_token',
                'refresh_token' : user.get('refresh_token','')
            }
    url = 'https://api.fitbit.com/oauth2/token'
    try:
        cres = (client_id + ":" + client_secret).encode()
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + base64.b64encode(cres).decode()}
        request = Request(url, urllib.parse.urlencode(request_params).encode(), headers=headers)
        
        response = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
        dbhandler.updateTokens(response)

    except urllib.error.HTTPError as e:
        return err.fail(str(e))
    except urllib.error.URLError as e:
        return err.fail(str(e))
