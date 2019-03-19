#!/usr/bin/env python
#coding=utf-8

import time
import demonhandler

##################################################################
# Runs different tasks once in a hour.                           #
##################################################################

while(True):
    print("Awoken!")
    
    # Refreshes access tokens which are about to get old.
    demonhandler.refreshTokens()


    demonhandler.fetchData()
    
    print("Sleepings...")
    time.sleep(3600)