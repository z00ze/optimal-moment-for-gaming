from datetime import datetime, timedelta
import math
import hashlib
import mysql.connector
import json

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
cursor = cnx.cursor(buffered=True)

dt = datetime.strptime("2019-03-01 00:00:00", "%Y-%m-%d %H:%M:%S")

datapoints = []
dummyseed = 578903879

for i in range(86400):
    
    dt += timedelta(seconds=1)
    dummyseed += 1
    eyetracker = {"sumvector": math.tan(dummyseed*0.9) % 100, "dist": math.tan(dummyseed*0.53) % 100, "pupils-avg": math.tan(dummyseed*1.3) % 100}
    maindata = (
        str(hashlib.sha256(bytes("7B8P5X" + json.dumps(str(dt)), 'utf-8')).hexdigest()),
        dt, 
        math.tan(dummyseed) % 100, 
        math.cos(dummyseed) % 100, 
        math.sin(dummyseed) % 100, 
        str(json.dumps(eyetracker)), 
        "7B8P5X", 
        False
    )
    
    cursor.execute(("INSERT IGNORE INTO processed (uniqueid, datetime, omfg, effiency, heartrate, eyetrack, user_id, predict) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"), maindata)
    cnx.commit()



