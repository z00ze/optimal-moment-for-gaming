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

"""
I - Fetch raw data from yesterday
        sleep_data
        hr_data
    
II - process sleep_data
    1. Define sleep_events (waking up, going to sleep + predicted end time when dynamic eff drops to zero)
    2. Generate user's data_entries & update part of old DB rows 
    
        2.1. Take first_time_entry from 1st sleep_event.end_time last_time_entry from last sleep_event.end_time
        2.2. Get rows from DB where datetime >= first_time_entry and predict, add to user's data_entries as DataEntry objects
        2.3. Generate data_entries for yesterday, add to user's data_entries
            2.3.1. Generate data_entries from last entry in user's data_entries
                (if got from database, else start from yesterday 00:00)
                to last_time_entry.end_time (rows to be predicted) 
    
        2.4. Update DB rows predict to False for rows where datetime < first_time_entry

    3. Define
        previous_sleep_event = sleep_events[0]
        user_data_entry_idx = 0
        default_hours_to_zero_eff = CONF.DEFAULT_HOURS_TO_ZERO_EFF
        dynamic_eff = None
    
    4 Iterate sleep_events from 1-n        
        4.1. Define
            sleep_eff = int(previous_sleep_event.efficiency)    | int / None
            sleeping = previous_sleep_event.sleeping            | True / False    
            main_sleep = previous_sleep_event.main_sleep        | True / False 
            predict = sleep_event.predict                       | True / False
            event_end_time = sleep_event.end_time

        4.2. Define dynamic_eff_change with help of sleep_event & previous_sleep_event
            IF sleeping:
                IF main sleep:
                    dynamic_eff rises all the way to sleep_event.eff
                ELSE:
                    dynamic_eff rises up to average value of current dynamic_eff and current_sleep_event.efficiency
            ELSE
                dynamic eff is decreased for default_hours_to_zero_eff time until zero

            dynamic_eff_change = eff_difference / event_duration / 3600 * eff_change_direction

        4.3. Iterate user's time_entries
            WHILE(TRUE):
                IF user_time_entries[user_data_entry_index] < event_end_time:
                    time_entry.sleep_eff = sleep_eff        | int / None
                    time_entry.dynamic_eff = dynamic_eff    | int / None
                    time_entry.sleeping = sleeping          | True / False
                    time_entry.main_sleep = main_sleep      | True / False
                    time_entry.predict = predict      | True / False

                    IF dynamic_eff:
                        dynamic_eff += dynamic_eff_change
                    
                    user_data_entry_index++

                ELSE
                    break
        
        4.3.1. Define
            IF NOT dynamic_eff:
                set dynamic eff to sleep_event.efficiency after first_sleep event
            
            previous_sleep_event = sleep_event


III - process hr_data

IV - uodate DB procesesed table
"""

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
    """NOTE: should omfg value and benchmark data be calculated separately?"""

    # I - Fetch raw data from yesterday
    #   sleep_data
    #   hr_data

    yesterday_date = "2019-04-11" # TODO: replace with: datetime.strftime(datetime.now()-timedelta(days=1), CONF.DATABASE_DATE_FORMAT)
    sleep_data = dbhandler.get_sleep_data_by_date(user.id, yesterday_date)
    hr_data =  dbhandler.get_hr_data_by_date(user.id, yesterday_date)

    # II - process sleep_data
    process_sleep_data(user, sleep_data)

    # III - process hr_data
    process_hr_data(user, hr_data, yesterday_date)    

    # datetime = "2019-02-28"
    # eye_data = dbhandler.get_eye_tracker_data_by_date(user.id, datetime)
    # log(f"eye_data:{eye_data}")

    # IV - update DB    
    dbhandler.update_processed_entries(user.id, user.data_entries)

    

