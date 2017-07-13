from enum import Enum

class PostType(Enum):
    #List of all possible topics
    
    Nothing = 0
    Technology = 1
    Physics = 2
    Politics = 3
    Economics = 4
    #...
    
class PostTopics(object):
    #Keeps track of the topics
    
    primaryTopic = PostType.Nothing
    secondaryTopic = PostType.Nothing
    thirdTopic = PostType.Nothing

class Post(object):
    #Has post information, like topics is is about
    #and who sent it
    
    topics = PostTopics()
    senderID = 1234567890
    
    like = True
    
    def __init__ (self, topics, senderID):
        self.topics = topics
        self.senderID = senderID
        
    