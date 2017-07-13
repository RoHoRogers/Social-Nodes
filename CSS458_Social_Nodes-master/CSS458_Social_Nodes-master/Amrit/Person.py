import numpy as N

import Old_Personality as PT
import Visualizer as V
import PersonsManager as PM
import Old_Post as PO
import Variables as VR

class Position(object):
    x = 0.0
    y = 0.0
    
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        
    def toTouple(self):
        return (self.x, self.y)
        
    def distanceFrom(self, position):
        return N.sqrt((position.x - self.x)**2 + (position.y - self.y)**2)

class Person(object):
    ID = 0
    position = Position()
    online = False
    
    personality = None
    
    connectedPeople = {}
    friendsList = {}
    ignoredList = {}
    
    likes = 0
    missed = 0
    
    allPosts = []
    receivedPosts = []
    
    def __init__(self, position, ID=0, friends=None):
        self.position = position
        self.connectedPeople = {}
        
        self.likes = 0
        self.missed = 0
        self.allPosts = []
        self.receivedPosts = []
        
        randomScales = N.random.randint(VR.MIN_TOPIC_VALUE, VR.MAX_TOPIC_VALUE, size=VR.NUM_OF_TOPICS)
        
        topics = {}
        for index in range(VR.NUM_OF_TOPICS):
            topics[index + 1] = randomScales[index]
            
        self.personality = PT.Introvert(topics=topics)
        self.ID = ID
        
    def getFriends(self):
        friends = []
        
        for personID in self.connectedPeople.keys():
            if self.connectedPeople[personID] >= VR.FRIEND_LIMIT:
                friends.append(personID)
                
        return friends
        
    def getIgnored(self):
        ignored = []
        
        for personID in self.connectedPeople.keys():
            if self.connectedPeople[personID] <= VR.ENEMY_LIMIT:
                ignored.append(personID)
                
        return ignored
        
    def getAvgFriendsDistance(self):
        friends = self.getFriends()
        distance = 0.0
        
        if len(friends) != 0:
            for personID in friends:
                person = PM.PersonsManager.sharedManager.getPersonFromID(personID)
            
                distance += person.position.distanceFrom(self.position)
            
            distance /= len(friends)
            
        return distance
        
    def getAvgIgnoredDistance(self):
        ignored = self.getIgnored()
        distance = 0.0
        
        if len(ignored) != 0:
            for personID in ignored:
                person = PM.PersonsManager.sharedManager.getPersonFromID(personID)
            
                distance += person.position.distanceFrom(self.position)
            
            distance /= len(ignored)
            
        return distance
    
    def getMostLikedTopic(self):
        theTopic = 0
        topicLikeness = VR.MIN_TOPIC_VALUE * 2
        
        for topic in self.personality.topics.keys():
            if self.personality.topics[topic] >= topicLikeness:
                theTopic = topic
                topicLikeness = self.personality.topics[topic]
                
        return [theTopic, topicLikeness]
        
    def getMostDislikedTopic(self):
        theTopic = 0
        topicLikeness = VR.MAX_TOPIC_VALUE * 2
        
        for topic in self.personality.topics.keys():
            if self.personality.topics[topic] <= topicLikeness:
                theTopic = topic
                topicLikeness = self.personality.topics[topic]
                
        return [theTopic, topicLikeness]
        
    def getEdges(self):
        edges = []
        
        for personID in self.connectedPeople:
            person = PM.PersonsManager.sharedManager.getPersonFromID(personID)
            
            edge = {(self, person): self.connectedPeople[personID]}
            edges.append(edge)
            
        return edges
        
    def evaluatePost(self, post):
        if (post in self.allPosts) == False:
            sender = PM.PersonsManager.sharedManager.getPersonFromID(post.senderID)
            self.allPosts.append(post)
            
            likeness = self.personality.evaluatePost(self, post)
            
            if ((post.senderID in self.connectedPeople) == False) or ((post.senderID in self.connectedPeople) and \
                self.connectedPeople[post.senderID] > VR.ENEMY_LIMIT):
                self.receivedPosts.append(post)
                
                self.likes += likeness
                
                if post.senderID in self.connectedPeople:
                    self.connectedPeople[post.senderID] += likeness
                else:
                    self.connectedPeople[post.senderID] = likeness
            
                PM.PersonsManager.sharedManager.startOnline(person=self)
        
            elif self.connectedPeople[post.senderID] > VR.ENEMY_LIMIT:
                if likeness > 0:
                    self.missed += 1
        
                #V.Visualizer.sharedVisualizer.connect(self, sender, self.connectedPeople[post.senderID])
        
    def sharePosts(self):
        self.likes = 0.0
        self.missed = 0
        
        for post in list(self.receivedPosts):
            if self.personality.shouldSharePost():
                PM.PersonsManager.sharedManager.sharePost(post, self.getFriends())
                self.receivedPosts.remove(post)
        
    def createPost(self):
        if self.personality.shouldCreatePost():
            chosenTopics = []
            
            for key in self.personality.topics:
                if self.personality.topics[key] > 0:
                    chosenTopics.append(key)
            
            #PM.PersonsManager.sharedManager.startOnline(person=self)
            
            post = PO.Post(chosenTopics, self.ID)
            PM.PersonsManager.sharedManager.broadcastPost(post)
            
            self.allPosts.append(post)