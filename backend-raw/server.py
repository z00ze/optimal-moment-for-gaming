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
import mysql.connector
import dbhandler
# DEMONHANDLER
import demonhandler
# ERROR HANDLER
import errorhandler as err
# FUNCTIONS
import functions

# CREDENTIALS
credentials = open('credentials-fitbitapp.data', 'r').read().split('\n')
client_id = credentials[0]
client_secret = credentials[1]

credentials_db = open('credentials-db.data', 'r').read().split('\n')
user = credentials_db[0]
password = credentials_db[1]


@cherrypy.expose
class omfg(object):
        
    def GET(self):
        return open('index.html')
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def GET(self, var = None, code = '', user_id = None, date_time = None, time_from = None, time_to = None, interval = None):
        
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
            
            cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
            cursor = cnx.cursor(buffered=True)
            
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
                dbresponse = dbhandler.addTokens(response, cnx, cursor)
                cursor.close()
                cnx.close()
                return dbresponse
               
            except urllib.error.HTTPError as e:
                return err.fail(str(e.code))
            except urllib.error.URLError as e:
                return err.fail(str(e.code))
            
        
        if(var == 'eyetrack' and user_id is not None and date_time is not None):
            cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
            cursor = cnx.cursor(buffered=True)
            try:
                params = cherrypy.request.params
                data = { "user_id": params.get("user_id"), "datetime": params.get("date_time")}
                returni = dbhandler.getTrackerdata(data, cnx, cursor)
                return returni
            
            except Exception as e:
                return err.fail(str(e))
        
        if(var == 'processed' and user_id is not None and time_from is not None and time_to is not None and interval is not None):
            
            cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
            cursor = cnx.cursor(buffered=True)
            try:
                returni = dbhandler.getProcessed(user_id, time_from, time_to, interval, cnx, cursor)
                return returni
            except Exception as e:
                    return err.fail(str(e))
        
    ##################################################################
    # End points for requests                                        #
    ##################################################################
    
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def POST(self, var = None):
        
        # end point for eyetrack to send data
        if(var == 'eyetrack'):
            try:
                cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
                cursor = cnx.cursor(buffered=True)
                
                data = json.loads(cherrypy.request.body.read().decode('utf-8'))
                print(data)
                
                # to do : check if data is valid...
                returni = dbhandler.addTrackerdata(data, cnx, cursor)
                cursor.close()
                cnx.close()
                return returni
            
            except Exception as e:
                return err.fail(str(e))
            
        # end point for benchmark to send data
        if(var == 'benchmark'):
            try:
                
                cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
                cursor = cnx.cursor(buffered=True)
                
                data = json.loads(cherrypy.request.body.read().decode('utf-8'))
                print(data)
                
                returni = dbhandler.addBenchmark(data, cnx, cursor)
                cursor.close()
                cnx.close()
                return returni
                
            except Exception as e:
                return err.fail(str(e))
        
    # End point to get access token for DEVELOPMENT PUPROSE ONLY!
    # SOS STOP SEIS SECURITY RISK - WILL BE REMOVED WHEN NOT NEEDED!
    
        if(var == 'access_token'):
            cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
            cursor = cnx.cursor(buffered=True)
            data = json.loads(cherrypy.request.body.read().decode('utf-8'))

            if('user_id' not in data):
                err.fail()
            returni = dbhandler.getAccesstoken(data, cnx, cursor)
            cursor.close()
            cnx.close()
            
            return returni
        
    # End point to get access token for DEVELOPMENT PUPROSE ONLY!
    # SOS STOP SEIS SECURITY RISK - WILL BE REMOVED WHEN NOT NEEDED!
            
            

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