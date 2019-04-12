import json
class Config:
    def __init__(self):
        config = json.loads(open('config.json', 'r').read())
        self.PROCESSOR_TIME_INTERVAL = config["PROCESSOR_TIME_INTERVAL"]
        self.DEFAULT_HOURS_TO_ZERO_EFF = config["DEFAULT_HOURS_TO_ZERO_EFF"]
        self.SLEEP_DATA_DATE_FORMAT = config["SLEEP_DATA_DATE_FORMAT"]
        self.DATABASE_DATE_FORMAT = config["DATABASE_DATE_FORMAT"]
        self.DATABASE_RESULT_DATA_KEY = config["DATABASE_RESULT_DATA_KEY"]
        self.DATABASE_RESULT_SUCCESS_KEY = config["DATABASE_RESULT_SUCCESS_KEY"]

        self.GET_USERS_KEYS = Users(config["GET_USERS"])
        self.HR_DATA_KEYS = HrData(config["HR_DATA"])
        self.SLEEP_DATA_KEYS = SleepData(config["SLEEP_DATA"])        
        self.DATABASE_RESULT_INDEXES = DataBaseResultIndexes(config["DATABASE_RESULT_COLUMN_INDEXES"])

class SleepData:
    def __init__(self, sleep_data_dict):        
        self.MAIN_SLEEP = sleep_data_dict["MAIN_SLEEP_KEY"]
        self.START_TIME = sleep_data_dict["START_TIME_KEY"]
        self.END_TIME = sleep_data_dict["END_TIME_KEY"]
        self.EFFICIENCY = sleep_data_dict["EFFICIENCY_KEY"]        

class HrData:
    def __init__(self, hr_data_dict):        
        self.DATASET = hr_data_dict["DATASET_KEY"]
        self.TIME = hr_data_dict["TIME_KEY"]
        self.VALUE = hr_data_dict["VALUE_KEY"]

class Users:
    def __init__(self, user_dict):
        self.USERS = user_dict["USERS_KEY"]
        self.USER_ID_KEY = user_dict["USER_ID_KEY"]
        self.ACCESS_TOKEN_KEY = user_dict["ACCESS_TOKEN_KEY"]

class DataBaseResultIndexes:
    def __init__(self, result_dict):        
        self.UNIQUE_ID = result_dict["UNIQUE_ID"]
        self.USER_ID = result_dict["USER_ID"]
        self.DATETIME = result_dict["DATETIME"]
        self.SLEEP_EFF = result_dict["SLEEP_EFF"]
        self.SLEEPING = result_dict["SLEEPING"]
        self.MAIN_SLEEP = result_dict["MAIN_SLEEP"]
        self.HR_VALUE = result_dict["HR_VALUE"]
        self.EYETRACK = result_dict["EYETRACK"]
        self.DYNAMIC_EFF = result_dict["DYNAMIC_EFF"]
        self.OMFG = result_dict["OMFG"]
        self.PREDICT = result_dict["PREDICT"]