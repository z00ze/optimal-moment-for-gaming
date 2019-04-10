#!/usr/bin/env python
#coding=utf-8

import time
import dbhandler
import json
import ast
import json

from Classes.User import User
from Classes.Config import Config
from Classes.DataEntry import DataEntry
from Classes.SleepData import SleepData

from datetime import datetime, timedelta

##################################################################
# Runs every day after midnight                                  #
##################################################################
LOGGING = True
def log(msg):
    if(LOGGING):
        print(msg)

CONF = Config()
log("#####\n\nCONF:")
for key, value in CONF.__dict__.items():
    try:
        log(f"{key} - {value.__dict__}")
    except:
        log(f"{key} - {value}")
log("\n#####")


def log_func(func):
    def wrapper(*args, **kwargs):
        if(LOGGING):
            log(f"\n### {func.__name__} ###")

        return func(*args, **kwargs)
    return wrapper        

@log_func
def get_users():    
    result = dbhandler.get_users()     

    users = result[CONF.GET_USERS_KEYS.USERS]    
    return users

@log_func
def process_user_data(user):    
    log(f"got user with id:{user.id} and token: {user.token}")
    user.time_entries = get_yesterday_time_entries()

    datetime = "2019-03-27" # TODO: change 
    hr_data =  dbhandler.get_hr_data_by_date(user.id, datetime)        
    process_hr_data(user, hr_data)    

    datetime = "2019-03-25"  # TODO: change 
    sleep_data = dbhandler.get_sleep_data_by_date(user.id, datetime)
    # log(f"sleep_data:{sleep_data}")    
    process_sleep_data(user, sleep_data)

   
    # # log(f"hr_data:{hr_data}")

    # datetime = "2019-02-28"
    # eye_data = dbhandler.get_eye_tracker_data_by_date(user.id, datetime)
    # log(f"eye_data:{eye_data}")

    # for test validation
    hr_values = 0
    for entry in user.time_entries:
        try:
            test = entry.hr_value
            hr_values += 1
        except:
            break   
    
    log(f"got {hr_values} updated hr entries")
 
    
@log_func
def get_yesterday_time_entries():   
    time_interval = CONF.PROCESSOR_TIME_INTERVAL

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    log(f"generating DataEntries from {yesterday} to {today} with time interval of {time_interval} seconds.")
    
    time_entries = []
    while yesterday < today:
        time_entries.append(DataEntry(yesterday))
        yesterday += timedelta(seconds=time_interval)

    log(f"created {len(time_entries)} time entries")
    return time_entries

@log_func
def get_sleep_events(sleep_list):

    sleep_events = []

    for sleep_values in sleep_list:        
        log(sleep_values)
        
        log(sleep_values[CONF.SLEEP_DATA_KEYS.START_TIME])
        
        going_to_sleep_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.START_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )         

        # Adding entry for first event: going to sleep. 
        sleep_events.append(
            SleepData(going_to_sleep_time, False, None, False)
        )

        main_sleep = sleep_values[CONF.SLEEP_DATA_KEYS.MAIN_SLEEP]
        
        #parsing datetime from str data entry
        waking_up_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.END_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )
        efficiency = sleep_values[CONF.SLEEP_DATA_KEYS.EFFICIENCY]

        # Adding entry for second event: waking up. 
        sleep_events.append(
            SleepData(waking_up_time, True, efficiency, main_sleep)
        )
    
    # Adding last sleep event for predicted values 
    sleep_events.append(
        SleepData(None, False, 0, False)
    )
 
    log("Generated sleep events:")
    for event in sleep_events:
        log(event.__dict__)
    
    log("Sleep events updated\n")
    return sleep_events
    

