"""
Created on Thu May 19 14:06:39 2016

@author: Kevin
"""

import networkx as nx
import matplotlib.pyplot as plt


G = nx.Graph()
G.add_edge(1,2,color='r',weight=2)
G.add_edge(2,3,color='b',weight=4)
G.add_edge(3,4,color='g',weight=6)
G.add_edge(3,5,color='b',weight=1)
G.add_edge(3,6,color='y',weight=3)
G.add_edge(3,7,color='g',weight=10)
G.add_edge(2,8,color='b',weight=4)

edges = G.edges()
colors = [G[u][v]['color'] for u,v in edges]
weights = [G[u][v]['weight'] for u,v in edges]

"""
Test for different layouts are commented out
**Using draw() will only allow them all to print out on a single graph
"""

pos = nx.fruchterman_reingold_layout(G)#<---- this is the one i was thinking of

#pos = nx.spectral_layout(G) <----- doubt this will be useful

#pos = nx.shell_layout(G)

#pos = nx.random_layout(G)

nx.draw(G, pos, edges=edges, edge_color=colors, width=weights)


"""
graph = nx.Graph()

graph.add_node(1)
graph.add_node(2)
graph.add_node(3)


"""

