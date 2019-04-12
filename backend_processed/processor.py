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
from Classes.SleepEvent import SleepEvent

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
        result =  func(*args, **kwargs)        
        if(LOGGING):
            log(f"### RETURNING FROM {func.__name__} ###\n")
        return result
    return wrapper        

@log_func
def get_users():    
    result = dbhandler.get_users()     

    users = result[CONF.GET_USERS_KEYS.USERS]    
    return users

@log_func
def process_user_data(user):
    """
    TODO:
        I - process sleep
            1) fetch previous unpredicted data
                1.1 - if query results None - create entries older entries            
            2) add yesterday entries to previous data
            3) process sleep data
                4.1 - update previous data
                4.2 - continue with yesterdays data
                4.3 - generate today's predicted data
        
        II - process HR data
            4) process hr data

        III - eye tracker etc
            
            5) eye tracker -data ? 
            6) benchmark data ? 
            7) omfg - value ? 
    NOTE: should omfg value and benchmark data be calculated separately?"""

    # 1-2
    set_user_data_entries(user)
    
    # 3
    yesterday_date = datetime.strftime(datetime.now()-timedelta(days=1), CONF.DATABASE_DATE_FORMAT)
    sleep_data = dbhandler.get_sleep_data_by_date(user.id, yesterday_date)
    process_sleep_data(user, sleep_data)

    hr_data =  dbhandler.get_hr_data_by_date(user.id, yesterday_date)        
    process_hr_data(user, hr_data) 
    # # log(f"hr_data:{hr_data}")

    # datetime = "2019-02-28"
    # eye_data = dbhandler.get_eye_tracker_data_by_date(user.id, datetime)
    # log(f"eye_data:{eye_data}")

    # for test validation
    hr_values = 0
    for entry in user.data_entries:
        try:
            test = entry.hr_value
            hr_values += 1
        except:
            break   
    
    log(f"got {hr_values} updated hr entries")
 
@log_func
def set_user_data_entries(user):
    log(f"got user with id:{user.id} and token: {user.token}")
    user_data_entries = []

    predicted_query_result = dbhandler.get_predicted_data_entries(user.id)
    predicted_data_entries = []

    if(predicted_query_result[CONF.DATABASE_RESULT_SUCCESS_KEY]):
        predicted_data_entries = predicted_query_result[CONF.DATABASE_RESULT_DATA_KEY]
        log(f"got {len(predicted_data_entries)} predicted_data_entries.")
        user_data_entries = generate_data_entries_from_predicted_results(predicted_data_entries)        
    else:
        log("got no predicted_data_entries.")
    user_data_entries.extend(get_yesterday_data_entries())
    user.set_data_entries(user_data_entries)

@log_func
def generate_data_entries_from_predicted_results(predicted_data_entries):
    result_list = []

    for entry in predicted_data_entries:               
        
        data_entry = DataEntry(
            entry[CONF.DATABASE_RESULT_INDEXES.DATETIME],
            unique_id = entry[CONF.DATABASE_RESULT_INDEXES.UNIQUE_ID],
            sleep_eff = entry[CONF.DATABASE_RESULT_INDEXES.SLEEP_EFF],            
            sleeping = entry[CONF.DATABASE_RESULT_INDEXES.SLEEPING],
            main_sleep = entry[CONF.DATABASE_RESULT_INDEXES.MAIN_SLEEP],
            hr_value = entry[CONF.DATABASE_RESULT_INDEXES.HR_VALUE],
            eye_data = entry[CONF.DATABASE_RESULT_INDEXES.EYETRACK],            
            dynamic_eff = entry[CONF.DATABASE_RESULT_INDEXES.DYNAMIC_EFF],
            omfg = entry[CONF.DATABASE_RESULT_INDEXES.OMFG],
            predict = entry[CONF.DATABASE_RESULT_INDEXES.PREDICT]
        )
        result_list.append(data_entry)

    log(f"generated {len(result_list)} data entries from predicted results")
    return result_list
       
    
@log_func
def get_yesterday_data_entries():   
    time_interval = CONF.PROCESSOR_TIME_INTERVAL

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    log(f"generating DataEntries from {yesterday} to {today} with time interval of {time_interval} seconds.")
    
    data_entries = []
    while yesterday < today:
        data_entries.append(DataEntry(yesterday))
        yesterday += timedelta(seconds=time_interval)

    log(f"created {len(data_entries)} data entries")
    return data_entries

@log_func
def get_sleep_events(sleep_list):

    sleep_events = []

    for sleep_values in sleep_list:
        
        # Adding entry for first event: going to sleep.
        going_to_sleep_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.START_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )
        sleep_events.append(
            SleepEvent(going_to_sleep_time, False, None, False)
        )

        main_sleep = sleep_values[CONF.SLEEP_DATA_KEYS.MAIN_SLEEP]        
        
        # Adding entry for second event: waking up.
        waking_up_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.END_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )
        efficiency = sleep_values[CONF.SLEEP_DATA_KEYS.EFFICIENCY]         
        sleep_events.append(
            SleepEvent(waking_up_time, True, efficiency, main_sleep)
        )
    
    # Adding last sleep event for predicted values 
    sleep_events.append(
        SleepEvent(None, False, 0, False)
    )
 
    log("Generated sleep events:")
    for event in sleep_events:
        log(event.__dict__)
    
    return sleep_events

