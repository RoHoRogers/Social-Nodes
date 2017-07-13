import numpy as N
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import TimeManager as TM
import pylab as pl
import Model as M
import Person as P

from enum import Enum

class VType(Enum):
    allGraphs = 0
    mainNodesGraph = 1
    friendsNodesGraph = 2
    enemiesNodesGraph = 3
    postsSentGraph = 4
    avgFriendsGraph = 5
    avgEnemiesGraph = 6
    avgLikenessGraph = 7
    avgFriendsDistanceGraph = 8
    avgEnemiesDistanceGraph = 9
    onlinePeopleGraph = 10
    avgShortestPathGraph = 11
    personalityGraphs = 12

class VItem(object):
    item = None
    time = 0.0
    
    def __init__(self, item, time):
        self.item = item
        self.time = time

class Visualizer(object):
    """
    Class which shows most of the data in graph format. It shows only one nodes graph at a time,
    but it can show multiple bar and line graphs. 
    """
    
    sharedVisualizer = None
    sharedVisualizers = []
    
    mainGraph = nx.Graph()
    
    mainGraphFig = None
    
    postsSentFig = None
    postsSent = []
    
    postsSharedFig = None
    postsShared = []
    
    avgFriendsFig = None
    avgFriends = []
    
    avgIgnoredFig = None
    avgIgnored = []
    
    avgLikenessFig = None
    avgLikeness = []
    
    avgFriendsDistanceFig = None
    avgFriendsDistance = []
    
    avgIgnoredDistanceFig = None
    avgIgnoredDistance = []
    
    avgMissedFig = None
    avgMissed = []
    
    onlinePeopleFig = None
    onlinePeople = []
    
    avgShortestPathFig = None
    avgShortestPath = []
    
    graphs = []
    nodes = []
    edges = {}
    
    acceptedTypes = []
    lastNodesGraph = []
    
    showAtEnd = False
    
    @staticmethod
    def createVisualizer(types=[], showAtEnd=False):
        """
        Creates the visualizer that is going to be updated by other objects.
        
        types: enum types that are wanted to be represented
        showAtEnd: boolean to decide if graphs are shown during or after the simulation
        """
        
        Visualizer.sharedVisualizer = Visualizer(types=types, showAtEnd=showAtEnd)
        Visualizer.sharedVisualizers.append(Visualizer.sharedVisualizer)
        
    @staticmethod
    def showWithPersonalities(personalities):
        """
        At the end of multiple simulations, show data in comparison to personality types.
        
        personalities: list of string naming the personalities.
        """
        
        #edges
        edges = []
        for visualizer in Visualizer.sharedVisualizers:
            edges.append(len(visualizer.lastNodesGraph[1]))
            
        plt.figure()
        plt.title("# of connections")
        plt.bar(range(len(edges)), edges, align="center")
        plt.xticks(range(len(edges)), personalities, size="small")
        
        plt.show()
        
        #posts sent
        postsSent = []
        for visualizer in Visualizer.sharedVisualizers:
            postsSent.append(N.sum(N.array(visualizer.postsSent)))
            
        plt.figure()
        plt.title("Total posts sent")
        plt.bar(range(len(postsSent)), postsSent, align="center")
        plt.xticks(range(len(postsSent)), personalities, size="small")
        
        #friends
        friends = []
        for visualizer in Visualizer.sharedVisualizers:
            friends.append(visualizer.avgFriends[-1])
            
        plt.figure()
        plt.title("Average # of friends")
        plt.bar(range(len(friends)), friends, align="center")
        plt.xticks(range(len(friends)), personalities, size="small")
        
        #enemies
        enemies = []
        for visualizer in Visualizer.sharedVisualizers:
            enemies.append(visualizer.avgIgnored[-1])
            
        plt.figure()
        plt.title("Average # of enemies")
        plt.bar(range(len(enemies)), enemies, align="center")
        plt.xticks(range(len(enemies)), personalities, size="small")
        
        #likeness
        likeness = []
        for visualizer in Visualizer.sharedVisualizers:
            likeness.append(visualizer.avgLikeness[-1])
            
        plt.figure()
        plt.title("Average post likeness")
        plt.bar(range(len(likeness)), likeness, align="center")
        plt.xticks(range(len(likeness)), personalities, size="small")
        
        #friends distance
        friendsDistance = []
        for visualizer in Visualizer.sharedVisualizers:
            friendsDistance.append(visualizer.avgIgnoredDistance[-1])
            
        plt.figure()
        plt.title("Average friend distance")
        plt.bar(range(len(friendsDistance)), friendsDistance, align="center")
        plt.xticks(range(len(friendsDistance)), personalities, size="small")
        
        #enemies distance
        enemiesDistance = []
        for visualizer in Visualizer.sharedVisualizers:
            enemiesDistance.append(visualizer.avgIgnoredDistance[-1])
            
        plt.figure()
        plt.title("Average enemy distance")
        plt.bar(range(len(enemiesDistance)), enemiesDistance, align="center")
        plt.xticks(range(len(enemiesDistance)), personalities, size="small")
        
        #path distance
        paths = []
        for visualizer in Visualizer.sharedVisualizers:
            paths.append(visualizer.avgShortestPath[-1])
            
        plt.figure()
        plt.title("Average shortest path")
        plt.bar(range(len(paths)), paths, align="center")
        plt.xticks(range(len(paths)), personalities, size="small")
        
        plt.show()
        
    def __init__(self, types=[], showAtEnd=False):
        """
        Constructor to initialize a visualizer.
        
        types: enum for graphs that need to be shown.
        showAtEnd: boolean for showing graphs during or after simulation.
        """
        
        self.acceptedTypes = types[:]
        self.lastNodesGraph = []
        
        self.showAtEnd = showAtEnd
        
        if len(types) == 0 or (VType.mainNodesGraph in types) or (VType.friendsNodesGraph in types) or (VType.enemiesNodesGraph in types):
            self.mainGraphFig = plt.figure()
        
        if len(types) == 0 or VType.postsSentGraph in types:
            self.postsSentFig = plt.figure()
            self.postsSent = []
        
        #self.postsSharedFig = plt.figure()
        #self.postsShared = []
        
        if len(types) == 0 or VType.avgFriendsGraph in types:
            self.avgFriendsFig = plt.figure()
            self.avgFriends = []
        
        if len(types) == 0 or VType.avgEnemiesGraph in types:
            self.avgIgnoredFig = plt.figure()
            self.avgIgnored = []
        
        if len(types) == 0 or VType.avgLikenessGraph in types:
            self.avgLikenessFig = plt.figure()
            self.avgLikeness = []
        
        if len(types) == 0 or VType.avgFriendsDistanceGraph in types:
            self.avgFriendsDistanceFig = plt.figure()
            self.avgFriendsDistance = []
        
        if len(types) == 0 or VType.avgEnemiesDistanceGraph in types:
            self.avgIgnoredDistanceFig = plt.figure()
            self.avgIgnoredDistance = []
        
        #self.avgMissedFig = plt.figure()
        #self.avgMissed = []
        
        if len(types) == 0 or VType.onlinePeopleGraph in types:
            self.onlinePeopleFig = plt.figure()
            self.onlinePeople = []

        if len(types) == 0 or VType.avgShortestPathGraph in types:    
            self.avgShortestPathFig = plt.figure()
            self.avgShortestPath = []
            
        if len(types) == 0 or VType.personalityGraphs in types:
            self.personalityPostsSentFig = plt.figure()
            self.personalityPostsSent = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            
            self.personalityConnectionsFig = plt.figure()
            self.personalityConnections = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            
            self.personalityFriendsFig = plt.figure()
            self.personalityFriends = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            
            self.personalityEnemiesFig = plt.figure()
            self.personalityEnemies = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            
            self.personalityFriendsDistanceFig = plt.figure()
            self.personalityFriendsDistance = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            
            self.personalityEnemiesDistanceFig = plt.figure()
            self.personalityEnemiesDistance = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    
    def addNode(self, node):
        item = VItem(node, TM.TimeManager.sharedManager.time)
        self.nodes.append(item)
        
        if len(self.graphs) == TM.TimeManager.sharedManager.time:
            self.graphs.append(nx.Graph())
        else:
            self.graphs[-1].add_node(node)
        
        #self.updateMainGraph(node=node)
        
    def addNodesAndEdges(self, nodes, edges):
        """
        Add new people and connections to the main graph.
        The nodes and edges will only be stored.
        
        The edges is a list with this format: [{(node1, node2): weight}, ...]
        
        nodes: list of people that need to be displayed
        edges: list of connection dictionaries with their weights
        """
        
        if len(self.acceptedTypes) == 0 or (VType.mainNodesGraph in self.acceptedTypes) or (VType.friendsNodesGraph in self.acceptedTypes) or (VType.enemiesNodesGraph in self.acceptedTypes):
            graph = nx.Graph()
            widths = []
            colors = []
            
            self.lastNodesGraph = []
        
            for node in nodes:
                graph.add_node(node)
            
            for edge in edges:
                firstNode = list(edge.keys())[0][0]
                secondNode = list(edge.keys())[0][1]
                
                if (not ((firstNode, secondNode) in graph.edges())) and \
                    (not ((secondNode, firstNode) in graph.edges())):
                
                    weight = edge[edge.keys()[0]] / 54 * 6
                    #wRange = ((edge[edge.keys()[0]] - minWeight) * 4) / (maxWeight - minWeight)
                    #weight = wRange - 2
                    
                    if weight > 6.0:
                        weight = 6.0
                    elif weight < -6.0:
                        weight = 6.0
                
                    #Color code the lines
                    if ((VType.friendsNodesGraph in self.acceptedTypes) and weight >= 4) or ((VType.enemiesNodesGraph in self.acceptedTypes) and weight >= -6 and weight < -4) or (VType.mainNodesGraph in self.acceptedTypes) or (len(self.acceptedTypes) == 0):
                        
                        if weight >= 4:
                            colors.append("g")
                        elif weight >= 0:
                            colors.append("#96ba07")
                        elif weight >= -4:
                            colors.append("#f59f0a")
                        elif weight >= -6:
                            colors.append("r")
                        
                        weight /= 6.0
                        graph.add_edge(firstNode, secondNode, weight=weight)
                
                        widths.append(weight)
            
            #Append for storage of last state
            self.lastNodesGraph.append(graph)
            self.lastNodesGraph.append(widths)
            self.lastNodesGraph.append(colors)
            
            if not self.showAtEnd:
                self.updateGraph(graph, widths, colors)
            
            #self.pause()
        
    def addPostsSent(self, postsSent):
        """
        Adds a number of posts that has been sent to be stored for later displaying.
        
        postsSent: number of posts
        """
        
        if len(self.acceptedTypes) == 0 or (VType.postsSentGraph in self.acceptedTypes):
            self.postsSent.append(postsSent)
            
            if not self.showAtEnd:
                self.updatePostsSentTimeGraph()
            
            #self.pause()
    
    def addPersonalityTypes(self, agents):
        """
        Stores all of the needed data for each personality.
        
        agents: list of Person objects
        """
        
        if len(self.acceptedTypes) == 0 or (VType.personalityGraphs in self.acceptedTypes):
            for agent in agents:
                self.personalityPostsSent[agent.p_type - 1] += agent.posts_sent
                self.personalityConnections[agent.p_type - 1] += len(agent.affinity_map)
                self.personalityFriends[agent.p_type - 1] += len(agent.friends)
                self.personalityEnemies[agent.p_type - 1] += len(agent.enemies)
                
                friendsDistance = 0.0
                for friend in agent.friends:
                    friendsDistance += M.find_distance(agent, friend)
                    
                enemiesDistance = 0.0
                for enemy in agent.enemies:
                    enemiesDistance += M.find_distance(agent, enemy)
                
                if len(agent.friends) != 0:
                    self.personalityFriendsDistance[agent.p_type - 1] += friendsDistance / len(agent.friends)
                if len(agent.enemies) != 0:
                    self.personalityEnemiesDistance[agent.p_type - 1] += enemiesDistance / len(agent.enemies)
                
            self.personalityConnections = (N.array(self.personalityConnections) / N.array(P.categoryNumOfPeople(agents))).tolist()
            self.personalityFriends = (N.array(self.personalityFriends) / N.array(P.categoryNumOfPeople(agents))).tolist()
            self.personalityEnemies = (N.array(self.personalityEnemies) / N.array(P.categoryNumOfPeople(agents))).tolist()
            self.personalityFriendsDistance = (N.array(self.personalityFriendsDistance) / N.array(P.categoryNumOfPeople(agents))).tolist()
            self.personalityEnemiesDistance = (N.array(self.personalityEnemiesDistance) / N.array(P.categoryNumOfPeople(agents))).tolist()
            self.updatePersonalityGraphs()
        
    def addPostsShared(self, postsShared):
        """
        Adds a number of posts that has been shared to be stored for later displaying.
        
        postsShared: number of posts
        """
        
        self.postsShared.append(postsShared)
        
        self.updatePostsSharedTimeGraph()
        
    def addAvgFriends(self, friends):
        """
        Adds a number of friends to be stored for later displaying.
        
        friends: number of friends in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgFriendsGraph in self.acceptedTypes):
            self.avgFriends.append(friends)
            
            if not self.showAtEnd:
                self.updateAvgFriendsGraph()
            
            #self.pause()
        
    def addAvgIgnored(self, ignored):
        """
        Adds a number of enemies to be stored for later displaying.
        
        enemies: number of enemies in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgEnemiesGraph in self.acceptedTypes):
            self.avgIgnored.append(ignored)
        
            if not self.showAtEnd:
                self.updateAvgIgnoredGraph()
            
            #self.pause()
        
    def addAvgLikeness(self, likeness):
        """
        Adds a connection likeness to be stored for later displaying.
        
        likeness: likeness in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgLikenessGraph in self.acceptedTypes):
            self.avgLikeness.append(likeness)
            
            if not self.showAtEnd:
                self.updateAvgLikenessGraph()
            
            #self.pause()
        
    def addAvgFriendsDistance(self, distance):
        """
        Adds a distance among friends to be stored for later displaying.
        
        distance: distance among friends in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgFriendsDistanceGraph in self.acceptedTypes):
            self.avgFriendsDistance.append(distance)
            
            if not self.showAtEnd:
                self.updateAvgFriendsDistanceGraph()
            
            #self.pause()
        
    def addAvgIgnoredDistance(self, distance):
        """
        Adds a distance among enemies to be stored for later displaying.
        
        distance: distance among enemies in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgEnemiesDistanceGraph in self.acceptedTypes):
            self.avgIgnoredDistance.append(distance)
            
            if not self.showAtEnd:
                self.updateAvgIgnoredDistanceGraph()
            
            #self.pause()
        
    def addAvgMissed(self, missed):
        self.avgMissed.append(missed)
        
        self.updateAvgMissedGraph()
        
    def addOnlinePeople(self, people):
        """
        Adds number of online people to be stored for later displaying.
        
        people: num of online people in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.onlinePeopleGraph in self.acceptedTypes):
            self.onlinePeople.append(people)
        
            if not self.showAtEnd:
                self.updateOnlinePeopleGraph()
            
            #self.pause()
            
    def addAvgShortestPath(self, path):
        """
        Adds the shortest path to be stored for later displaying.
        
        path: shortest path to everyone in a certain round on average per person.
        """
        
        if len(self.acceptedTypes) == 0 or (VType.avgShortestPathGraph in self.acceptedTypes):
            self.avgShortestPath.append(path)
        
            if not self.showAtEnd:
                self.updateAvgShortestPathGraph()
        
    def connect(self, fromNode, toNode, weight):
        if (toNode, fromNode) in self.edges.keys():
            self.edges[(toNode, fromNode)] = weight
            
            self.mainGraph.remove_edge(toNode, fromNode)
            self.mainGraph.add_edge(toNode, fromNode, weight=weight)
            
            #self.updateMainGraph(edge={(toNode, fromNode): weight})
            
        elif (fromNode, toNode) in self.edges.keys():
            self.edges[(fromNode, toNode)] = weight
            
            self.mainGraph.remove_edge(fromNode, toNode)
            self.mainGraph.add_edge(fromNode, toNode, weight=weight)
            
            #self.updateMainGraph(edge={(fromNode, toNode): weight})
            
        else:
            self.edges[(fromNode, toNode)] = weight
            self.mainGraph.add_edge(fromNode, toNode, weight=weight)
            
            #self.updateMainGraph(edge={(fromNode, toNode): weight})
    
    def updateGraph(self, graph, widths, edgeColors):
        """
        Shows the main nodes graph. 
        
        Depending on the options, it will show all of the nodes, only the friends,
        or only the enemies.
        
        graph: nx graph to show
        widths: list of widths of each connection
        edgeColors: list of string of color of each connection
        """
        
        plt.figure(self.mainGraphFig.number)
        self.mainGraphFig.clear()
        
        nodes = graph.nodes()
        
        positions = {}
        for node in nodes:
            positions[node] = (node.location[0], node.location[1])
            
        colors = []
        for node in nodes:
            if node.online:
                if node.p_type == 1:
                    colors.append("g")
                elif node.p_type == 2:
                    colors.append("#0080ff")
                elif node.p_type == 3:
                    colors.append("#cccc00")
                elif node.p_type == 4:
                    colors.append("#000000")
                elif node.p_type == 5:
                    colors.append("#a0a0a0")
                elif node.p_type == 6:
                    colors.append("#990099")
                elif node.p_type == 7:
                    colors.append("#ff66b2")
            else:
                colors.append("r")
        
        #if len(widths) != 0:
        pos=nx.fruchterman_reingold_layout(graph)
        nx.draw(graph, ax=self.mainGraphFig.add_subplot(111), pos=positions, width=widths, node_color=colors, \
        edge_color=edgeColors)
        
        self.mainGraphFig.show()
        
        patch1 = mpatches.Patch(color='g', label='Introvert')
        patch2 = mpatches.Patch(color='#0080ff', label='Extrovert')
        patch3 = mpatches.Patch(color='#cccc00', label='Neutral')
        patch4 = mpatches.Patch(color='#000000', label='Creep')
        patch5 = mpatches.Patch(color='#a0a0a0', label='Post abuser')
        patch6 = mpatches.Patch(color='#990099', label='Friend-Dependent')
        patch7 = mpatches.Patch(color='#ff66b2', label='Friend-Independent')
        patch8 = mpatches.Patch(color='r', label='Offline')
        plt.legend(handles=[patch1, patch2, patch3, patch4, patch5, patch6, patch7, patch8])
        
        plt.title("Nodes-connections graph")
            
        plt.pause(0.01)
            
    def updatePostsSentTimeGraph(self):
        """
        Shows the posts sent vs round graph.
        """
        
        plt.figure(self.postsSentFig.number)
        
        self.postsSentFig.clear()
        sub = self.postsSentFig.add_subplot(111)
        sub.plot(range(len(self.postsSent)), self.postsSent)
        sub.set_title("Posts sent vs time")
        self.postsSentFig.show()
        
        plt.pause(0.01)
        
    def updatePostsSharedTimeGraph(self):
        """
        Shows the posts shared vs round graph.
        """
        
        plt.figure(self.postsSharedFig.number)
        
        self.postsSharedFig.clear()
        sub = self.postsSharedFig.add_subplot(111)
        sub.plot(range(len(self.postsShared)), self.postsShared)
        sub.set_title("Posts shared vs time")
        self.postsSharedFig.show()
        
        plt.pause(0.01)
        
    def updateAvgFriendsGraph(self):
        """
        Shows the average num of friends vs round graph.
        """
        
        plt.figure(self.avgFriendsFig.number)
        
        self.avgFriendsFig.clear()
        sub = self.avgFriendsFig.add_subplot(111)
        sub.plot(range(len(self.avgFriends)), self.avgFriends)
        sub.set_title("Average # of friends vs time")
        self.avgFriendsFig.show()
        
        plt.pause(0.01)
        
    def updateAvgIgnoredGraph(self):
        """
        Shows the average num of enemies vs round graph.
        """
        
        plt.figure(self.avgIgnoredFig.number)
        
        self.avgIgnoredFig.clear()
        sub = self.avgIgnoredFig.add_subplot(111)
        sub.plot(range(len(self.avgIgnored)), self.avgIgnored)
        sub.set_title("Average # of enemies vs time")
        self.avgIgnoredFig.show()
        
        plt.pause(0.01)
        
    def updateAvgLikenessGraph(self):
        """
        Shows the average likeness value vs round graph.
        """
        
        plt.figure(self.avgLikenessFig.number)
        
        self.avgLikenessFig.clear()
        sub = self.avgLikenessFig.add_subplot(111)
        sub.plot(range(len(self.avgLikeness)), self.avgLikeness)
        sub.set_title("Average likeness level vs time")
        self.avgLikenessFig.show()
        
        plt.pause(0.01)
        
    def updateAvgFriendsDistanceGraph(self):
        """
        Shows the average distance of friends vs round graph.
        """
        
        plt.figure(self.avgFriendsDistanceFig.number)
        
        self.avgFriendsDistanceFig.clear()
        sub = self.avgFriendsDistanceFig.add_subplot(111)
        sub.plot(range(len(self.avgFriendsDistance)), self.avgFriendsDistance)
        sub.set_title("Average friend distance vs time")
        self.avgFriendsDistanceFig.show()
        
        plt.pause(0.01)
    
    def updateAvgIgnoredDistanceGraph(self):
        """
        Shows the average distance of enemies vs round graph.
        """
        
        plt.figure(self.avgIgnoredDistanceFig.number)
        
        self.avgIgnoredDistanceFig.clear()
        sub = self.avgIgnoredDistanceFig.add_subplot(111)
        sub.plot(range(len(self.avgIgnoredDistance)), self.avgIgnoredDistance)
        sub.set_title("Average enemies distance vs time")
        self.avgIgnoredDistanceFig.show()
        
        plt.pause(0.01)
        
    def updateAvgMissedGraph(self):
        plt.figure(self.avgMissedFig.number)
        
        self.avgMissedFig.clear()
        sub = self.avgMissedFig.add_subplot(111)
        sub.plot(range(len(self.avgMissed)), self.avgMissed)
        sub.set_title("Average missed opportunities vs time")
        self.avgMissedFig.show()
        
        plt.pause(0.01)
        
    def updateOnlinePeopleGraph(self):
        """
        Shows the num of online people vs round graph.
        """
        
        plt.figure(self.onlinePeopleFig.number)
        
        self.onlinePeopleFig.clear()
        sub = self.onlinePeopleFig.add_subplot(111)
        sub.plot(range(len(self.onlinePeople)), self.onlinePeople)
        sub.set_title("People becoming online vs time")
        self.onlinePeopleFig.show()
        
        plt.pause(0.01)
        
    def updateAvgShortestPathGraph(self):
        """
        Shows the average shortest path to everyone vs round graph.
        """
        
        plt.figure(self.avgShortestPathFig.number)
        
        self.avgShortestPathFig.clear()
        sub = self.avgShortestPathFig.add_subplot(111)
        sub.plot(range(len(self.avgShortestPath)), self.avgShortestPath)
        sub.set_title("Average shortest path to everyone vs time")
        self.avgShortestPathFig.show()
        
        plt.pause(0.01)
        
    def updatePersonalityGraphs(self):
        """
        Shows the graph for all of the data grouped in personality categories.
        
        Shows bar graphs, where each personality is in the x axis.
        """
        
        personalities = ["Introvert", "Extrovert", "Neutral", "Creep", "Post-Abuser", "Friend-Dep", "Friend-Indep"]
        
        plt.figure(self.personalityPostsSentFig.number)
        self.personalityPostsSentFig.clear()
        plt.title("Posts sent per personality")
        plt.bar(range(len(self.personalityPostsSent)), self.personalityPostsSent, align="center")
        plt.xticks(range(len(self.personalityPostsSent)), personalities, size="small")
        
        plt.figure(self.personalityConnectionsFig.number)
        self.personalityConnectionsFig.clear()
        plt.title("Connections per personality")
        plt.bar(range(len(self.personalityConnections)), self.personalityConnections, align="center")
        plt.xticks(range(len(self.personalityConnections)), personalities, size="small")
        
        plt.figure(self.personalityFriendsFig.number)
        self.personalityFriendsFig.clear()
        plt.title("# of friends per personality")
        plt.bar(range(len(self.personalityFriends)), self.personalityFriends, align="center")
        plt.xticks(range(len(self.personalityFriends)), personalities, size="small")
        
        plt.figure(self.personalityEnemiesFig.number)
        self.personalityEnemiesFig.clear()
        plt.title("# of enemies per personality")
        plt.bar(range(len(self.personalityEnemies)), self.personalityEnemies, align="center")
        plt.xticks(range(len(self.personalityEnemies)), personalities, size="small")
        
        plt.figure(self.personalityFriendsDistanceFig.number)
        self.personalityFriendsDistanceFig.clear()
        plt.title("Friends distance per personality")
        plt.bar(range(len(self.personalityFriendsDistance)), self.personalityFriendsDistance, align="center")
        plt.xticks(range(len(self.personalityFriendsDistance)), personalities, size="small")
        
        plt.figure(self.personalityEnemiesDistanceFig.number)
        self.personalityEnemiesDistanceFig.clear()
        plt.title("Enemies distance per personality")
        plt.bar(range(len(self.personalityEnemiesDistance)), self.personalityEnemiesDistance, align="center")
        plt.xticks(range(len(self.personalityEnemiesDistance)), personalities, size="small")
        
        plt.show()
        
    def updateEverything(self):
        """
        Shows all graphs only if the simulation doesn't produce real time graphs.
        """
        if self.showAtEnd:
            if len(self.acceptedTypes) == 0 or (VType.mainNodesGraph in self.acceptedTypes) or (VType.friendsNodesGraph in self.acceptedTypes) or (VType.enemiesNodesGraph in self.acceptedTypes):
                self.updateGraph(self.lastNodesGraph[0], self.lastNodesGraph[1], self.lastNodesGraph[2])
            if len(self.acceptedTypes) == 0 or (VType.postsSentGraph in self.acceptedTypes):
                self.updatePostsSentTimeGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgFriendsGraph in self.acceptedTypes):
                self.updateAvgFriendsGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgEnemiesGraph in self.acceptedTypes):
                self.updateAvgIgnoredGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgLikenessGraph in self.acceptedTypes):
                self.updateAvgLikenessGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgFriendsDistanceGraph in self.acceptedTypes):
                self.updateAvgFriendsDistanceGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgEnemiesDistanceGraph in self.acceptedTypes):
                self.updateAvgIgnoredDistanceGraph()
            if len(self.acceptedTypes) == 0 or (VType.onlinePeopleGraph in self.acceptedTypes):
                self.updateOnlinePeopleGraph()
            if len(self.acceptedTypes) == 0 or (VType.avgShortestPathGraph in self.acceptedTypes):
                self.updateAvgShortestPathGraph()
        
    def pause(self, time=0.5):
        plt.pause(time)
