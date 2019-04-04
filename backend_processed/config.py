import json
class Config:
    def __init__(self):
        config = json.loads(open('config.json', 'r').read())
        self.GET_USERS_KEYS = Users(config["GET_USERS"])

        

class Users:
    def __init__(self, user_dict):
        self.USERS = user_dict["USERS_KEY"]
        self.USER_ID_KEY = user_dict["USER_ID_KEY"]
        self.ACCESS_TOKEN_KEY = user_dict["ACCESS_TOKEN_KEY"]