@log_func
def get_eff_change_per_sec(previous_sleep_event, current_sleep_event, default_hours_to_zero_eff, end_time):
    
    log(f"Previous_sleep_event: {previous_sleep_event.__dict__}")
    log(f"Current sleep_data: {current_sleep_event.__dict__}")
    predicted_value = False

    if(not current_sleep_event.sleeping):
        log(f"#### not sleeping, eff is decreacing ####")
        eff_change_direction = -1
        if(not current_sleep_event.efficiency):
            log(f"current_sleep_event has no efficiency, starting to decrease from previous_sleep_event.effciency: {previous_sleep_event.efficiency}")
            current_sleep_event.efficiency = previous_sleep_event.efficiency
        
        eff_difference = current_sleep_event.efficiency
        log(f"effciency is decreasing, setting event_duration to default {default_hours_to_zero_eff} hours")
        event_duration = default_hours_to_zero_eff
        if(not current_sleep_event.end_time):
            end_time = previous_sleep_event.end_time + timedelta(hours = default_hours_to_zero_eff)
            predicted_value = True
            log(f"set end_time to {end_time} & predicted value to {predicted_value}")
            
    else:
        log("#### sleeping, eff is increasing ####")
        eff_change_direction = 1
        eff_difference = (current_sleep_event.efficiency - previous_sleep_event.efficiency) * eff_change_direction

        event_duration = (current_sleep_event.end_time - previous_sleep_event.end_time).total_seconds() / 3600            
        log(f"event_duration: {event_duration} hours")

    log(f"eff_difference: {eff_difference}")
    eff_change_per_sec = eff_difference / event_duration / 3600 * eff_change_direction

    log(f"eff_change_per_sec: {eff_change_per_sec}")

    return eff_change_per_sec, end_time, predicted_value

   


@log_func
def process_sleep_data(user, raw_sleep_data):
    sleep_list = raw_sleep_data[CONF.DATABASE_RESULT_DATA_KEY]
    sleep_events = get_sleep_events(sleep_list)
    # TODO: calculate days first efficiency with previous day's values
    # TODO: update old predict values
    
    log("Generating sleep values for user data entries")

    default_hours_to_zero_eff = CONF.DEFAULT_HOURS_TO_ZERO_EFF
    log(f"default_hours_to_zero_eff: {default_hours_to_zero_eff}")

    user_data_index = 0
    max_user_data_index = len(user.data_entries)

    predicted_value = False
    previous_sleep_event = None    
    
    for sleep_event in sleep_events:
        eff_change_per_sec = None
        end_time = sleep_event.end_time

        if(previous_sleep_event):
            eff_change_per_sec, end_time, predicted_value = get_eff_change_per_sec(
                previous_sleep_event, 
                sleep_event, 
                default_hours_to_zero_eff,
                end_time)
        else:
            log("No previous_sleep_event processed, updating old values and fethcing last efficiency value")
            # TODO: implement: update older values, set predict to False and get last efficiency value
            sleep_event.efficiency = 23
            previous_sleep_event = sleep_event

        dynamic_eff = previous_sleep_event.efficiency
        sleep_eff = int(previous_sleep_event.efficiency)
        while(True):
            user_entry = user.data_entries[user_data_index]
            # log(f"user_entry's datetime: {user_entry.datetime}")
            
            if(user_entry.datetime <= end_time):
                user_entry.set_sleep_eff(sleep_eff)
                user_entry.set_dynamic_eff(dynamic_eff)
                #TODO: set_sleeping
                #TODO: set_main_sleep
                #TODO: set_dynamic_eff
                
                
                user_entry.predicted = predicted_value
                # log(f"setting user_entry's , {user_entry.datetime} efficiency to {user_entry.efficiency}")
                dynamic_eff += eff_change_per_sec
                user_data_index += 1
                
                # TODO: how to handle times from day before yesterday? now fails to calculate correct value when starting from midnight         
                if(user_data_index == len(user.data_entries)):
                    log("last user data entry processed, breaking the loop")
                    break
            else:
                log(f"user_entry.datetime:{user_entry.datetime} >= end_time: {end_time}. Continuing to next one")                
                break
        
        log(f"user_data_index: {user_data_index} / {max_user_data_index}")
        log(f"last updated user data entry: {user.data_entries[user_data_index-1].__dict__}")
        
        previous_sleep_event = sleep_event

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
            processor_entry = user.data_entries[processor_index]
            processor_datetime = processor_entry.datetime
            # log(f"processor_datetime: {processor_datetime}")
            processor_time = processor_datetime.time()
            # log(f"processor_time: {processor_time} vs hr_time: {hr_time}")            

            if(processor_time <= hr_time or hr_index == len(hr_time_entries)-1):
                # log("processor_time <= hr_time")
                # log(f"setting processor_entry's hr to {hr_value}")
                processor_entry.hr_value = hr_value
                processor_index +=1
                if(processor_index >= len(user.data_entries)):
                    log(f"processor_index {processor_index} >= len(user.data_entries) : {len(user.data_entries)}")
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