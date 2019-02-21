import mysql.connector
from datetime import datetime

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
        
        for (user_id, accesstoken) in cursor:
            return {"userid": user_id, "access_token": accesstoken}
        
    except Exception as e:
        print(e)
        return False
    
    
##################################################################    
# SLEEP DATA                                                     #
##################################################################
def addSleepdata(data):
    
    global query_addSleepdata
    
    try:
        maindata = (data['uniqueid'], data['userid'], data['datetime'], data['data'])
        cursor.execute(query_addSleepdata, maindata)
        cnx.commit()
        return True
    
    except Exception as e:
        print(str(e) + " addsleepdata error")
        return False

def getSleepless():
    cursor.execute(query_getSleeplessIds)
    cnx.commit()
    ids = []
    for userid, in cursor:
        ids.append(userid)
    return ids

