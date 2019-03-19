import dbhandler
import functions
import mysql.connector
import datetime as datetime

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
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    credentials_db = open('credentials-db.data', 'r').read().split('\n')
    user = credentials_db[0]
    password = credentials_db[1]
    
    cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
    cursor = cnx.cursor(buffered=True)
    
    # get all users...
    data = dbhandler.getUsers(cnx, cursor)
    
    for user in data['users']:
        
        functions.import_sleep(user, cnx, cursor, current_date)
        functions.import_detailed_hr(user, cnx, cursor, current_date)
    

    cursor.close()
    cnx.close()