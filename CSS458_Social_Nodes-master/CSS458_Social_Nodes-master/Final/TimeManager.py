"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

TimeManager
"""

class TimeManager(object):
    sharedManager = None
    
    time = 0
    
    @staticmethod
    def createManager():
        TimeManager.sharedManager = TimeManager()
        
    def increaseTime(self):
        self.time += 1