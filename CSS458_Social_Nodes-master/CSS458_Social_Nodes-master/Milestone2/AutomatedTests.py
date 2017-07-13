"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

Unit testing module for each class
"""

import Person
import Model
import Logger
import Personality
import Post

import unittest

class TestModel(unittest.TestCase):
    def setUp(self):
        self.m = Model.Model()
        self.m.spawn_agents(self.m.num_agents)
        self.m.logger._loggers[0].threshold = 10

    def test_model_instantiation(self):
        m = Model.Model(num_agents = 5000, topics = 30)
        m.spawn_agents(m.num_agents)
        self.assertNotEquals(m, None, "Model instantiation not working.")
        self.assertEquals(len(m.agents), 5000, "Model creating improper number of agents.")


    def test_distance_calculator(self):
        seattleperson = Person.Person(self.m, location=(-122, -48))
        newyorkperson = Person.Person(self.m, location=(-74, -40))
        jakartaperson = Person.Person(self.m, location=(107, 6))
        self.assertEquals(int(Model.find_distance(seattleperson, newyorkperson)), 2409, "SEA->NYC != 2409")
        self.assertEquals(int(Model.find_distance(newyorkperson, jakartaperson)), 10092, "NYC->JKT != 10092")
        self.assertEquals(int(Model.find_distance(jakartaperson, seattleperson)), 8361, "JKT->SEA != 8361")

        # edge cases
        people = []
        people.append(Person.Person(self.m, location=(180,90)))
        people.append(Person.Person(self.m, location=(-180,90)))
        people.append(Person.Person(self.m, location=(180,-90)))
        people.append(Person.Person(self.m, location=(-180,-90)))
        people.append(Person.Person(self.m, location=(0,0)))
        for person in people:
            for person2 in people:
                self.m.logger.log(5, "TestDistance: %r to %r = %r" % (person, person2, Model.find_distance(person, person2)))

    def test_degrees_of_separation(self):
        for x in range(30):
            self.m.agents[x].friends = set()
            self.m.agents[x].enemies = set()

        self.assertTrue(Model.find_degrees_of_separation(self.m.agents[0], self.m.agents[1]) == None,
                                                         "No conntection between agents, but one was found.")

        self.m.agents[0].friends = set()
        self.m.agents[0].friends.add(self.m.agents[1])

        self.assertEqual(Model.find_degrees_of_separation(self.m.agents[0], self.m.agents[1]), 0,
                                                          "Degrees of separation should be 0, but is not")

        for x in range(2, 30):
            self.m.agents[x-1].friends = set()
            self.m.agents[x-1].friends.add(self.m.agents[x])

        self.assertEqual(Model.find_degrees_of_separation(self.m.agents[0], self.m.agents[29]), 28,
                                                          "Degrees of separation should be 28, but is not")

        self.assertEqual(Model.find_degrees_of_separation(self.m.agents[13], self.m.agents[13]), None,
                                                          "Should return None for check against self, but doesn't")

class TestPersonalityAndPersonBehavior(unittest.TestCase):
    def setUp(self):
        self.m = Model.Model()
        self.m.spawn_agents(self.m.num_agents)
        self.m.logger._loggers[0].threshold = 10
        self.person1 = self.m.agents[0]
        self.person1.online = True
        self.person1.personality.fame = 0
        self.person2 = self.m.agents[1]
        self.person2.online = True
        self.person2.personality.fame = 0

        self.person1.friends = set()
        self.person2.friends = set()
        self.person1.friends.add(self.person2)
        self.person2.friends.add(self.person1)

    def test_like_score(self):
        # Disable any modifications of personality behavior
        self.person1.personality.facets = Personality.PersonalityFacet()
        self.person2.personality.facets = Personality.PersonalityFacet()

        self.person1.personality.interests={1: 1, 2: -1}
        post_to_like = Post.Post(self.person2, [1,])

        self.person2.dispatch_post(post_to_like)
        self.assertNotEquals(self.person1.inbox, None, "Message not arrived in inbox.")

        self.person1.settle_reposts()

        self.assertEqual(self.person1.affinity_map[self.person2], 1, "Liked post not scored correctly."
                         "%r != %r map: %r" % (self.person1.affinity_map[self.person2], 1, self.person1.affinity_map))

    def test_dislike_score(self):
        # Disable any modifications of personality behavior
        self.person1.personality.facets = Personality.PersonalityFacet()
        self.person2.personality.facets = Personality.PersonalityFacet()

        self.person1.personality.interests={1: 1, 2: -1}
        post_to_dislike = Post.Post(self.person2, [2,])

        self.person2.dispatch_post(post_to_dislike)
        self.person1.settle_reposts()

        self.assertEqual(self.person1.affinity_map[self.person2], -1, "Disliked post not scored correctly."
                                                                     "%r != %r map: %r" % (
                         self.person1.affinity_map[self.person2], -1, self.person1.affinity_map))

    def test_post_shares(self):
        self.person1.personality.repost_probability = 2

        for x in range(2, 30):
            self.m.agents[x].online = True
            self.m.agents[x].personality.repost_probability = 0.5
            self.m.agents[x].personality.probability_read_reposts = 0.5
            self.person1.friends.add(self.m.agents[x])

        self.person1.personality.interests = {1: 1, 2: -1}
        post_to_share = Post.Post(self.person2, [1, ])

        self.person2.dispatch_post(post_to_share)
        self.person1.settle_reposts()

        total_reposts = 0
        formed_opinion = 0
        for x in range(2,30):
            if self.m.agents[x].inbox != None:
                total_reposts += 1
                self.m.agents[x].settle_reposts()
                if self.person2 in self.m.agents[x].affinity_map:
                    formed_opinion += 1

        self.assertGreater(total_reposts, 0, "More than 0 reposts should have occured")
        self.assertLess(total_reposts, 28, "Fewer than 28 reposts should have occured")
        self.assertGreater(formed_opinion, 0, "More than 0 opinions should have been formed")
        self.assertLess(formed_opinion, 28, "Fewer than 28 opinions should have been formed")

    def test_make_friend(self):
        # Disable any modifications of personality behavior
        self.person1.personality.facets = Personality.PersonalityFacet()
        self.person2.personality.facets = Personality.PersonalityFacet()

        self.person1.personality.interests = {1: self.m.friends_affinity, 2: self.m.enemies_affinity}
        post_to_like = Post.Post(self.person2, [1, ])

        self.person1.process_post(post_to_like)
        self.assertTrue(self.person2 in self.person1.friends, "Person2 should now be person1's friend, but is not.")

    def test_make_enemy(self):
        # Disable any modifications of personality behavior
        self.person1.personality.facets = Personality.PersonalityFacet()
        self.person2.personality.facets = Personality.PersonalityFacet()

        self.person1.personality.interests = {1: self.m.friends_affinity, 2: self.m.enemies_affinity}
        post_to_hate = Post.Post(self.person2, [2, ])

        self.person1.process_post(post_to_hate)
        self.assertTrue(self.person2 in self.person1.enemies, "Person2 should now be person1's enemy, but is not.")

    def test_transition_friend_to_enemy(self):
        self.person1.friends=set()
        self.person2.friends=set()
        self.person1.friends.add(self.person2)
        self.person2.friends.add(self.person1)

        self.person1.personality.facets = Personality.PersonalityFacet()
        self.person2.personality.facets = Personality.PersonalityFacet()

        self.person1.affinity_map = {self.person2: self.m.friends_affinity * 0.5}

        self.person1.personality.interests = {1: self.m.friends_affinity, 2: self.m.enemies_affinity}
        posts_to_hate = []

        for x in range(2):
            posts_to_hate.append(Post.Post(self.person2, [2, ]))

        self.person1.process_post(posts_to_hate[0])
        self.assertTrue(self.person2 in self.person1.friends, "Person2 should now be person1's friend, but is not.")
        self.assertTrue(self.person2 not in self.person1.enemies, "Person2 should not be person1's enemy, but is.")

        self.person1.process_post(posts_to_hate[1])
        self.assertTrue(self.person2 not in self.person1.friends, "Person2 should not be person1's friend, but is.")
        self.assertTrue(self.person2 in self.person1.enemies, "Person2 should be person1's enemy, but is not.")

    def test_verify_posts_from_enemy_ignored(self):
        self.person1.friends = set()
        self.person2.friends = set()
        self.person1.enemies = set()
        self.person2.enemies = set()

        self.person1.enemies.add(self.person2)
        self.person1.affinity_map = {self.person2: 0}

        self.person1.personality.interests = {1: self.m.friends_affinity * 100, 2: self.m.enemies_affinity}
        post_to_very_much_like = Post.Post(self.person2, [1, ])

        self.person1.process_post(post_to_very_much_like)
        self.assertEqual(self.person1.affinity_map[self.person2], 0, "Affinities should not have changed, but they did")
        self.assertTrue(self.person2 not in self.person1.friends, "Person2 should not be person1's friend, but is.")
        self.assertTrue(self.person2 in self.person1.enemies, "Person2 should be person1's enemy, but is not.")

    def test_verify_facets_can_affect_score(self):
        self.person1.personality.interests={1: 1, 2: -1}

        # arbitrary number to cause an eventual timeout if the test is a failure
        for x in range(200):
            post_to_like = Post.Post(self.person2, [1, ])
            self.person1.process_post(post_to_like)
            if self.person1.affinity_map[self.person2] != 1:
                return True
            self.person1.personality.facets = Personality.random_facets(self.person1.personality, self.m)
            self.person1.affinity_map = {}

        self.fail("Random personalities should have caused score deviation, but did not.")

    def test_verify_famous_spam(self):
        self.person1.personality.fame = 100
        post = Post.Post(self.person1, [1,])
        self.person1.dispatch_post(post)

        self.assertTrue(len(self.person1.friends) == 1, "Test setUp changed?")

        num_delivered = 0
        for agent in self.m.agents:
            if agent.inbox == post:
                num_delivered += 1

        self.assertGreater(num_delivered, 5, "Message should have been spammed to a large number of people.")
