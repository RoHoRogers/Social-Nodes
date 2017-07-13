class TimeManager(object):
    sharedManager = None
    
    time = 0
    
    @staticmethod
    def createManager():
        TimeManager.sharedManager = TimeManager()
        
    def increaseTime(self):
        self.time += 1