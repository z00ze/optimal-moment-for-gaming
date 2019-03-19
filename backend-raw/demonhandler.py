import dbhandler
import functions
import mysql.connector
from datetime import datetime, timedelta

def refreshTokens():
    
    credentials_db = open('credentials-db.data', 'r').read().split('\n')
    user = credentials_db[0]
    password = credentials_db[1]
    
    cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
    cursor = cnx.cursor(buffered=True)
    expired = dbhandler.getExpired(cnx, cursor)
    
    if(expired.get('success', False)):
        for user in expired['users']:
            functions.refresh_token(user, cnx, cursor)
            
    cursor.close()
    cnx.close()

def fetchData():
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    credentials_db = open('credentials-db.data', 'r').read().split('\n')
    user = credentials_db[0]
    password = credentials_db[1]
    
    cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
    cursor = cnx.cursor(buffered=True)
    
    # get all users
    data = dbhandler.getUsers(cnx, cursor)
    
    for user in data['users']:
        
        # update users data for today
        functions.import_sleep(user, cnx, cursor, current_date)
        functions.import_detailed_hr(user, cnx, cursor, current_date)
        
        # update users data for yesterday
        functions.import_sleep(user, cnx, cursor, yesterday)
        functions.import_detailed_hr(user, cnx, cursor, yesterday)
    

    cursor.close()
    cnx.close()