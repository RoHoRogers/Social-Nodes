class Post(object):
    topics = [1, 2]
    senderID = 0
    
    def __init__ (self, topics, senderID):
        self.topics = list(topics)
        self.senderID = senderID
        
    