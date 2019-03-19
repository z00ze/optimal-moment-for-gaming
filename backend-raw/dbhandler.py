#!/usr/bin/env python
#coding=utf-8

import mysql.connector
import json
from datetime import datetime
import errorhandler as err
import functions
import hashlib
import time
import dateutil.parser

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

# MYSQL CONNECTION
#cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
#cursor = cnx.cursor(buffered=True)



# BASIC QUERIES

# Tokens
query_addTokens = ("INSERT IGNORE INTO tokens (user_id, access_token, refresh_token, expires_in, updated) VALUES (%s, %s, %s, %s, %s)")
query_updateTokens = ("UPDATE tokens SET access_token = %s, refresh_token = %s, expires_in = %s, updated = now() WHERE user_id = %s")
query_getAccesstoken = ("SELECT user_id, access_token FROM tokens WHERE user_id = %s")
query_getExpired = ("SELECT user_id, refresh_token FROM tokens WHERE updated <= now() - INTERVAL 6 HOUR")

# Sleep
query_addSleepdata = ("INSERT IGNORE INTO sleepdata (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
query_getSleep = ("SELECT data FROM sleepdata WHERE user_id = %s and datetime = %s")
query_getSleepCountDup = ("SELECT count(*) FROM sleepdata WHERE user_id = %s and datetime = %s and uniqueid != %s")
query_deleteSleep = ("DELETE FROM sleepdata WHERE user_id = %s and datetime = %s")

# HR
query_addHRdata = ("INSERT IGNORE INTO heartratedata (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
query_getHr = ("SELECT data FROM heartratedata WHERE user_id = %s and datetime = %s")

# HR detailed
query_addHR_detaileddata = ("INSERT IGNORE INTO heartrate_detailed (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
query_getHr_detailed = ("SELECT data FROM heartrate_detailed WHERE user_id = %s and datetime = %s")
query_getHr_detailedCountDup = ("SELECT count(*) FROM heartrate_detailed WHERE user_id = %s and datetime = %s and uniqueid != %s")
query_deleteHr_detailed = ("DELETE FROM heartrate_detailed WHERE user_id = %s and datetime = %s")

# EyeTracker
query_setTrackerdata = ("INSERT IGNORE INTO eyetracker (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
query_getTrackerdata = ("SELECT data FROM eyetracker WHERE uniqueid = %s")
query_addTrackerdata = ("UPDATE eyetracker SET data = JSON_ARRAY_APPEND(data, '$', CAST(%s AS JSON)) WHERE uniqueid = %s")

# Get users
query_getUsers = ("SELECT user_id, access_token FROM tokens")

##################################################################
# USERS                                                          #
##################################################################

def getUsers(cnx, cursor):
    
    global query_getUsers
    
    try:
        cursor.execute(query_getUsers)
        cnx.commit()
        data = {"success": True, "users":[]}
        for (user_id, access_token) in cursor:
            data['users'].append({"user_id": user_id, "access_token": access_token})
        return data
    
    except Exception as e:
        return err.fail(str(e))

##################################################################
# TOKENS                                                         #
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
# SLEEP DATA                                                     #
##################################################################
# Adds sleep data to DB
def addSleepdata(data, cnx, cursor):
    
    global query_addSleepdata
    global query_getSleepCountDup
    global query_deleteSleep
    
    try:
        maindata = (data['user_id'], data['datetime'], data['uniqueid'])
        cursor.execute(query_getSleepCountDup, maindata)
        cnx.commit()
        for i, in cursor:
            if(int(i) != 0):
                maindata = (data['user_id'], data['datetime'])
                cursor.execute(query_deleteSleep, maindata)
                cnx.commit()
        
        maindata = (data['uniqueid'], data['user_id'], data['datetime'], data['data'])
        cursor.execute(query_addSleepdata, maindata)
        cnx.commit()
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e.code))

# Returns sleep data by datetime.
def getSleep(data, cnx, cursor):

    global query_getSleep
    
    try:
        maindata = (data['user_id'], data['datetime'])
        cursor.execute(query_getSleep, maindata)
        cnx.commit()
        
        # Fetch the sleep data if not found in db
        if(cursor.rowcount == 0):
            
            access = getAccesstoken(data, cnx, cursor)
            data.update({'access_token': access.get('access_token','')})
            if(access.get('success', False)):
                if(functions.import_sleep(data, cnx, cursor, data['datetime']).get('success', False)):
                    
                    # Makes new request to db if the record would be now there.
                    try:
                        maindata = (data['user_id'], data['datetime'])
    
                        cursor.execute(query_getSleep, maindata)
                        cnx.commit()
            
                    except Exception as e:
                        print(str(e) + " query_getSleep error")
                        return err.fail(str(e))
            
        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}
        
        
        return err.fail()
    
    except Exception as e:
        return err.fail(str(e))

##################################################################
# HEARTRATE DETAILED DATA                                        #
##################################################################

# Returns heartrate data by datetime.
def getHrDetailed(data, cnx, cursor):
    global query_getHr_detailed
    
    try:
        maindata = (data['user_id'], data['datetime'])
        cursor.execute(query_getHr_detailed, maindata)
        cnx.commit()
        
        # Fetch the hr data if not found in db
        if(cursor.rowcount == 0):
            
            access = getAccesstoken(data, cnx, cursor)
            data.update({'access_token': access.get('access_token','')})
            if(access.get('success', False)):
                if(functions.import_detailed_hr(data, data['datetime'], cnx, cursor).get('success', False)):
                    
                    # Makes new request to db if the record would be now there.
                    try:
                        maindata = (data['user_id'], data['datetime'])
                        print(maindata)
                        cursor.execute(query_getHr_detailed, maindata)
                        cnx.commit()
                        if(cursor.rowcount == 0):
                            print("rawrarwar")
            
                    except Exception as e:
                        return err.fail(str(e))
            
        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}
        
        return err.fail()
    
    except Exception as e:
        return err.fail(str(e))
    

