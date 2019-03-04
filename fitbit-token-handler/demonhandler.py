import dbhandler
import functions

def sleepless():
    
    sleepless = dbhandler.getSleepless()
    if(sleepless.get('success', False)):
        for user_id in sleepless.get('ids', []):
            functions.import_sleep(user_id)
            
def heartless():
    
    heartless = dbhandler.getHeartless()
    if(heartless.get('success', False)):
        for user_id in heartless.get('ids', []):
            functions.import_hr(user_id)

def refreshTokens():

    expired = dbhandler.getExpired()
    
    if(expired.get('success', False)):
        for user in expired['users']:
            functions.refresh_token(user)