#!/usr/bin/env python
#coding=utf-8

import mysql.connector
import json
from datetime import datetime
import errorhandler as err
import functions

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

# MYSQL CONNECTION
cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
cursor = cnx.cursor(buffered=True)

# BASIC QUERIES

# Tokens
query_addTokens = ("INSERT IGNORE INTO tokens (user_id, access_token, refresh_token, expires_in, updated) VALUES (%s, %s, %s, %s, %s)")
query_updateTokens = ("UPDATE tokens SET access_token = %s, refresh_token = %s, expires_in = %s, updated = now() WHERE user_id = %s")
query_getAccesstoken = ("SELECT user_id, access_token FROM tokens WHERE user_id = %s")
query_getExpired = ("SELECT user_id, refresh_token FROM tokens WHERE updated <= now() - INTERVAL 6 HOUR")

# Sleep
query_getSleeplessIds = ("SELECT user_id FROM tokens WHERE user_id NOT IN (SELECT user_id FROM sleepdata)")
query_addSleepdata = ("INSERT IGNORE INTO sleepdata (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
query_getSleep = ("SELECT data FROM sleepdata WHERE user_id = %s and datetime = %s")

# HR
query_getSleep = ("SELECT data FROM sleepdata WHERE user_id = %s and datetime = %s")



##################################################################    
# TOKENS                                                        #
##################################################################

# add tokens to database
def addTokens(data):
    
    global query_addTokens
    
    try:
        maindata = (data['user_id'], data['access_token'], data['refresh_token'], data['expires_in'], data['datetime'])
        cursor.execute(query_addTokens, maindata)
        cnx.commit()
        return {'success': True}
    
    except Exception as e:
        return err.fail(str(e))
    
# updates tokens in database
def updateTokens(data):
    
    global query_updateTokens
    
    maindata = (data.get('access_token', ""), data.get('refresh_token', ""), data.get('expires_in', 0), data.get('user_id', ""))
    cursor.execute(query_updateTokens, maindata)
    cnx.commit()
        
# returns accesstoken by user_id
def getAccesstoken(data):
    
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
def getExpired():
    
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
def addSleepdata(data):
    
    global query_addSleepdata
    
    try:
        maindata = (data['uniqueid'], data['user_id'], data['datetime'], data['data'])
        cursor.execute(query_addSleepdata, maindata)
        cnx.commit()
        return {"success": True}
    
    except Exception as e:
        print(str(e) + " query_addSleepdata error")
        return err.fail(str(e.code))

# Returns those who have given access to their data but do not have sleep data yet in the DB
def getSleepless():
    
    global query_getSleeplessIds
    
    try:
        cursor.execute(query_getSleeplessIds)
        cnx.commit()
        data = {"ids": [], "success": True}
        
        if(cursor.rowcount == 0):
            return err.fail()
        
        for user_id, in cursor:
            data['ids'].append(user_id)
            
        return data
    
    except Exception as e:
        print(str(e) + " query_getSleeplessIds error")
        return err.fail(str(e.code))

# Returns sleep data by datetime.
def getSleep(data):
    
    global query_getSleep
    
    try:
        maindata = (data['user_id'], data['datetime'])
        cursor.execute(query_getSleep, maindata)
        cnx.commit()
        
        # Fetch the sleep data if not found in db
        if(cursor.rowcount == 0):
            
            access = getAccesstoken(data)
            data.update({'access_token': access.get('access_token','')})
            if(access.get('success', False)):

                if(functions.import_sleep(data, data['datetime']).get('success', False)):
                    
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
        print(str(e) + " query_getSleep error")
        return err.fail(str(e))
    
##################################################################    
# HEARTRATE DATA                                                 #
##################################################################

# Returns sleep data by datetime.
def getHr(data):
    
    global query_getHr
    
    try:
        maindata = (data['user_id'], data['datetime'])
        cursor.execute(query_getSleep, maindata)
        cnx.commit()
        
        # Fetch the sleep data if not found in db
        if(cursor.rowcount == 0):
            
            access = getAccesstoken(data)
            data.update({'access_token': access.get('access_token','')})
            if(access.get('success', False)):

                if(functions.import_sleep(data, data['datetime']).get('success', False)):
                    
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
        print(str(e) + " query_getSleep error")
        return err.fail(str(e))
    
