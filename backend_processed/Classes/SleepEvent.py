class SleepEvent:
    def __init__(self, end_time, sleeping, efficiency, main_sleep, predict):
        """ Every event marks an end to previous action. 
    
        Therefore term end_time is used in SleepEvent
        """
        self.end_time = end_time
        self.sleeping = sleeping
        self.efficiency = efficiency
        self.main_sleep = main_sleep
        self.predict = predict