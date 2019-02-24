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
def import_sleep(sleepless, date=None):
    # SLEEP
    data = dbhandler.getAccesstoken(sleepless)

    if(date == None):
        startdate = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        enddate = datetime.today().strftime('%Y-%m-%d')

        url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/'+ enddate +'.json'
        request = Request(url)
        request.add_header('Authorization', 'Bearer ' + data['access_token'])
        sleeps = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))['sleep']

        for sleep in sleeps:
            night = {}
            
            # .update
            # .update
            night['userid'] = data['userid']
            night['uniqueid'] = str(hashlib.sha256(bytes(night['userid'] + json.dumps(sleep),'utf-8')).hexdigest())
            night['data'] = json.dumps(sleep)
            night['datetime'] = sleep['dateOfSleep']
            if(dbhandler.addSleepdata(night)):
                print("OK")
            else:
                print("FAIL")
    else:
        # one sleep
        print("r")
        
##################################################################    
# Refresh tokens for user                                        #
##################################################################

def refresh_token(user):
    request_params = {
                'grant_type': 'refresh_token',
                'refresh_token' : user['refresh_token']
            }
    url = 'https://api.fitbit.com/oauth2/token'
    try:
        cres = (client_id + ":" + client_secret).encode()
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + base64.b64encode(cres).decode()}
        request = Request(url, urllib.parse.urlencode(request_params).encode(), headers=headers)
        response = json.loads(urlopen(request).read().decode())

        print(response)
        dbhandler.updateTokens(response)

        
    except urllib.error.HTTPError as e:
        return err.fail(str(e.code))
    except urllib.error.URLError as e:
        return err.fail(str(e.code))
