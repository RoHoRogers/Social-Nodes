"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

Overall simulation manager that carries variables and settings that will change the model.
This class will initiate the social nodes simulation and call appropriate statistics generation
and visualization modules.

DRIVER CLASS
"""

import Logger as L
import Person as P
import Personality as Personality
import math
import random
import PersonalityShaping

import TimeManager as TM
import Visualizer as V

import DataExporter

class Model(object):
    """
    Model class acts as the simulation manager that carries variables and settings.
    """

    def __init__(self, num_agents = 3000, topics = 20, friends_affinity = 15, enemies_affinity = -15,
                 time_to_run = 100, probability_initially_online = 0.5, probability_become_online = 0.05,
                 visualizer = False, visualizerOptions = [], data_collector = None, data_collector_results = None, log_level = 3,
                 force_personalities = None, **kwargs):
        """
        :param num_agents: Maximum number of agents for the simulation
        :param topics: Number of topics of interest
        :param friends_affinity: Affinity score required for an agent to become friends with another agent
        :param enemies_affinity: Affinity score required for an agent to become enemies with another agent
        :param time_to_run: Number of rounds before ending simulation
        :param probability_initially_online: The probability that an agent is connected to internet at the
                                             beginning of the simulation
        :param probability_become_online: The probability that an agent who is not online will become connected
                                          to the internet at each round
        """

        # Instance variables for simulation's configuration
        self.logger = L.Logger(self, options = {'threshold': log_level})

        self.agents = []
        self.online_agents = []
        self.num_agents = num_agents
        self.topics = topics
        self.friends_affinity = friends_affinity
        self.enemies_affinity = enemies_affinity
        self.time_to_run = time_to_run
        self.probability_initially_online = probability_initially_online
        self.probability_become_online = probability_become_online
        self.agents_to_settle = set()

        # Counters for statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0

        self.visualizer = visualizer
        self.visualizerOptions = visualizerOptions

        if data_collector == None:
            self.data_collector = data_collector
        else:
            self.data_collector = data_collector(self, data_collector_results)

        self.force_personalities = force_personalities

    def run_simulation(self):
        """
        Loops through each agent fo rthe specified number of rounds.
        :return: Nothing
        """

        # Create agents for simulation
        self.spawn_agents(self.num_agents)

        if self.force_personalities != None:
            self.force_personalities(self)

        if self.visualizer == True:
            V.Visualizer.createVisualizer(types=self.visualizerOptions, showAtEnd=True)

        TM.TimeManager.createManager()
        for x in range (self.time_to_run):
            for agent in self.agents:
                agent.take_turn()
                while self.agents_to_settle:
                    self.agents_to_settle.pop().settle_reposts()
                if self.data_collector != None:
                    self.data_collector.collector_turn(x, agent)
            if self.visualizer == True:
                self.generate_visualizations(x)
                TM.TimeManager.sharedManager.increaseTime()
            if self.data_collector != None:
                self.data_collector.collector_round(x)
            self.generate_statistics(x)

        if self.visualizer == True:
            V.Visualizer.sharedVisualizer.updateEverything()

        if self.data_collector != None:
            self.data_collector.finalize()

    def request_post_attention(self, agent):
        """
        Method called by agents that have recieved a message, so that the message can be processed before
        proceeding to the next agent's turn.
        """
        self.agents_to_settle.add(agent)

    def spawn_agents(self, num_agents):
        """
        Spawn the specified number of agents
        :param num_agents: Number of agents to spawn
        :return: nothing
        """
        for x in range(num_agents):
            self.agents.append(P.Person(self, personality = Personality.Personality,
                               friends_affinity = self.friends_affinity, enemies_affinity = self.enemies_affinity))
            # Determine if this agent will be online at the start of the simulation
            if random.random() < self.probability_initially_online:
                self.agents[x].online = True
                self.online_agents.append(self.agents[x])

        # connect some users to internet and seed some friends just by random for now
        for agent in self.online_agents:
            self.initial_connect_friend(agent)

    def initial_connect_friend(self, agent):
        """
        Create a random friend connection for the speciifed agent

        :param agent: Agent for which to make new friend connection(s)
        :return: nothing
        """
        # Randomly decide to create 2 friend connections or 1

        if len(self.online_agents) < 3:
            raise Exception("At least 3 agents must be initially online for friendships to properly form.  " +
                            "Please re-run with a greater number of agents, or increase the initially online " +
                            "probability")
        if random.random() < .40:
            num_friends = 2
        else:
            num_friends = 1

        for x in range(num_friends):
            friend_to_add = None

            # randomly choose a friend and ensure friend isn't itself
            while friend_to_add is None or friend_to_add == agent:
                friend_to_add = self.online_agents[random.randint(0, len(self.online_agents) - 1)]

            agent.friends.add(friend_to_add)
            friend_to_add.friends.add(agent)

    def generate_statistics(self, timestep):
        """
        Method generates some basic statistics that are created each time step and sent to the logger.

        :param timestep: Integer specifying the current time step
        :return: nothing
        """
        total_friends = 0
        total_enemies = 0
        affinity_entries = 0
        num_online = len(self.online_agents)
        for agent in self.online_agents:
            total_friends += len(agent.friends)
            total_enemies += len(agent.enemies)
            affinity_entries += len(agent.affinity_map)
        self.logger.log(3, "round %d: %d agents, each average of %d friend(s), %d unfriend(s), %d people known" %
                        (timestep, num_online, total_friends / num_online, total_enemies / num_online,
                         affinity_entries / num_online))
        self.logger.log(3, "Relationship between online agents 0 and 1 (degrees of separation): %r" %
                        (find_degrees_of_separation(self.online_agents[0], self.online_agents[1])))

        # Randomly pick a couple pairs of agents and check to see how many degrees of separation there are between
        # those two agents.
        num_users_to_average_separation = int(len(self.online_agents) / 200)
        deg_sep = 0
        unknowns = 0
        for x in range(num_users_to_average_separation):
            a1 = random.randint(0, len(self.online_agents)-1)
            a2 = a1
            while a2 == a1:
                a2 = random.randint(0, len(self.online_agents)-1)
            sep = find_degrees_of_separation(self.online_agents[a1], self.online_agents[a2])
            if sep is not None:
                deg_sep += sep
            else:
                unknowns += 1

        if num_users_to_average_separation != unknowns:
            deg_sep = int(deg_sep / (num_users_to_average_separation - unknowns))

        self.logger.log(3, "%d random user pairs whom have a chain of connection, the average length of"
                        " that chain is %d.  %d had no path to other agent." %
                        (num_users_to_average_separation, deg_sep, unknowns))

        self.logger.log(3, "There were %d messages sent and %d messages received this round." %
                        (self.messages_sent, self.messages_received))

        self.logger.log(3, "------------")
        self.total_messages_received += self.messages_received
        self.total_messages_sent += self.messages_sent
        self.messages_sent = 0
        self.messages_received = 0

    def generate_visualizations(self, x):
        total_friends = 0
        total_enemies = 0
        affinity_entries = 0

        for agent in self.online_agents:
            total_friends += len(agent.friends)
            total_enemies += len(agent.enemies)
            affinity_entries += len(agent.affinity_map)

        likeness = 0.0
        
        if len(self.visualizerOptions) == 0 or V.VType.avgLikenessGraph in self.visualizerOptions:
            for agent in self.agents:
                for agentA in agent.affinity_map:
                    likeness += agent.affinity_map[agentA]
                
        friendDistance = 0.0
        
        if len(self.visualizerOptions) == 0 or V.VType.avgFriendsDistanceGraph in self.visualizerOptions:
            for agent in self.agents:
                if len(agent.friends) != 0:
                    friendsDist = 0.0
                    for friend in agent.friends:
                        friendsDist += find_distance(agent, friend)
                
                    friendDistance += friendsDist / len(agent.friends)
            
        enemyDistance = 0.0
        
        if len(self.visualizerOptions) == 0 or V.VType.avgEnemiesDistanceGraph in self.visualizerOptions:
            for agent in self.agents:
                if len(agent.enemies) != 0:
                    enemiesDist = 0.0
                    for enemy in agent.enemies:
        	            enemiesDist += find_distance(agent, enemy)
                
                    enemyDistance += enemiesDist / len(agent.enemies)
                
        edges = []
        
        if len(self.visualizerOptions) == 0 or V.VType.mainNodesGraph in self.visualizerOptions:
            for agent in self.agents:
                for person in agent.affinity_map:
                    edges.append({(agent, person): agent.affinity_map[person]})
      
        totalPath = 0.0
        pathCount = 0
      
        if len(self.visualizerOptions) == 0 or V.VType.avgShortestPathGraph in self.visualizerOptions:  
            for agent1 in self.agents:
                for agent2 in self.agents:
                    if agent1 != agent2 and agent1.online and agent2.online:
                        path = find_degrees_of_separation(agent1, agent2)
                        
                        if path != None:
                            totalPath += path
                            pathCount += 1
        else:
            pathCount = 1.0
        
        V.Visualizer.sharedVisualizer.addNodesAndEdges(self.agents, edges)  
        V.Visualizer.sharedVisualizer.addPostsSent(self.messages_sent)
        V.Visualizer.sharedVisualizer.addAvgFriends(float(total_friends) / len(self.agents))
        V.Visualizer.sharedVisualizer.addAvgIgnored(float(total_enemies) / len(self.agents))
        V.Visualizer.sharedVisualizer.addAvgLikeness(likeness / len(self.agents))
        V.Visualizer.sharedVisualizer.addAvgFriendsDistance(friendDistance / len(self.agents))
        V.Visualizer.sharedVisualizer.addAvgIgnoredDistance(enemyDistance / len(self.agents))
        V.Visualizer.sharedVisualizer.addOnlinePeople(len(self.online_agents))
        V.Visualizer.sharedVisualizer.addAvgShortestPath(totalPath / pathCount)
        V.Visualizer.sharedVisualizer.addPersonalityTypes(self.agents)


def find_degrees_of_separation(agent1, agent2):
    """
    Finds the degrees of separation (number of intermediary friends) between two
    agents.

    :param agent1: first agent
    :param agent2: second agent
    :return: returns integer containing the count of intermediate friends between agent1 and agent2
    or, if no relationship is found between the two agents, None is returned.
    """

    # Perform breadth-first search to see if we can find agent2 starting from agent1
    if agent1 == agent2:
        return None
    
    if not agent1.friends:
        return None

    checked = set()

    queue = list(agent1.friends)
    separation = 0
    while (queue):
        if agent2 in queue:
            return separation
        separation += 1
        oldqueue = queue
        checked.update(oldqueue)
        queue = []
        for person in oldqueue:
            if person.friends:
                queue.extend([x for x in list(person.friends) if x not in checked])

    # No relationship found
    return None


def find_distance(agent1, agent2):
    """
    :param agent1: first agent
    :param agent2: second agent
    :return: distance (in miles) between agent1 and agent2

    Taken from http://andrew.hedges.name/experiments/haversine/
    Permission granted by terms specified on source page
    """
    dlon = math.radians(agent1.location[0]) - math.radians(agent2.location[0])
    dlat = math.radians(agent1.location[1]) - math.radians(agent2.location[1])
    a = (math.sin(dlat / 2)) ** 2 + math.cos(math.radians(agent1.location[1])) * \
         math.cos(math.radians(agent2.location[1])) * (math.sin(dlon / 2)) ** 2
    c = 2 * math.atan2(a ** .5, (1 - a) ** .5)
    return 3961 * c

if __name__ == "__main__":
    m = Model(time_to_run=20, num_agents=200, force_personalities=PersonalityShaping.personality_shaping_flexible,
              visualizer = False, visualizerOptions=[])

    m.personality_shaping = {
        'ranges': 'probabilistic',
        'definitions': [(20, [PersonalityShaping.introvert]),
                        (20, [PersonalityShaping.extrovert]),
                        (20, [PersonalityShaping.netrual]),
                        (20, [PersonalityShaping.creep]),
                        (20, [PersonalityShaping.post_abuser])]
        }

    m.run_simulation()
