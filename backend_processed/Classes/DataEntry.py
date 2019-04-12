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

        self.sleep_eff = sleep_eff
        self.sleeping = sleeping
        self.main_sleep = main_sleep
        self.hr_value = hr_value
        self.eye_data = eye_data

        self.dynamic_eff = dynamic_eff
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

    # TODO: eye data, omfg

