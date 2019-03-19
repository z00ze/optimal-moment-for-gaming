#!/usr/bin/env python
#coding=utf-8

import mysql.connector
import json
from datetime import datetime
import errorhandler as err
import hashlib
import time
import dateutil.parser

import urllib
import urllib.error
from urllib.request import Request, urlopen
import urllib.parse
import base64

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

# Tokens
query_addTokens = ("INSERT IGNORE INTO tokens (user_id, access_token, refresh_token, expires_in, updated) VALUES (%s, %s, %s, %s, %s)")
query_updateTokens = ("UPDATE tokens SET access_token = %s, refresh_token = %s, expires_in = %s, updated = now() WHERE user_id = %s")
query_getAccesstoken = ("SELECT user_id, access_token FROM tokens WHERE user_id = %s")
query_getExpired = ("SELECT user_id, refresh_token FROM tokens WHERE updated <= now() - INTERVAL 6 HOUR")

# HR timeseries
query_addHR_detaileddata = ("INSERT IGNORE INTO heartrate_timeseries (uniqueid, user_id, datetime, value) VALUES (%s, %s, %s, %s)")
query_getHR_detaileddata = ("SELECT datetime, value FROM heartrate_timeseries WHERE user_id = %s AND datetime BETWEEN %s AND %s")

# Eyetracker
query_addEyetrackerData = ("INSERT IGNORE INTO eyetracker_timeseries (uniqueid, user_id, datetime, left_pupil, right_pupil, sumvector) VALUES (%s, %s, %s, %s, %s, %s)")
query_getEyetrackerData = ("SELECT user_id, datetime, left_pupil, right_pupil, sumvector FROM eyetracker_timeseries WHERE user_id = %s AND datetime BETWEEN %s AND %s")

##################################################################
# TOKENS                                                        #
##################################################################

# add tokens to database
def addTokens(data, cnx, cursor):
    
    global query_addTokens
    
    try:
        maindata = (data['user_id'], data['access_token'], data['refresh_token'], data['expires_in'], data['datetime'])
        cursor.execute(query_addTokens, maindata)
        cnx.commit()
        return {'success': True}
    
    except Exception as e:
        return err.fail(str(e))
    
# updates tokens in database
def updateTokens(data, cnx, cursor):
    
    global query_updateTokens
    
    maindata = (data.get('access_token', ""), data.get('refresh_token', ""), data.get('expires_in', 0), data.get('user_id', ""))
    cursor.execute(query_updateTokens, maindata)
    cnx.commit()
        
# returns accesstoken by user_id
def getAccesstoken(data, cnx, cursor):
    
    global query_getAccesstoken

    try:
        cursor.execute(query_getAccesstoken, (data.get('user_id',''),))
        cnx.commit()
        if(cursor.rowcount == 0):
            return err.fail('no user')
        
        for (user_id, access_token) in cursor:
            asd = {
                    'success': True,
                    'user_id': user_id,
                    'access_token': access_token
                    }
            return asd

    except Exception as e:
        return err.fail(str(e))

# returns those users who are about to have access token expired
def getExpired(cnx, cursor):
    
    global query_getExpired
    
    try:
        cursor.execute(query_getExpired)
        cnx.commit()
        if(cursor.rowcount == 0):
            return err.fail("no expired users")
        expired_users = {"users": [], "success": True}
        for (user_id, refresh_token) in cursor:
            expired_users['users'].append({"user_id": user_id, "refresh_token": refresh_token})
        
        return expired_users
    
    except Exception as e:
        print()
        return err.fail()

##################################################################
# HR                                                             #
##################################################################
def populateHR(data, cnx, cursor):
    
    global query_addHR_detaileddata
    
    try:
        access = getAccesstoken(data, cnx, cursor)
        data.update({'access_token': access.get('access_token','')})
       
        if(access.get('success', False)):
            data['data'] = fetch_hr_detailed(data, data['datetime'], cnx, cursor)
            
        datapoints_to_add = []
        for dat in data['data']['dataset']:
            
            datapoint_datetime = data['datetime'] + " " + dat['time']
            data['uniqueid'] = str(hashlib.sha256(bytes(data['user_id'] + datapoint_datetime, 'utf-8')).hexdigest())
            datapoints_to_add.append((data['uniqueid'], data['user_id'], datapoint_datetime, dat['value']))
        
        cursor.executemany(query_addHR_detaileddata, datapoints_to_add)
        cnx.commit()
            
        return err.fail("ok")
    
    except Exception as e:
        return err.fail(str(e))


def addEyetrackerdata(data, cnx, cursor):
    
    global query_addEyetrackerData
    
    try:
        data['uniqueid'] = str(hashlib.sha256(bytes(data['user_id'] + data['datetime'], 'utf-8')).hexdigest())
        maindata = (data['uniqueid'], data['user_id'], data['datetime'], data['left_pupil'], data['right_pupil'], data['sumvector'])
        cursor.execute(query_addEyetrackerData, maindata)
        cnx.commit()
        
        return {"success": True}
        
    except Exception as e:
        return err.fail(str(e))
    
##################################################################
# Gather all data and return it in same time frame.              #
##################################################################
def gatherer(data, cnx, cursor):
    
    # data has user_id, time_from and time_to
    time_from = dateutil.parser.parse(data['time_from'])
    time_to = dateutil.parser.parse(data['time_to'])
    
    global query_getHR_detaileddata
    global query_getEyetrackerData
    
    try:
        maindata = (data['user_id'], data['time_from'], data['time_to'])
        cursor.execute(query_getHR_detaileddata, maindata)
        cnx.commit()
        
        detailed_data = {"time_from": data['time_from'], "time_to": data['time_to'], "datapoints": []}
        for dt,val in cursor:
            
            datapoint = {"datetime": str(dt), "heartrate": {"value": val}, "sleep": {"level": ""}, "eyetracker": {"left": -1, "right": -1}}
            
            detailed_data['datapoints'].append(datapoint)
        
        if(len(detailed_data) > 0):
            return detailed_data

        return err.fail("no data for time frame")
        
    
    except Exception as e:
        return err.fail(str(e))

    

####
# FUNCTIONS
####

def fetch_hr_detailed(data, date, cnx, cursor):
    
    try:
        url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + date + '/1d/1sec.json'
        
        request = Request(url)
        
        request.add_header('Authorization', 'Bearer ' + data.get('access_token', ''))
        hrs = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
        
        return hrs.get('activities-heart-intraday', '')
    
    except Exception as e:
        return err.fail(str(e))
