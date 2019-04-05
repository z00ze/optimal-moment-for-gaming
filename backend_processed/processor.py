#!/usr/bin/env python
#coding=utf-8

import time
import dbhandler
from Classes.Config import Config
from Classes.DataEntry import DataEntry
from datetime import datetime, timedelta

##################################################################
# Runs every day after midnight                                  #
##################################################################
LOGGING = True
def log(msg):
    if(LOGGING):
        print(msg)

CONF = Config()
log(f"#####\n\nCONF:")
for key, value in CONF.__dict__.items():
    try:
        log(f"{key} - {value.__dict__}")
    except:
        log(f"{key} - {value}")
log("\n#####")

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
    time_entries = get_processed_time_entries()
    log(f"got user with id:{user.id} and token: {user.token}")
    datetime = "2019-03-25"
    sleep_data = dbhandler.get_sleep_data_by_date(user.id, datetime)
    # log(f"sleep_data:{sleep_data}")

    datetime = "2019-03-27"
    hr_data = dbhandler.get_hr_data_by_date(user.id, datetime)
    process_hr_data(hr_data)
    # log(f"hr_data:{hr_data}")

    datetime = "2019-02-28"
    eye_data = dbhandler.get_eye_tracker_data_by_date(user.id, datetime)
    # log(f"eye_data:{eye_data}")
    
@log_func
def get_processed_time_entries():   
    time_interval = CONF.PROCESSOR_TIME_INTERVAL

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    log(f"generating DataEntries from {yesterday} to {today} with time interval of {time_interval} seconds.")
    
    time_entries = []
    while yesterday < today:
        time_entries.append(DataEntry(yesterday))
        yesterday += timedelta(seconds=time_interval)

    log(f"created {len(time_entries)} time entries")
    teststop


@log_func
def process_hr_data(hr_data):
    """ NOTE: making assumption that hr data is already sorted! """

    hr_time_entries = hr_data[CONF.HR_DATA_KEYS.DATA][CONF.HR_DATA_KEYS.DATASET]
    for entry in hr_time_entries:
        log(entry)
        teststop



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