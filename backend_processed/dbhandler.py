#!/usr/bin/env python
#coding=utf-8

import mysql.connector
import json
from datetime import datetime
import hashlib
import time
import errorhandler as err

from Classes.Credentials import Credentials
CRED = Credentials()

# MYSQL CONNECTION
#cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
#cursor = cnx.cursor(buffered=True)



# BASIC QUERIES
# # Get users
query_get_users = ("SELECT user_id, access_token FROM tokens")

# Sleep
query_get_sleep_data = ("SELECT data FROM sleepdata WHERE user_id = %s and datetime = %s")

# HR
query_get_hr_data_by_date = ("SELECT data FROM heartrate_detailed WHERE user_id = %s and datetime = %s")

# eye tracker
query_eyetracker_data_by_date = ("SELECT data FROM eyetracker WHERE user_id = %s and datetime = %s")

# predicted time entries
query_predicted_time_entries_by_user = ("SELECT * FROM fitbittokens.processed_test WHERE user_id = %s and NOT predict")

# query_getSleepCountDup = ("SELECT count(*) FROM sleepdata WHERE user_id = %s and datetime = %s and uniqueid != %s")
# query_deleteSleep = ("DELETE FROM sleepdata WHERE user_id = %s and datetime = %s")

# # HR detailed
# query_addHR_detaileddata = ("INSERT IGNORE INTO heartrate_detailed (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")

# query_getHr_detailedCountDup = ("SELECT count(*) FROM heartrate_detailed WHERE user_id = %s and datetime = %s and uniqueid != %s")
# query_deleteHr_detailed = ("DELETE FROM heartrate_detailed WHERE user_id = %s and datetime = %s")

# # EyeTracker
# query_setTrackerdata = ("INSERT IGNORE INTO eyetracker (uniqueid, user_id, datetime, data) VALUES (%s, %s, %s, %s)")
# query_addTrackerdata = ("UPDATE eyetracker SET data = JSON_ARRAY_APPEND(data, '$', CAST(%s AS JSON)) WHERE uniqueid = %s")

# # Benchmark
# query_addBenchmark = ("INSERT IGNORE INTO benchmark (uniqueid, datetime, user_id, result) VALUES (%s, %s, %s, %s)")                   

def init_connection(func):
    def wrapper(*args, **kwargs):
        print(f"\n ## init_connection to db before function: {func.__name__} ## ")
        cnx = mysql.connector.connect(user=CRED.user, database='fitbittokens', password=CRED.password)
        cursor = cnx.cursor(buffered=True)
        kwargs["cnx"] = cnx
        kwargs["cursor"] = cursor        
        
        result = func(*args, **kwargs)
        
        cursor.close()
        cnx.close()

        return result
    return wrapper

##################################################################
# USERS                                                          #
##################################################################

@init_connection
def get_users(cnx=None, cursor=None):    
    try:
        cursor.execute(query_get_users)
        cnx.commit()
        data = {"success": True, "users":[]}
        for (user_id, access_token) in cursor:
            data['users'].append({"user_id": user_id, "access_token": access_token})

        return data
    
    except Exception as e:
        print("get_users encountered exception")
        return err.fail(str(e))

# Returns sleep data by datetime.
@init_connection
def get_sleep_data_by_date(user_id, datetime, cnx=None, cursor=None):
    try:
        maindata = (user_id, datetime)
        cursor.execute(query_get_sleep_data, maindata)
        cnx.commit()
        
        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}       
        
        return err.fail()
    
    except Exception as e:
        return err.fail(str(e))

##################################################################
# HEARTRATE DETAILED DATA                                        #
##################################################################

# Returns heartrate data by datetime.
@init_connection
def get_hr_data_by_date(user_id, datetime, cnx=None, cursor=None):
    global query_getHr_detailed
    
    try:
        maindata = (user_id, datetime)
        cursor.execute(query_get_hr_data_by_date, maindata)
        cnx.commit()

        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}       
        
        return err.fail()
    
    except Exception as e:
        return err.fail(str(e))

@init_connection
def get_eye_tracker_data_by_date(user_id, datetime, cnx=None, cursor=None):
    
    try:
        maindata = (user_id, datetime)
        print(f"maindata:{maindata}")
        cursor.execute(query_eyetracker_data_by_date, maindata)
        cnx.commit()
        
        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}       
        
        return err.fail()
    
    except Exception as e:
        return err.fail(str(e))


@init_connection
def get_predicted_data_entries(user_id, cnx=None, cursor=None):    

    try:
        maindata = (user_id,)
        cursor.execute(query_predicted_time_entries_by_user, maindata)
        cnx.commit()
        result = cursor.fetchall()   
        if(result):            
            return {"success": True, "data" : result}       
        
        return err.fail("No predicted data found.")
    
    except Exception as e:
        return err.fail(str(e))
