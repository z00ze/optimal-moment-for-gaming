#!/usr/bin/env python
#coding=utf-8

import time
import dbhandler
from config import Config
from datetime import datetime, timedelta

##################################################################
# Runs different tasks once in a hour.                           #
##################################################################
CONF = Config()
LOGGING = True

def log(msg):
    if(LOGGING):
        print(msg)

current_date = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def log_func(func):
    def wrapper(*args, **kwargs):
        if(LOGGING):
            log(f"### {func.__name__} ###")

        return func(*args, **kwargs)
    return wrapper

class User:
    def __init__(self, user_dict):
        self.id = user_dict[CONF.GET_USERS_KEYS.USER_ID_KEY]
        self.token = user_dict[CONF.GET_USERS_KEYS.ACCESS_TOKEN_KEY]

        

@log_func
def get_users():    
    result = dbhandler.get_users()       
    users = result[CONF.GET_USERS_KEYS.USERS]    
    return users

@log_func
def process_user_data(user):
    log(f"got user with id:{user.id} and token: {user.token}")
    datetime = "2019-03-25"
    sleep_data = dbhandler.get_sleep_data_by_date(user.id, datetime)
    # log(f"sleep_data:{sleep_data}")

    datetime = "2019-03-27"
    hr_data = dbhandler.get_hr_data_by_date(user.id, datetime)
    # log(f"hr_data:{hr_data}")

    datetime = "2019-02-28"
    eye_data = dbhandler.get_eye_tracker_data_by_date(user.id, datetime)
    log(f"eye_data:{eye_data}")
    


for entry in get_users():    
    process_user_data(User(entry))
    


# while(True):
#     log("Awoken!")
    
#     # Refreshes access tokens which are about to get old.
#     demonhandler.refreshTokens()

#     # Fetches data for each user.
#     demonhandler.fetchData()
    
#     log("Sleepings...")
#     time.sleep(3600)