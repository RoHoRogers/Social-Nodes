# -*- coding: utf-8 -*-
import numpy as N
import Person as PE
import Old_Post as PO
import PersonsManager as PM
import Variables as VR

class Personality(object):
    distancePreference = 0.25
    topicPreference = 0.25
    friendPreference = 0.25
    influencePreference = 0.25
    
    postPreference = 0.20
    friendPostPreference = 0.4
    
    sharePreference = 0.8
    
    maxDistance = 5
    topics = {1:3, 2:4}
    
    def __init__(self):
        pass
        
    def evaluatePost(self, person, post):
        sender = PM.PersonsManager.sharedManager.getPersonFromID(post.senderID)
        
        distanceLikeness = 0.0
        
        distanceRandom = N.random.uniform(0.0, 1.0)
        if distanceRandom <= self.distancePreference:
            if person.position.distanceFrom(sender.position) <= self.maxDistance:
                distanceLikeness = 1.0
            else:
                distanceLikeness = -1.0
            
        topicLikeness = 0
        
        topicRandom = N.random.uniform(0.0, 1.0)
        if topicRandom <= self.topicPreference:
            for key in post.topics:
                topicLikeness += self.topics[key]
                
            topicLikeness /= (VR.MAX_TOPIC_VALUE * VR.NUM_OF_TOPICS - VR.MIN_TOPIC_VALUE * VR.NUM_OF_TOPICS)
            
        friendLikeness = 0
        
        friendRandom = N.random.uniform(0.0, 1.0)
        if friendRandom <= self.friendPreference:
            if post.senderID in person.getFriends():
                friendLikeness = 1.0
            else:
                friendLikeness = -1.0
                
        influenceLikeness = 0
        
        influenceRandom = N.random.uniform(0.0, 1.0)
        if influenceRandom <= self.influencePreference:
            if PM.PersonsManager.sharedManager.getTrendingTopics()[0] in post.topics:
                influenceLikeness = 1.0
                PM.PersonsManager.sharedManager.trendInfluences += 1
                
            elif PM.PersonsManager.sharedManager.getTrendingTopics()[1] in post.topics:
                influenceLikeness = -1.0
                PM.PersonsManager.sharedManager.trendInfluences += 1
        
        return distanceLikeness + topicLikeness + friendLikeness + influenceLikeness
    
    def shouldSharePost(self):
        random = N.random.randint(0.0, 1.0)
        
        if random <= self.sharePreference:
            return True
            
        return False
        
    def shouldCreatePost(self):
        random = N.random.uniform(0.0, 1.0)

        if random <= self.postPreference:
            return True
            
        return False
        
                        
class Introvert(Personality):
    
    def __init__(self, topics={1:3, 2:-4, 3:-5, 7: 2}):
        self.topics = {}
        
        self.distancePreference = 0.2
        self.topicPreference = 0.8
        
        self.postPreference = 0.2
        
        self.sharePreference = 0.2
        
        self.maxDistance = 3
        
        for key in topics:
            self.topics[key] = topics[key]