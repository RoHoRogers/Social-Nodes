"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

File containing the classes necessary for an agent's personality
"""

import random
import Post as Post
import Model

repost_probability_mutiplier = 1
many_friends_liking = 2
many_friends_disliking = -2
fame_liking = 2
fame_disliking = -2
hemisphere_liking = 2
hemisphere_disliking = -2
close_liking_multiplier = 1.5
distant_liking_multiplier = 1.5
many_friends_threshold = 30
distance_close_threshold = 2000

# For random personality generator - Both of these must sum to <= 1
prob_to_like = .5
prob_to_dislike = .3

# Tuple containing the minimum and maximum magnitude of a like or dislike
amount_to_like_dislike = (1,7)


def random_personality_generator(model):
    """
    Randomly allocate likes and dislikes to a person for a subset of the total topics in the simulation

    :param model: reference to model object
    :return: mapping of likes and dislikes for this person
    """
    num_of_topics = model.topics

    likemap = None

    # put in a loop in case no likes get selected
    while likemap is None or len(likemap) == 0:
        likemap = {}
        for x in range(num_of_topics):
            like = random.random()
            amount = random.randint(amount_to_like_dislike[0], amount_to_like_dislike[1])
            if like < prob_to_like:
                likemap[x] = amount
            elif like < prob_to_dislike + prob_to_like:
                amount *= -1
                likemap[x] = amount
            else:
                pass

    return likemap


def random_facets(personality, model):
    """
    Randomly allocates personality facets to a person and establishes the chain of facets for processing
    a message.

    :param personality: reference to personality object
    :param model: reference to model object
    :return: first personality facet in facet chain
    """
    options = (eval('PersonalityFacet.__subclasses__()'))
    selected = []
    num_to_select = len(options) / 2
    while len(selected) < num_to_select:
        for option in options:
            if random.random() < .5 and len(selected) < num_to_select:
                selected.append(option)

    model.logger.log(1, "%r has gained personality facets %r" % (personality.person, selected))
    selected[len(selected)-1] = selected[len(selected)-1]()
    for x in range(len(selected)-2, -1, -1):
        selected[x] = selected[x](selected[x+1])
    return selected[0]


class Personality(object):
    """
    Personality class that defines the behavior of a personality
    """

    def __init__(self, person, model, generator = random_personality_generator,
                 facet_generator = random_facets):
        """
        Create a personality for an agent

        :param person: person for which to create a personality for
        :param model: reference to model object
        :param generator: generator to use for generating the personality
        :param facet_generator: generator to use for creating personalty facets for this personality
        """

        self.person = person
        self.interests = generator(model)
        self.facets = facet_generator(self, model)
        self.model = model
        self.post_probability = random.random()
        self.repost_probability = random.random() * repost_probability_mutiplier
        self.probability_read_reposts = random.random()
        self.fame = random.random() * 100

    def accept_repost(self):
        """
        Determines if a reposted message will be accepted.
        :return: Boolean of whether to accept the message repost
        """
        if random.random() < self.probability_read_reposts:
            return True
        else:
            return False

    def process_post(self, message):
        """
        Accepts a message, and using the settings defined in the person's personality, determine whether, and
        by how much, a message is liked.

        :param message: message to process
        :return: amount that the message was liked or disliked
        """
        if self.person.online == True:
            like_total = 0

            for topic in message.topics:
                if topic in self.interests:
                    like_total += self.interests[topic]

            like_total = self.facets.process_post(message, like_total, self.person)
            self.model.logger.log(0, "%r had reaction of %d to %r" % (self.person, like_total, message))
            self.repost_decide(message)
            return like_total
        return None

    def create_post(self):
        """
        Generates a post with a random subset of the person's interests
        :return: message to post
        """
        if random.random() < self.post_probability:
            keys = list(self.interests.keys())
            post_topic = []
            # randomly 1 to 4 topics
            for x in range(random.randint(0, 4)):
                post_topic.append(self.interests[keys[random.randint(0, len(keys)-1)]])
            return Post.Post(self.person, post_topic)

    def spam_to_world(self):
        """
        Determines if a post should be randomly spammed.  Currently based only the the 'fame' attribute
        of a personality of the agent which posted the message.

        :return: True if a post should be randomly spammed to other agents
        """
        if self.fame + random.random() * 100 > 100:
            return True
        else:
            return False

    def repost_decide(self, message):
        """
        Determines if a message will be reposted.  Currently all "famous" reposts are reposted,
        and messages from non-famous agents are reposted at a variable probability level

        :param message: message which is a candidate for being reposted
        :return: nothing
        """
        if random.random() < self.repost_probability:
            self.person.dispatch_post(message)

class PersonalityFacet(object):
    """
    Decorator to allow arbitrary number of personality "facets" that can manipulate the
    end result of how much a post is liked or disliked
    """
    def __init__(self, next_facet = None):
        self.next_facet = next_facet

    def process_post(self, message, current_score, person):
        if self.next_facet is None:
            return current_score
        return self.return_result(message, current_score, person)

    def return_result(self, message, current_score, person):
        if self.next_facet is None:
            return current_score
        return self.next_facet.return_result(message, current_score, person)

class LikesPeopleWithManyFriends(PersonalityFacet):
    def process_post(self, message, current_score, person):
        num_of_friends = len(message.sender.friends)
        if num_of_friends > many_friends_threshold:
            current_score += many_friends_liking
        return self.return_result(message, current_score, person)
        
class LikesPeopleWithFame(PersonalityFacet):
    def process_post(self, message, current_score, person):
        fame = message.sender.personality.fame
        if fame > (random.random() * 100):
            current_score += fame_liking
        return self.return_result(message, current_score, person)
        
class HatesPeopleWithFame(PersonalityFacet):
    def process_post(self, message, current_score, person):
        fame = message.sender.personality.fame
        if fame > (random.random() * 100):
            current_score += fame_disliking
        return self.return_result(message, current_score, person)
        
class LikesPeopleWithFewFriends(PersonalityFacet):
    def process_post(self, message, current_score, person):
        num_of_friends = len(message.sender.friends)
        if num_of_friends < many_friends_threshold:
            current_score += many_friends_disliking
        return self.return_result(message, current_score, person)

class LikesClosePeople(PersonalityFacet):
    def process_post(self, message, current_score, person):
        distance = Model.find_distance(person, message.sender)
        if distance < distance_close_threshold and current_score > 0:
            current_score *= close_liking_multiplier if current_score > 0 else 1 / close_liking_multiplier
        return self.return_result(message, current_score, person)


class LikesDistantPeople(PersonalityFacet):
    def process_post(self, message, current_score, person):
        distance = Model.find_distance(person, message.sender)
        if distance > distance_close_threshold and current_score > 0:
            current_score *= distant_liking_multiplier if current_score > 0 else 1 / distant_liking_multiplier
        return self.return_result(message, current_score, person)


class HatesPeopleInOppositeHemisphere(PersonalityFacet):
    def process_post(self, message, current_score, person):
        if person.location[0] * message.sender.location[0] < 0:
            current_score += hemisphere_disliking
        if person.location[1] * message.sender.location[1] < 0:
            current_score += hemisphere_disliking
        return self.return_result(message, current_score, person)


class LovesPeopleInOppositeHemisphere(PersonalityFacet):
    def process_post(self, message, current_score, person):
        if person.location[0] * message.sender.location[0] < 0:
            current_score += hemisphere_liking
        if person.location[1] * message.sender.location[1] < 0:
            current_score += hemisphere_liking
        return self.return_result(message, current_score, person)