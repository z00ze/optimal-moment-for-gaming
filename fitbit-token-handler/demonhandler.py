import dbhandler
import functions

def refreshTokens():

    expired = dbhandler.getExpired()
    
    if(expired.get('success', False)):
        for user in expired['users']:
            functions.refresh_token(user)