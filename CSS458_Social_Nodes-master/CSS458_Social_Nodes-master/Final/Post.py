"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

Module for the post object
"""

class Post(object):
    """
    Post object, currently contains no behavior
    """

    def __init__(self, sender, topics):
        """
        :param sender: Reference to agent who sent the message
        :param topics: List of integers representing message topics
        """
        self.sender = sender
        self.topics = topics