@log_func
def process_sleep_data(user, raw_sleep_data):

    # 1. Define sleep_events 
    # (waking up, going to sleep + predicted end time when dynamic eff drops to zero)
    sleep_list = raw_sleep_data[CONF.DATABASE_RESULT_DATA_KEY]
    sleep_events = get_sleep_events(sleep_list)

    # 2. Generate user's data_entries & update part of old DB rows
    first_time_entry = generate_user_data_entries(user, sleep_events)
    
    # 2.4. Update DB rows predict to False for rows where datetime < first_time_entry
    dbhandler.confirm_predicted_values_before_time(user.id, first_time_entry)

    # 3. Define
    #   previous_sleep_event = sleep_events[0]
    #   user_data_entry_idx = 0
    #   default_hours_to_zero_eff = CONF.DEFAULT_HOURS_TO_ZERO_EFF

    previous_sleep_event = sleep_events[0]
    user_data_entry_idx = 0
    dynamic_eff = None

    max_user_data_index = len(user.data_entries) # for logging info

    
    
    # 4 Iterate sleep_events from 1 to n    
    for sleep_event in sleep_events[1:]:
        log(f"\nPrevious_sleep_event: {previous_sleep_event.__dict__}")
        log(f"Current sleep_event: {sleep_event.__dict__}")


        # 4.1. Define
        #   sleep_eff = int(previous_sleep_event.efficiency)    | int / None
        #   dynamic_eff = current_user_data_entry.dynamic_eff   | int / None
        #   sleeping = previous_sleep_event.sleeping            | True / False    
        #   main_sleep = previous_sleep_event.main_sleep        | True / False
        #   predict = sleep_event.predict                       | True / False        
        #   event_end_time = sleep_event.end_time               | datetime 

        current_user_data_entry = user.data_entries[user_data_entry_idx]

        sleep_eff = int(previous_sleep_event.efficiency) if previous_sleep_event.efficiency else None
        sleeping = sleep_event.sleeping
        main_sleep = sleep_event.main_sleep
        predict = sleep_event.predict
        event_end_time = sleep_event.end_time

        # 4.2. Define dynamic_eff_change with help of sleep_event & previous_sleep_event
        dynamic_eff_change = get_dynamic_eff_change(sleep_event, previous_sleep_event, dynamic_eff) if dynamic_eff else None

        # 4.3. Iterate user's time_entries
        while(True):
            user_entry = user.data_entries[user_data_entry_idx]
            # log(f"user_entry's datetime: {user_entry.datetime}")
            
            if(user_entry.datetime <= event_end_time):
                user_entry.set_sleep_eff(sleep_eff)
                user_entry.set_dynamic_eff(int(round(dynamic_eff)) if dynamic_eff else None)
                user_entry.set_sleeping(sleeping)
                user_entry.set_main_sleep(main_sleep)
                user_entry.set_predict(predict)

                if(dynamic_eff):
                    dynamic_eff += dynamic_eff_change
                
                user_data_entry_idx += 1

                if(user_data_entry_idx == len(user.data_entries)):
                    log("last user data entry processed, breaking the loop")
                    break
            else:
                log(f"user_entry.datetime:{user_entry.datetime} >= event_end_time: {event_end_time}. Continuing to next one")                
                break
        
        # 4.3.1.
        # If first sleeping_event was user's first one, setting dynamic eff to sleep eff when waking up
        if(not dynamic_eff):            
            dynamic_eff = sleep_event.efficiency
            log(f"setting dybamic_eff to {dynamic_eff} after first sleep_event")
        
        log(f"user_data_entry_idx: {user_data_entry_idx} / {max_user_data_index}")
        log(f"last updated user data entry: {user.data_entries[user_data_entry_idx-1].__dict__}")
        
        previous_sleep_event = sleep_event

@log_func
def get_sleep_events(sleep_list):
    """ Every event marks an end to previous action. 
    
    Therefore term end_time is used in SleepEvent
    """
    
    sleep_events = []
    latest_end_time = None
    efficiency = None

    for sleep_values in sleep_list:
        
        # Adding entry for first event: going to sleep.
        going_to_sleep_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.START_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )
        sleep_events.append(
            SleepEvent(going_to_sleep_time, False, efficiency, False, False)
        )

        # boolean must be evaluated from raw data result
        main_sleep = ast.literal_eval(sleep_values[CONF.SLEEP_DATA_KEYS.MAIN_SLEEP])
        
        # Adding entry for second event: waking up.
        waking_up_time = datetime.strptime(
            sleep_values[CONF.SLEEP_DATA_KEYS.END_TIME].split(".")[0],
            CONF.SLEEP_DATA_DATE_FORMAT
            )
        efficiency = sleep_values[CONF.SLEEP_DATA_KEYS.EFFICIENCY]         
        sleep_events.append(
            SleepEvent(waking_up_time, True, efficiency, main_sleep, False)
        )

        latest_end_time = waking_up_time
    
    # Adding last sleep event for predicted values
    predicted_end_time = latest_end_time + timedelta(hours = CONF.DEFAULT_HOURS_TO_ZERO_EFF)
    log(f"generated predicted_end_time: {predicted_end_time} from latest_end_time: {latest_end_time} by adding default_hours_to_zero_eff: {CONF.DEFAULT_HOURS_TO_ZERO_EFF}")    
    sleep_events.append(
        SleepEvent(predicted_end_time, False, efficiency, False, True)
    )
 
    log("Generated sleep events:")
    for event in sleep_events:
        log(event.__dict__)
    
    return sleep_events