# Adds detailed hr data to DB
def addHrDetailed(data, cnx, cursor):
    
    global query_addHR_detaileddata
    global query_getHr_detailedCountDup
    global query_deleteHr_detailed
    
    
    try:
        maindata = (data['user_id'], data['datetime'], data['uniqueid'])
        cursor.execute(query_getHr_detailedCountDup, maindata)
        cnx.commit()
        i = cursor.fetchone()
        if(int(i[0]) != 0):
            maindata = (data['user_id'], data['datetime'])
            cursor.execute(query_deleteHr_detailed, maindata)
            cnx.commit()

        maindata = (data['uniqueid'], data['user_id'], data['datetime'], data['data'])
        cursor.execute(query_addHR_detaileddata, maindata)
        cnx.commit()
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))


# Adds detailed hr data to DB
def addTrackerdata(data, cnx, cursor):
    
    global query_setTrackerdata
    global query_addTrackerdata
    
    try:
        
        data['data']['datetime'] = data['datetime']
        dt = dateutil.parser.parse(data['datetime'])
        data['datetime'] = str(datetime(dt.year, dt.month, dt.day))
        data['unique_id'] = str(hashlib.sha256(bytes(data.get('user_id','') + json.dumps(data.get('datetime','')), 'utf-8')).hexdigest())
        
        maindata = (data['unique_id'], data['user_id'], data['datetime'], '[]')
        
        # set the data if not set
        cursor.execute(query_setTrackerdata, maindata)
        cnx.commit()
        
        # append data
        maindata = (str(json.dumps(data['data'])), data['unique_id'])
        
        cursor.execute(query_addTrackerdata, maindata)
        cnx.commit()
        
        return {"success": True}
    
    except Exception as e:
        return err.fail(str(e))
