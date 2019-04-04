#!/usr/bin/env python
#coding=utf-8

##################################################################
# ERROR REPORTING                                                #
##################################################################

debug = True

def fail(error=""):
    fail = { "success" : False}
    if(len(error) > 0):
        fail["error"] = error
    if(debug):
        print(fail)
    return fail