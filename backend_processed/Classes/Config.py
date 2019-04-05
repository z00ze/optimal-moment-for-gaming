import json
class Config:
    def __init__(self):
        config = json.loads(open('config.json', 'r').read())
        self.PROCESSOR_TIME_INTERVAL = int(config["PROCESSOR_TIME_INTERVAL"])
        self.GET_USERS_KEYS = Users(config["GET_USERS"])
        self.HR_DATA_KEYS = HrData(config["HR_DATA"])

        
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