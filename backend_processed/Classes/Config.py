import json
class Config:
    def __init__(self):
        config = json.loads(open('config.json', 'r').read())
        self.PROCESSOR_TIME_INTERVAL = config["PROCESSOR_TIME_INTERVAL"]
        self.DEFAULT_HOURS_TO_ZERO_EFF = config["DEFAULT_HOURS_TO_ZERO_EFF"]
        self.SLEEP_DATA_DATE_FORMAT = config["SLEEP_DATA_DATE_FORMAT"]
        self.GET_USERS_KEYS = Users(config["GET_USERS"])
        self.HR_DATA_KEYS = HrData(config["HR_DATA"])
        self.SLEEP_DATA_KEYS = SleepData(config["SLEEP_DATA"])
        

class SleepData:
    def __init__(self, sleep_data_dict):
        self.DATA = sleep_data_dict["DATA_KEY"]
        self.MAIN_SLEEP = sleep_data_dict["MAIN_SLEEP_KEY"]
        self.START_TIME = sleep_data_dict["START_TIME_KEY"]
        self.END_TIME = sleep_data_dict["END_TIME_KEY"]
        self.EFFICIENCY = sleep_data_dict["EFFICIENCY_KEY"]        

class HrData:
    def __init__(self, hr_data_dict):
        self.DATA = hr_data_dict["DATA_KEY"]
        self.DATASET = hr_data_dict["DATASET_KEY"]
        self.TIME = hr_data_dict["TIME_KEY"]
        self.VALUE = hr_data_dict["VALUE_KEY"]

class Users:
    def __init__(self, user_dict):
        self.USERS = user_dict["USERS_KEY"]
        self.USER_ID_KEY = user_dict["USER_ID_KEY"]
        self.ACCESS_TOKEN_KEY = user_dict["ACCESS_TOKEN_KEY"]