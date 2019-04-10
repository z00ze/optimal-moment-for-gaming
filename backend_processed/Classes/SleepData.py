class SleepData:
    def __init__(self, end_time, sleeping, efficiency, main_sleep):
        self.end_time = end_time
        self.sleeping = sleeping
        self.efficiency = efficiency
        self.main_sleep = main_sleep

        print(f"New SleepData object created with end_time: {end_time}, sleeping: {sleeping}, efficiency: {efficiency} and main_sleep:{main_sleep}")