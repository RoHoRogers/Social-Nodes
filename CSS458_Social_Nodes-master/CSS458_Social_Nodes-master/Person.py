"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

File containing the classes necessary for an agent's overall behavior
"""

import random
import Personality as Personality
import Post as Post

spam_to_world_proportion = .01 # proportion of agents that certian users are allowed to spam to

class Person(object):
    def __init__(self, model, location = None, friends_affinity = 150, enemies_affinity = -200,
                 personality = None, online = False):
        """
        Create a person object

        :param model: reference to simulation model object
        :param location: physical location of the agent (lat,long)
        :param friends_affinity: Affinity score needed to become friends
        :param enemies_affinity: Affinity score needed to become enemies
        :param personality: Personality to give the agent
        :param online: Boolean representing if this agent will initially be online
        """

        self.affinity_map = {}
        self.friends = set()
        self.enemies = set()
        self.friends_affinity = friends_affinity
        self.enemies_affinity = enemies_affinity
        self.posts_seen = set()

        if personality == None:
            self.personality = personality
        else:
            self.personality = personality(person = self, model = model)
        self.model = model
        self.online = online

        if location is None:
            self.location = (random.randint(-180, 180), random.randint(-80, 80))
        else:
            self.location = location

        self.inbox = set()

    def take_turn(self):
        """
        Method that performs the actions of an agent taking its turn

        :return: nothing
        """

        # decide to create a post or not
        self.posts_seen.clear()
        if self.online == True:
            self.create_post()
            self.decay_relationships()
        else:
            # agent currently is not online, randomly decide whether to make this agent online
            if random.random() < self.model.probability_become_online:
                # just give them one random friend for now...
                self.model.logger.log(1, "%r got connected to the internet." % self)
                self.online = True
                self.model.online_agents.append(self)
                self.model.initial_connect_friend(self)

    def receive_post(self, message):
        """
        Method that is called when an agent recieves a message.

        :param message: message that is recieved
        :return: nothing
        """
        if self.online == True and message not in self.posts_seen:
            self.model.messages_received += 1
            self.inbox.add(message)
            self.model.request_post_attention(self)

    def accept_repost(self):
        """
        Method to determine whether a repost should be accepted
        :return: boolean of whether message will be accepted
        """
        return self.personality.accept_repost()

    def settle_reposts(self):
        """
        Method that is called by the model class if this agent has requested to process posts that it has
        recieved.

        :return: nothing
        """
        self.posts_seen.update(self.inbox)
        for message in self.inbox:
            self.process_post(message)
        self.inbox.clear()

    def create_post(self):
        """
        Method that is called to give an agent an opportunity to create a post

        :return: nothing
        """
        if self.personality is None:
            # No personality, do nothing
            pass
        else:
            post = self.personality.create_post()
            if post is not None:
                self.model.messages_sent += 1
                self.dispatch_post(post)

    def process_post(self, message):
        """
        Method to process a post that an agent has recieved, and possibly repost it, if the agent decides
        to do so.

        :param message: message to process
        :return: nothing
        """
        if message.sender not in self.enemies:
            if self.personality is None:
                pass
            else:
                affinity_delta = self.personality.process_post(message)
                if message.sender in self.affinity_map:
                    self.affinity_map[message.sender] += affinity_delta
                else:
                    self.affinity_map[message.sender] = affinity_delta

                poster_affinity = self.affinity_map[message.sender]

                # currently friendship is not reciprocal, perhaps change?

                if poster_affinity >= self.friends_affinity:
                    self.friends.add(message.sender)
                    #message.sender.friends.add(self)
                    self.model.logger.log(1, "%r became friends with %r"% (self, message.sender))
                elif poster_affinity <= self.enemies_affinity:
                    if message.sender in self.friends:
                        self.friends.remove(message.sender)
                        if self in message.sender.friends:
                            message.sender.friends.remove(self)
                    self.enemies.add(message.sender)
                    self.model.logger.log(1, "%r became enemies with %r" % (self, message.sender))
        else:
            # ignore message
            pass

    def spam_to_world(self):
        """
        Determine whether posts from this person should be spammed to people who are not friends with this agent

        :return: True if spam should happen, false if not
        """
        return self.personality.spam_to_world()

    def dispatch_post(self, post):
        """
        Send post to each agent in this agent's friend list, and spam the message to a certain proportion of all
        online agents if this agent is allowed to do so.

        :param post: post to send
        :return: nothing
        """
        for friend in self.friends:
            self.model.logger.log(0, "%r dispatching post %r to %r" % (self, post, friend))

            # if this is a repost, see if receiver will accept it
            if post.sender != self and friend.accept_repost():
                friend.receive_post(post)

        if post.sender.spam_to_world():
            num_to_spam = int(len(self.model.online_agents) * spam_to_world_proportion)
            for x in range (num_to_spam):
                self.model.online_agents[random.randint(0, len(self.model.online_agents) - 1)].receive_post(post)

    def decay_relationships(self):
        """
        Reduces the amount of like/dislike for people who are not friends or unfriended,
        in that way over time, people "forget about" people that they don't really know well
        :return: nothing
        """
        affect_magnitude = 0.95 # these settings need to be moved somewhere more centralized
        removal_thresh = 0.05

        known_people = self.affinity_map.keys()
        people_to_affect = [x for x in known_people if x not in self.friends
                            and x not in self.enemies]

        for person in people_to_affect:
            self.affinity_map[person] *= affect_magnitude
            if abs(self.affinity_map[person]) < removal_thresh:
                del self.affinity_map[person]