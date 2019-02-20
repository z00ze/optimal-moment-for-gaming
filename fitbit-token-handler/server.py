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

import dbhandler

# CREDENTIALS
credentials = open('credentials-fitbitapp.data', 'r').read().split('\n')
client_id = credentials[0]
client_secret = credentials[1]


@cherrypy.expose
class omfg(object):
        
    def GET(self):
        return open('index.html')

    @cherrypy.expose
    def GET(self, var = None, code = ''):
        global client_id
        global client_secret
        
        #
        # Get permission for data
        # 
        
        if(var == 'getData'):
            params = {
                'client_id' : client_id,
                'response_type' : 'code',
                'scope' : 'activity heartrate location nutrition profile settings sleep social weight',
                'redirect_uri' : 'https://riski.business/fitbit-callback'
            }
            url = 'https://www.fitbit.com/oauth2/authorize?'
            raise cherrypy.HTTPRedirect(url + urllib.parse.urlencode(params))
        
        #
        # Callback
        #
        
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
                print(response)
                
                # DATE RANGE
                startdate = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
                enddate = datetime.today().strftime('%Y-%m-%d')
                
                # SLEEP
                url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/'+ enddate +'.json'
                httpreq = Request(url=url)
                httpreq.add_header('Authorization', 'Bearer ' + response['access_token'])
                access_token = response['access_token']
                sleep = urllib.request.urlopen(httpreq).read()
                
                # HEART RATE
                url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + startdate + '/'+ enddate +'.json'
                httpreq = Request(url=url)
                httpreq.add_header('Authorization', 'Bearer ' + response['access_token'])
                access_token = response['access_token']
                heartrate = urllib.request.urlopen(httpreq).read()

                return '''
                        <html>
                            <head>
                                <script type="text/javascript">
                                console.log({response});
                                console.log({heartrate})
                                </script>
                            </head>
                            <body>
                            {token}
                            </body>
                        </html>
                '''.format(response=sleep.decode(), heartrate=heartrate.decode(), token=access_token)
            
            except urllib.error.HTTPError as e:
                return str(e.code)
            except urllib.error.URLError as e:
                return str(e.code)
            

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
        #'/scripts': {'tools.staticdir.on': True,
        #            'tools.staticdir.dir': os.path.join(current_dir, 'scripts')},
        #'/icons': {'tools.staticdir.on': True,
        #              'tools.staticdir.dir': os.path.join(current_dir, 'icons')},
        #'/styles': {'tools.staticdir.on': True,
        #            'tools.staticdir.dir': os.path.join(current_dir, 'styles')},

    }

    cherrypy.config.update(
        {'server.socket_host': '0.0.0.0', 'server.socket_port': 1337, })
    cherrypy.quickstart(omfg(), '/', conf)