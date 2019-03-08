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
# Retvieve sleep data                                            #
##################################################################
def import_sleep(data, cnx, cursor, date=None):
    
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
        
        thenight = dbhandler.addSleepdata(night, cnx, cursor)
        if(not thenight.get('success', False)):
            return thenight
    return {"success": True}

##################################################################
# Retvieve HR data                                            #
##################################################################
def import_hr(data, cnx, cursor, date=None):
    
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

            theday = dbhandler.addHRdata(day, cnx, cursor)
            if(not theday.get('success', False)):
                return theday
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))


##################################################################
# Retvieve detailed HR data                                      #
##################################################################
# Date range does not work in here, https://community.fitbit.com/t5/Web-API-Development/Intra-Day-Activity-Time-Series-for-Date-Range/m-p/2323035
def import_detailed_hr(data, date, cnx, cursor):
    
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

##################################################################
# Gather all data and return it in same time frame.              #
##################################################################
def gatherer(data, cnx, cursor):
    
    # data has user_id, time_from and time_to
    time_from = dateutil.parser.parse(data['time_from'])
    time_to = dateutil.parser.parse(data['time_to'])
    time_between = int((time_to-time_from).total_seconds())
    
    datapoints = []
    for i in range(time_between):
        datapoints.append(
            {
                "datetime": str(time_from + timedelta(0, i)),
                "heart_rate": {"value":-1},
                "sleep": {"level":""},
                "eye_tracker": {"left": -1, "right": -1}
            })
    
    # HR DETAILED
    maindata = (
                str(time_from),
                str(time_to),
                data['user_id']
               )
    query_getHr_detailed_range = ("SELECT hr.v, ADDTIME(datetime, hr.t) as dt FROM heartrate_detailed, JSON_TABLE(data, '$.dataset[*]' COLUMNS (v INT(40) PATH '$.value', t VARCHAR(100) PATH '$.time')) hr WHERE ADDTIME(datetime, hr.t) >= %s AND ADDTIME(datetime, hr.t) <= %s AND user_id LIKE %s")
    cursor.execute(query_getHr_detailed_range, maindata)
    cnx.commit()
    hr_data = []
    for v,t, in cursor:
            hr_data.append({"value": v, "time": str(t)})


    
    # SLEEP
    time_from_without_time = time_from.replace(hour=0, minute=0, second=0)
    time_to_without_time = time_to.replace(hour=0, minute=0, second=0)
    query_getSleepdata = ("SELECT data FROM sleepdata WHERE datetime BETWEEN %s AND %s AND user_id LIKE %s")
    maindata = (
                str(time_from_without_time),
                str(time_to_without_time),
                data['user_id']
               )
    cursor.execute(query_getSleepdata, maindata)
    cnx.commit()
    sleep_data = []
    for val, in cursor:
        data = json.loads(val)
        for dt in data['levels']['data']:
            sleep_data.append(dt)

    # GOTTA CATCH 'EM ALL!

    for datapoint in datapoints:
        dt = dateutil.parser.parse(datapoint['datetime'])
        for hr in hr_data:
            
            if(datapoint['datetime'] == hr['time']):
                datapoint['heart_rate']['value'] = hr['value']
        
        for sleep in sleep_data:
            dt_slp = dateutil.parser.parse(sleep['dateTime'])
            if(dt_slp == dt):
                print("rawr")
            if(dt_slp +  timedelta(0, sleep['seconds']) >= dt and dt_slp +  timedelta(0, sleep['seconds']) <= dt):
                datapoint['sleep']['level'] = sleep['level']
            
    return {"success": True}

#{
#	“time_from” : “”,		# DATETIME
#	“time_to” : “”,		# DATETIME 
#	“datapoints”: [
#		“datetime”: “”,	# DATETIME BY DEFINED INTERVAL (5 sec / 1 sec etc)
#		“heart_rate”: {
#			“value”: 69					# HEART RATE
#   },
#       “eye_tracker” : {
#	          “left”: 0, “right”: 0			# EYE LOCATIONS
#       }
#       “sleep” : {
#	          "level": ""					# SLEEP LEVEL (rem/light/wake etc)
#       }
#]
#}



    #global query_getAll
    #try:
     #   maindata = (data['user_id'], data['time_from'], data['time_to'])

    #    cursor.execute(query_getAll, maindata)
    #    cnx.commit()
        
    #    return data
    #except Exception as e:
    #    return err.fail(str(e))
    
    