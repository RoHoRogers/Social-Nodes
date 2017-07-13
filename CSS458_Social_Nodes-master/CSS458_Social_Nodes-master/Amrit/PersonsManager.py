import numpy as N
import Visualizer as V
import Person as PE
import Variables as VR

class PersonsManager(object):
    sharedManager = None
    
    increasingID = 0
    
    people = []
    postsSent = []
    postsShared = []
    
    trendsInfluences = 0
    
    @staticmethod
    def createManager():
        PersonsManager.sharedManager = PersonsManager()
        
    def __init__(self):
        self.increasingID = 0
        
        self.people = []
        self.postsSent = []
        self.postsShared = []
        
        self.trendInfluences = 0
    
    def addPerson(self, position):
        person = PE.Person(PE.Position(position.x, position.y), ID=self.increasingID)
        
        self.people.append(person)
        self.increasingID += 1
        
        V.Visualizer.sharedVisualizer.addNode(person)
        
    def getPersonFromID(self, personID):
        for person in self.people:
            if person.ID == personID:
                return person
                
        return None
        
    def getTrendingTopics(self):
        likedTopics = []
        bestTopic = [0,VR.MIN_TOPIC_VALUE * 2.0]
        
        for person in self.people:
            topic = person.getMostLikedTopic()
            
            likedTopics.append(topic)
        
        for topic in likedTopics:
            if topic[1] >= bestTopic[1]:
                bestTopic[0] = topic[0]
                bestTopic[1] = topic[1]
                
        dislikedTopics = []
        worstTopic = [0,VR.MAX_TOPIC_VALUE * 2.0]
        
        for person in self.people:
            topic = person.getMostDislikedTopic()
            
            dislikedTopics.append(topic)
        
        for topic in dislikedTopics:
            if topic[1] <= worstTopic[1]:
                worstTopic[0] = topic[0]
                worstTopic[1] = topic[1]
        
        return [bestTopic[0], worstTopic[0]]
        
    def startOnline(self, person=None):
        if person == None:
            randomIndexes = N.random.randint(len(self.people), size=5)
        
            for i in range(len(self.people)):
                if i in randomIndexes:
                    self.people[i].online = True
        else:
            for aPerson in self.people:
                if person.position.distanceFrom(aPerson.position) <= VR.NEIGHBOUR_DISTANCE:
                    aPerson.online = True
        
    def startSending(self):
        for person in self.people:
            if person.online == True:
                person.createPost()
                
    def startSharing(self):
        for person in self.people:
            if person.online == True:
                person.sharePosts()
        
    def broadcastPost(self, post):
        for person in self.people:
            if (person.ID != post.senderID) and (person.online == True):
                person.evaluatePost(post)
            
        self.postsSent.append(post)
        
    def sharePost(self, post, people):
        for person in self.people:
            if person.ID in people:
                person.evaluatePost(post)
                
        self.postsShared.append(post)
        
    def getAverageFriends(self):
        average = 0.0
        
        for person in self.people:
            average += len(person.getFriends())
            
        return average / len(self.people)
        
    def getAverageIgnored(self):
        average = 0.0
        
        for person in self.people:
            average += len(person.getIgnored())
            
        return average / len(self.people)
        
    def getAverageLikeness(self):
        average = 0.0
        
        for person in self.people:
            average += person.likes
            
        return average / len(self.people)
        
    def getAverageFriendsDistance(self):
        average = 0.0
        
        for person in self.people:
            average += person.getAvgFriendsDistance()
            
        return average / len(self.people)
        
    def getAverageIgnoredDistance(self):
        average = 0.0
        
        for person in self.people:
            average += person.getAvgIgnoredDistance()
            
        return average / len(self.people)
        
    def getAverageMissed(self):
        average = 0.0
        
        for person in self.people:
            average += person.missed
            
        return average / len(self.people)
        
    def getOnlinePeople(self):
        onlinePeople = 0.0
        
        for person in self.people:
            if person.online:
                onlinePeople += 1
            
        return onlinePeople
                
    def updateVisualization(self):
        edges = []
        
        for person in self.people:
            edges = edges + person.getEdges()
        
        V.Visualizer.sharedVisualizer.addNodesAndEdges(self.people, edges)    
        V.Visualizer.sharedVisualizer.addPostsSent(len(self.postsSent))
        V.Visualizer.sharedVisualizer.addPostsShared(len(self.postsShared))
        V.Visualizer.sharedVisualizer.addAvgFriends(self.getAverageFriends())
        V.Visualizer.sharedVisualizer.addAvgIgnored(self.getAverageIgnored())
        V.Visualizer.sharedVisualizer.addAvgLikeness(self.getAverageLikeness())
        V.Visualizer.sharedVisualizer.addAvgFriendsDistance(self.getAverageFriendsDistance())
        V.Visualizer.sharedVisualizer.addAvgIgnoredDistance(self.getAverageIgnoredDistance())
        V.Visualizer.sharedVisualizer.addAvgMissed(self.getAverageMissed())
        V.Visualizer.sharedVisualizer.addOnlinePeople(self.getOnlinePeople())
        #V.Visualizer.sharedVisualizer.pause()