@log_func
def generate_user_data_entries(user, sleep_events):
    log(f"got user with id:{user.id}") #" and token: {user.token}")

    user_data_entries = []

    # 2.1. Take first_time_entry from 1st sleep_event.end_time 
    #  last_time_entry from last sleep_event.end_time
    first_time_entry = sleep_events[0].end_time
    last_time_entry = sleep_events[len(sleep_events)-1].end_time
    log(f"Got first_time_entry: {first_time_entry} & last_time_entry: {last_time_entry}")

    # 2.2. Get rows from DB where datetime >= first_time_entry and predict, 
    # add to user's data_entries as DataEntry objects
    predicted_query_result = dbhandler.get_predicted_data_entries(user.id, first_time_entry)
    if(predicted_query_result[CONF.DATABASE_RESULT_SUCCESS_KEY]):
        predicted_data_entries = predicted_query_result[CONF.DATABASE_RESULT_DATA_KEY]
        log(f"got {len(predicted_data_entries)} predicted_data_entries.")
        user_data_entries = generate_data_entries_from_predicted_results(predicted_data_entries)        
    else:
        log("got no predicted_data_entries.")
    
    # 2.3. Generate data_entries for yesterday, add to user's data_entries
    yesterday_data_entries = get_yesterday_data_entries(user_data_entries, last_time_entry)    
    user_data_entries.extend(yesterday_data_entries)
    user.set_data_entries(user_data_entries)
    
    log(f"user.data_entries updated with {len(user_data_entries)} values.")

    return first_time_entry

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
def get_yesterday_data_entries(user_data_entries, datetime_to):
    # 2.3.1. Generate data_entries from last entry in user's data_entries
    # (if got from database, else start from yesterday 00:00) 
    # to last_time_entry.end_time (rows to be predicted)    
    datetime_from = None
    if(len(user_data_entries) > 0):
        datetime_from = user_data_entries[len(user_data_entries)-1].datetime
    else:
        today = datetime(2019, 4, 12) # TODO: replace with: datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        datetime_from = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    time_interval = CONF.PROCESSOR_TIME_INTERVAL
    log(f"generating DataEntries from {datetime_from} to {datetime_to} with time interval of {time_interval} seconds.")
    
    data_entries = []
    while datetime_from < datetime_to:
        data_entries.append(DataEntry(datetime_from))
        datetime_from += timedelta(seconds=time_interval)

    log(f"created {len(data_entries)} data entries")
    return data_entries

@log_func
def get_dynamic_eff_change(current_sleep_event, previous_sleep_event, dynamic_eff):

    eff_difference = None

    if(not current_sleep_event.sleeping):
        log(f"#### not sleeping, eff is decreacing ####")
        eff_change_direction = -1
        eff_difference = dynamic_eff
        event_duration = CONF.DEFAULT_HOURS_TO_ZERO_EFF
        log(f"effciency is decreasing, setting eff_change_direction to {eff_change_direction}, eff_difference to {eff_difference} and event_duration to default {CONF.DEFAULT_HOURS_TO_ZERO_EFF} hours")
            
    else:
        log("#### sleeping, eff is increasing ####")
        eff_change_direction = 1
        
        if(current_sleep_event.main_sleep):
            log(f"current_sleep_event.main_sleep == True")
            eff_difference = (current_sleep_event.efficiency - dynamic_eff)
        else:
            log("current_sleep_event.main_sleep == False, dynamic_eff is increasing up to average value of current dynamic_eff and current_sleep_event.efficiency")            
            wanted_result = (dynamic_eff + current_sleep_event.efficiency) / 2
            log(f"current dynamic_eff: {dynamic_eff} - current_sleep_event.efficiency: {current_sleep_event.efficiency} / 2 = {wanted_result}")
            eff_difference = wanted_result - dynamic_eff
            log(f"eff_difference: {eff_difference}")
            

        event_duration = (current_sleep_event.end_time - previous_sleep_event.end_time).total_seconds() / 3600            
        log(f"event_duration: {event_duration} hours")

    log(f"eff_difference: {eff_difference}")
    dynamic_eff_change = eff_difference / event_duration / 3600 * eff_change_direction

    log(f"dynamic_eff_change: {dynamic_eff_change}")
    return dynamic_eff_change


@log_func
def process_hr_data(user, hr_data, yesterday_date):
    """ NOTE: making assumption that hr data is already sorted! """

    hr_time_entries = hr_data[CONF.DATABASE_RESULT_DATA_KEY][CONF.HR_DATA_KEYS.DATASET]
    yesterday_date = datetime.strptime(yesterday_date, "%Y-%m-%d")    

    user_data_entry_idx = 0
    for hr_index, hr_entry in enumerate(hr_time_entries):
        # log(f"hr_entry: {hr_entry}")
        hr_time = datetime.strptime(hr_entry[CONF.HR_DATA_KEYS.TIME], "%H:%M:%S").time()
        hr_value = hr_entry[CONF.HR_DATA_KEYS.VALUE]       
        
        while(True):
            user_data_entry = user.data_entries[user_data_entry_idx]
            data_entry_datetime = user_data_entry.datetime
            # log(f"data_entry_datetime: {data_entry_datetime}")
            if(data_entry_datetime < yesterday_date):
                # log(f"data_entry_datetime: {data_entry_datetime} < yesterday_date: {yesterday_date}")
                user_data_entry_idx += 1
                continue               
            
            data_entry_time = data_entry_datetime.time()
            # log(f"data_entry_time: {data_entry_time} vs hr_time: {hr_time}")
            user_data_entry_idx += 1

            if(data_entry_time == hr_time):
                # log("procdata_entry_timeessor_time == hr_time")
                # log(f"setting data_entry_time's hr to {hr_value}")
                user_data_entry.hr_value = hr_value
                break
            else:
                user_data_entry.hr_value = None


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