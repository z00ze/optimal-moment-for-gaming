import dbhandler
import functions

def sleepless():
    
    sleepless = dbhandler.getSleepless()
    
    if(sleepless.get('success', False)):
        for userid in sleepless.get('ids', []):
            functions.import_sleep(userid)

def refreshTokens():

    expired = dbhandler.getExpired()
    
    if(expired.get('success', False)):
        for user in expired['users']:
            functions.refresh_token(user)