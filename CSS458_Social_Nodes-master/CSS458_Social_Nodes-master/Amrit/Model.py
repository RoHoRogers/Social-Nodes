import numpy as N
import Visualizer as V
import PersonsManager as PM
import Person as PE
import TimeManager as TM

class Model(object):
    agents = []
    
    def __init__(self):
        PM.PersonsManager.createManager()
        V.Visualizer.createVisualizer()
        TM.TimeManager.createManager()
    
    def spawnAgents(self, count=100):
        
        for num in range(0, count):
            position = PE.Position(N.random.uniform(-100, 100), N.random.uniform(-100, 100))
            
            PM.PersonsManager.sharedManager.addPerson(position)
            
    def startSimulating(self, maxTime=10):
        
        for time in range(maxTime + 1):
            if time == 0:
                PM.PersonsManager.sharedManager.startOnline()
            else:
                PM.PersonsManager.sharedManager.startSharing()
                PM.PersonsManager.sharedManager.startSending()
                
            PM.PersonsManager.sharedManager.updateVisualization()
                
            TM.TimeManager.sharedManager.increaseTime()
        
model = Model()
model.spawnAgents()
model.startSimulating(10)