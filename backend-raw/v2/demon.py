#!/usr/bin/env python
#coding=utf-8

import time

##################################################################
# Runs different tasks once in a hour.                           #
##################################################################

while(True):
    
    print("Awoken!")
    
    # Refreshes access tokens which are about to get old.
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
    
    print("Sleepings...")
    time.sleep(3600)