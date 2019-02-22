import mysql.connector
import json
from datetime import datetime
import errorhandler as err

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

# MYSQL CONNECTION
cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
cursor = cnx.cursor(buffered=True)

# BASIC QUERIES

query_addTokens = ("INSERT IGNORE INTO tokens (userid, access_token, refresh_token, expires_in, updated) VALUES (%s, %s, %s, %s, %s)")
query_getAccesstoken = ("SELECT userid, access_token FROM tokens WHERE userid = %s")

query_getSleeplessIds = ("SELECT userid FROM tokens WHERE userid NOT IN (SELECT userid FROM sleepdata)")
query_addSleepdata = ("INSERT IGNORE INTO sleepdata (uniqueid, userid, datetime, data) VALUES (%s, %s, %s, %s)")
query_getSleep = ("SELECT data FROM fitbittokens.sleepdata WHERE userid = %s and datetime = %s")

##################################################################    
# ToOKENS                                                        #
##################################################################
def addTokens(data):
    
    global query_addTokens
    
    try:
        maindata = (data['user_id'], data['access_token'], data['refresh_token'], data['expires_in'], data['datetime'])
        cursor.execute(query_addTokens, maindata)
        cnx.commit()
        return True
    
    except Exception as e:
        print(e)
        return False
    
def getAccesstoken(userid):
    
    global query_getAccesstoken
    
    try:
        cursor.execute(query_getAccesstoken, (userid,))
        cnx.commit()
        if(cursor.rowcount == 0):
            return err.fail()
        for (user_id, accesstoken) in cursor:
            return {"success": True, "userid": user_id, "access_token": accesstoken}
        
    except Exception as e:
        print(e)
        return err.fail()
    
    
##################################################################    
# SLEEP DATA                                                     #
##################################################################

# Adds sleep data to DB
def addSleepdata(data):
    
    global query_addSleepdata
    
    try:
        maindata = (data['uniqueid'], data['userid'], data['datetime'], data['data'])
        cursor.execute(query_addSleepdata, maindata)
        cnx.commit()
        return True
    
    except Exception as e:
        print(str(e) + " query_addSleepdata error")
        return { "success": False, "errorcode": str(e.code) }

# Returns those who have given access to their data but do not have sleep data yet in the DB
def getSleepless():
    
    global query_getSleeplessIds
    
    try:
        cursor.execute(query_getSleeplessIds)
        cnx.commit()
        data = {"ids": [], "success": True}
        
        if(cursor.rowcount == 0):
            return err.fail()
        
        for userid, in cursor:
            data['ids'].append(userid)
            
        return data
    
    except Exception as e:
        print(str(e) + " query_getSleeplessIds error")
        return err.fail(str(e.code))

# Returns sleep data by datetime.
def getSleep(data):
    
    global query_getSleep
    
    try:
        maindata = (data['userid'], data['datetime'])
        cursor.execute(query_getSleep, maindata)
        cnx.commit()
        
        if(cursor.rowcount == 0):
            print(getAccesstoken(data['userid']))
            # TODO :
            #       Fetching data from FITBIT if data is not in database
            #       Checking if user has given access to the data
            print("0")
            
        for val, in cursor:
            return {"success": True, "data" : json.loads(val)}
        
        return err.fail()
    
    except Exception as e:
        print(str(e) + " query_getSleep error")
        return err.fail(str(e))
    
