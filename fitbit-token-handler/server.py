#!/usr/bin/env python
#coding=utf-8

# FILE
import os
# api cherrypy
import cherrypy
import string
import json

import urllib
import urllib.error
from urllib.request import Request, urlopen
import urllib.parse
import base64
from datetime import datetime, timedelta
import requests
from cherrypy.lib.static import serve_file

# DATABASE
import dbhandler
# DEMONHANDLER
import demonhandler
# ERROR HANDLER
import errorhandler as err

# CREDENTIALS
credentials = open('credentials-fitbitapp.data', 'r').read().split('\n')
client_id = credentials[0]
client_secret = credentials[1]

def fail():
    return { "success": False }

@cherrypy.expose
class omfg(object):
        
    def GET(self):
        return open('index.html')

    
    
    @cherrypy.expose
    def GET(self, var = None, code = ''):
        global client_id
        global client_secret
        
        ##################################################################
        # Endpoint for giving user consent to use their fitbit data.     #
        ##################################################################
        
        if(var == 'fitbit-permission'):
            params = {
                'client_id' : client_id,
                'response_type' : 'code',
                'scope' : 'activity heartrate location nutrition profile settings sleep social weight',
                'redirect_uri' : 'https://riski.business/fitbit-callback'
            }
            url = 'https://www.fitbit.com/oauth2/authorize?'
            raise cherrypy.HTTPRedirect(url + urllib.parse.urlencode(params))
        
        ##################################################################
        # Callback from fitbit servers after user has given consent.     #
        ##################################################################
        
        # To do :  scope checks.
        
        if(var == 'fitbit-callback'):
            request_params = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri' : 'https://riski.business/fitbit-callback',
                'client_id': client_id,
            }
            url = 'https://api.fitbit.com/oauth2/token'
            try:
                cres = (client_id + ":" + client_secret).encode()
                headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + base64.b64encode(cres).decode()}
                request = Request(url, urllib.parse.urlencode(request_params).encode(), headers=headers)
                response = json.loads(urlopen(request).read().decode())
                
                response['datetime'] = datetime.now()
                dbresponse = dbhandler.addTokens(response)
                return dbresponse
               
            except urllib.error.HTTPError as e:
                return err.fail(str(e.code))
            except urllib.error.URLError as e:
                return err.fail(str(e.code))
    
    
    ##################################################################
    # End points for requests                                        #
    ##################################################################
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def POST(self, var = None):
          
        # End point to get sleep data for one day.
        # To do : Request data for day range.
        if(var == 'sleep'):
            
            data = json.loads(cherrypy.request.body.read().decode('utf-8'))
            if('user_id' not in data and 'datetime' not in data):
                err.fail()

            return dbhandler.getSleep(data)
               
        # End point to get heartrate data for one day.
        # To do : Request data for day range.
        if(var == 'heartrate'):
            
            data = json.loads(cherrypy.request.body.read().decode('utf-8'))
            
            if('user_id' not in data and 'datetime' not in data):
                err.fail()
            if(data.get('detailed', False)):
                return dbhandler.getHrDetailed(data)
            return dbhandler.getHr(data)
        
        # End point to input eyetracker data to database.
        if(var == 'eyetrack'):
            try:
                data = json.loads(cherrypy.request.body.read().decode('utf-8'))
                print(data)
                # check if data is valid...
                
                return dbhandler.addTrackerdata(data)
            
            except Exception as e:
                return err.fail(str(e))
            
        if(var == 'get-eyetrack'):
            try:
                data = json.loads(cherrypy.request.body.read().decode('utf-8'))
                
                if('user_id' not in data and 'datetime' not in data):
                    err.fail()
                    
                return dbhandler.getTrackerdata(data)
            
            except Exception as e:
                print(e)
                return err.fail(str(e))

            
        
    # End point to get access token for DEVELOPMENT PUPROSE ONLY!
    # SOS STOP SEIS SECURITY RISK - WILL BE REMOVED WHEN NOT NEEDED!
        if(var == 'access_token'):
            data = json.loads(cherrypy.request.body.read().decode('utf-8'))
            print(data)
            if('user_id' not in data):
                err.fail()
            
            return dbhandler.getAccesstoken(data)

            
            
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        },
        '/favicon.ico':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(current_dir, 'favicon.ico'),
            }
    }

    cherrypy.config.update(
        {'server.socket_host': '0.0.0.0', 'server.socket_port': 1337, })
    cherrypy.quickstart(omfg(), '/', conf)