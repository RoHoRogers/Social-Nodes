import networkx as nx
import matplotlib.pyplot as plt

graph = nx.Graph()

graph.add_node(1)
graph.add_node(2)

#edges
graph.add_edge(1,2, weight=5.0)

#positions
positions = {1:(1,2),
             2:(1,5),}

#drawing stuff
#nx.draw_networkx(graph)
nx.draw_networkx_nodes(graph, positions)
nx.draw_networkx_edges(graph, positions, width=5.0)
plt.show()