@log_func
def process_sleep_data(user, raw_sleep_data):
    sleep_list = raw_sleep_data[CONF.SLEEP_DATA_KEYS.DATA]
    # log(f"sleep_list: {sleep_list}")

    sleep_events = get_sleep_events(sleep_list)
    # TODO: calculate days first efficiency with previous day's values
    # TODO: update old predict values
    
    log("Generating sleep values for user data entries")
    previous_sleep_event = None

    default_hours_to_zero_eff = CONF.DEFAULT_HOURS_TO_ZERO_EFF
    log(f"default_hours_to_zero_eff: {default_hours_to_zero_eff}")

    user_data_index = 0
    max_user_data_index = len(user.time_entries)

    predicted_value = False
    
    for sleep_data in sleep_events:
        eff_change_per_sec = None
        end_time = sleep_data.end_time
        log(f"\n #### sleep_data with end_time: {end_time} ####")

        if(previous_sleep_event):
            log(f"Previous_sleep_event: {previous_sleep_event.__dict__}")
            log(f"Current sleep_data: {sleep_data.__dict__}")

            if(not sleep_data.sleeping):
                log(f"#### not sleeping, eff is decreacing ####")
                eff_change_direction = -1
                if(not sleep_data.efficiency):
                    log(f"sleep_data has no efficiency, starting to decrease from previous_sleep_event.effciency: {previous_sleep_event.efficiency}")
                    sleep_data.efficiency = previous_sleep_event.efficiency
                
                eff_difference = sleep_data.efficiency
                log(f"effciency is decreasing, setting event_duration to default {default_hours_to_zero_eff} hours")
                event_duration = default_hours_to_zero_eff
                if(not sleep_data.end_time):
                    end_time = previous_sleep_event.end_time + timedelta(hours = default_hours_to_zero_eff)
                    predicted_value = True
                    log(f"set end_time to {end_time} & predicted value to {predicted_value}")
                            
                    
            else:
                log("#### sleeping, eff is increasing ####")
                eff_change_direction = 1
                eff_difference = (sleep_data.efficiency - previous_sleep_event.efficiency) * eff_change_direction

                event_duration = (sleep_data.end_time - previous_sleep_event.end_time).total_seconds() / 3600            
                log(f"event_duration: {event_duration} hours")

            log(f"eff_difference: {eff_difference}")
            eff_change_per_sec = eff_difference / event_duration / 3600 * eff_change_direction

            log(f"eff_change_per_sec: {eff_change_per_sec}")

        else:
            log("No previous_sleep_event processed, updating old values and fethcing last efficiency value")
            # TODO: implement: update older values, set predict to False and get last efficiency value
            sleep_data.efficiency = 23
            previous_sleep_event = sleep_data
    
        while(True):
            user_entry = user.time_entries[user_data_index]
            # log(f"user_entry's datetime: {user_entry.datetime}")
            
            if(user_entry.datetime <= end_time):
                user_entry.efficiency = int(previous_sleep_event.efficiency)
                user_entry.predicted = predicted_value
                # log(f"setting user_entry's , {user_entry.datetime} efficiency to {user_entry.efficiency}")
                previous_sleep_event.efficiency += eff_change_per_sec
                user_data_index += 1
                
                # TODO: how to handle times from day before yesterday? now fails to calculate correct value when starting from midnight         
                if(user_data_index == len(user.time_entries)):
                    log("last user data entry processed, breaking the loop")
                    break
            else:
                log(f"user_entry.datetime:{user_entry.datetime} >= end_time: {end_time}. Continuing to next one")                
                break
        
        log(f"user_data_index: {user_data_index} / {max_user_data_index}")
        log(f"last updated user data entry: {user.time_entries[user_data_index-1].__dict__}")
        
        previous_sleep_event = sleep_data

@log_func
def process_hr_data(user, hr_data):
    """ NOTE: making assumption that hr data is already sorted! """

    hr_time_entries = hr_data[CONF.HR_DATA_KEYS.DATA][CONF.HR_DATA_KEYS.DATASET]    

    processor_index = 0
    for hr_index, hr_entry in enumerate(hr_time_entries):
        # log(f"hr_entry: {hr_entry}")
        hr_time = datetime.strptime(hr_entry[CONF.HR_DATA_KEYS.TIME], "%H:%M:%S").time()
        hr_value = hr_entry[CONF.HR_DATA_KEYS.VALUE]       
        
        while(True):
            processor_entry = user.time_entries[processor_index]
            processor_datetime = processor_entry.datetime
            # log(f"processor_datetime: {processor_datetime}")
            processor_time = processor_datetime.time()
            # log(f"processor_time: {processor_time} vs hr_time: {hr_time}")            

            if(processor_time <= hr_time or hr_index == len(hr_time_entries)-1):
                # log("processor_time <= hr_time")
                # log(f"setting processor_entry's hr to {hr_value}")
                processor_entry.hr_value = hr_value
                processor_index +=1
                if(processor_index >= len(user.time_entries)):
                    log(f"processor_index {processor_index} >= len(user.time_entries) : {len(user.time_entries)}")
                    break
            else:
                # log("processor_time over hr_time!")
                break



for user_dict in get_users():  
    process_user_data(
        User(
            user_dict[CONF.GET_USERS_KEYS.USER_ID_KEY],
            user_dict[CONF.GET_USERS_KEYS.ACCESS_TOKEN_KEY]
            )
        )
    


# while(True):
#     log("Awoken!")
    
#     # Refreshes access tokens which are about to get old.
#     demonhandler.refreshTokens()

#     # Fetches data for each user.
#     demonhandler.fetchData()
    
#     log("Sleepings...")
#     time.sleep(3600)