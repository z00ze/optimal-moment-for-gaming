from Classes.Config import Config
CONF = Config()

class DataEntry:
    def __init__(self, datetime,
            unique_id = None,
            sleep_eff = None,            
            sleeping = None,
            main_sleep = None,
            hr_value = None,
            eye_data = None,
            dynamic_eff = None,
            omfg = None,
            predict = False):

        self.datetime = datetime
        self.unique_id = unique_id
        self.sleep_eff = sleep_eff
        self.sleeping = sleeping
        self.main_sleep = main_sleep
        self.hr_value = hr_value
        self.eye_data = eye_data       

        self.dynamic_eff = dynamic_eff
        self.predict = predict
        self.omfg = omfg
        

    def set_sleep_eff(self, sleep_eff):
        self.sleep_eff = sleep_eff   

    def set_sleeping(self, sleeping):
        self.sleeping = sleeping
    
    def set_main_sleep(self, main_sleep):
        self.main_sleep = main_sleep

    def set_hr_value(self, hr_value):
        self.hr_value = hr_value

    def set_dynamic_eff(self, dynamic_eff):
        self.dynamic_eff = dynamic_eff

    def set_predict(self, predict):
        self.predict = predict

    def get_values_to_sql_query(self, user_id):
        columns = []
        values = []

        if(self.unique_id):
            columns.append(CONF.DATABASE_COLUMN_NAMES.UNIQUE_ID)
            values.append(self.unique_id)
        
        columns.append(CONF.DATABASE_COLUMN_NAMES.USER_ID)
        values.append(user_id)
        
        if(self.datetime):
            columns.append(CONF.DATABASE_COLUMN_NAMES.DATETIME)
            values.append(self.datetime.strftime("%Y-%m-%d %H:%M:%S"))
        
        if(self.sleep_eff):
            columns.append(CONF.DATABASE_COLUMN_NAMES.SLEEP_EFF)
            values.append(self.sleep_eff)
        
        if(self.sleeping):
            columns.append(CONF.DATABASE_COLUMN_NAMES.SLEEPING)
            values.append(self.sleeping)

        if(self.main_sleep):
            columns.append(CONF.DATABASE_COLUMN_NAMES.MAIN_SLEEP)
            values.append(self.main_sleep)
        
        if(self.hr_value):
            columns.append(CONF.DATABASE_COLUMN_NAMES.HR_VALUE)
            values.append(self.hr_value)

        if(self.eye_data):
            columns.append(CONF.DATABASE_COLUMN_NAMES.EYETRACK)
            values.append(self.eye_data)

        if(self.dynamic_eff):
            columns.append(CONF.DATABASE_COLUMN_NAMES.DYNAMIC_EFF)
            values.append(self.dynamic_eff)
        
        if(self.omfg):
            columns.append(CONF.DATABASE_COLUMN_NAMES.OMFG)
            values.append(self.omfg)
        
        if(self.predict):
            columns.append(CONF.DATABASE_COLUMN_NAMES.PREDICT)
            values.append(self.predict)
            
        return columns, values

    # TODO: eye data, omfg

