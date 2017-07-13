"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

Module to allow batch processing of simulations and averaging of results over a multiple
test runs.
"""

import Model
import DataExporter
import numpy as np
import Personality
import Person
import networkx as nx
import matplotlib.pyplot as plt
import random


class AnalysisAggregator(object):
    """
    Class to allow the averaging of results over multiple test runs
    """
    def __init__(self):
        self.results = []

    def reset(self):
        self.results = []

    def collector(self, model, round_totals, data_map):
        self.results.append(round_totals)

    def collector_with_data_map(self, model, round_totals, data_map):
        self.results.append((round_totals, data_map))

    #---------------------------------------------------
    # These methods are different ways that session data can be returned.
    # New methods for different types of processing may be added as needed
    def return_overall_averages(self, final_only = False):
        """
        Returns the average results over multiple test runs

        :param final_only: Whether to only consider the last round of the simulation in the averages
        :return: tuple of averaged result data
        """
        result_array = np.zeros((len(self.results),5))
        for x in range(len(self.results)):
            test = self.results[x]
            if final_only == True:
                test = (test[-1],)

            for round in test:
                result_array[x, 0] += round['num_messages_sent'] / round['num_online_agents']
                result_array[x, 1] += round['num_messages_received'] / round['num_online_agents']
                result_array[x, 2] += round['num_total_friend'] / round['num_online_agents']
                result_array[x, 3] += round['num_total_enemies'] / round['num_online_agents']
                result_array[x, 4] += round['num_knowledge'] / round['num_online_agents']

            result_array = result_array / len(test)

        return (np.average(result_array[:, 0]), np.std(result_array[:, 0]),
                np.average(result_array[:, 1]), np.std(result_array[:, 1]),
                np.average(result_array[:, 2]), np.std(result_array[:, 2]),
                np.average(result_array[:, 3]), np.std(result_array[:, 3]),
                np.average(result_array[:, 4]), np.std(result_array[:, 4]))

    def return_raw_data(self, final_only=False):
        """
        Returns the complete data as returned by the DataExporter module
        :param final_only: Not used (but provided as part of the data return interface)
        :return: Raw data provided by DataExporter
        """
        return self.results
    # End of data processing/session data returning methods
    # ---------------------------------------------------

    def simple_exec(self, reset = True, repeat = 3, modifications = None, final_only = False,
                    processor = return_overall_averages, **kwargs):
        """
        :param reset: Whether to reset the rest results from previous executions
        :param repeat: Number of times to repeat the test
        :param modifications: A list of variable changes that are desired for this test run
        :param final_only: Whether to only consider the final round of the test results
        :param processor: Function to use to process the resultant data
        :param kwargs: Arguments to pass onto model.py
        :return: data as provided by the specified processor
        """
        if reset == True:
            self.reset()

        for x in range(repeat):
            m = Model.Model(**kwargs)
            restore = []

            if modifications != None:
                for mod in modifications:
                    if hasattr(mod[0], '__call__'):
                        mod[0](m)
                    else:
                        restore.append((mod[0], eval(mod[0])))
                        exec("%s=%s" % (mod[0], mod[1]))
            m.run_simulation()

            for item in restore:
                exec("%s=%s" % (item[0], item[1]))

        return processor(self, repeat, final_only=final_only)

# Utility report functions


def build_node_graph_affinities(dataset):
    """
    Produce networkX graph of each node based on affinity data
    :param dataset: data as provided by the DataExporter
    :return: networkX graph
    """
    graph = nx.Graph()
    nodes = list(dataset.keys())
    for node in nodes:
        if dataset[node]['rounds'][-1]['online'] == True:
            posx, posy = dataset[node]['location']
            graph.add_node(node, posxy=(posx+180, posy+90))

            edges = dataset[node]['rounds'][-1]['affinity_map']
            for second_node, affinity in edges.items():
                if affinity < 0:
                    color = 'r'
                else:
                    color = 'k'

                if affinity != 0:
                    graph.add_edge(node, second_node, color=color, weight=abs(affinity))
    return graph


def build_node_graph_friends(dataset):
    """
    Produce networkX graph of each node based on friend/enemy data
    :param dataset: data as provided by the DataExporter
    :return: networkX graph
    """
    graph = nx.Graph()
    nodes = list(dataset.keys())
    for node in nodes:
        if dataset[node]['rounds'][-1]['online'] == True:
            posx, posy = dataset[node]['location']
            graph.add_node(node, posxy=(posx+180, posy+90))

            edges = dataset[node]['rounds'][-1]['friends']
            for second_node in edges:
                graph.add_edge(node, second_node, color='k', weight = .3)

            edges = dataset[node]['rounds'][-1]['enemies']
            for second_node in edges:
                graph.add_edge(node, second_node, color='r', weight = .1)
    return graph


def save_graph(graph_sets, dpi=300):
    """
    :param graph_sets: tuple containing neworkX graph and name of file for which to save
    :param dpi: dpi of image to save
    :return: nothing
    """
    for x in range(len(graph_sets)):
        normalize_weights = graph_sets[x][2]
        graph = graph_sets[x][0]
        name = graph_sets[x][1]
        fig = plt.figure(x+1)
        plt.title(name)
        edges = graph.edges()
        colors = [graph[u][v]['color'] for u, v in edges]
        weights = [graph[u][v]['weight'] for u, v in edges]
        positions = nx.get_node_attributes(graph, 'posxy')
        if normalize_weights == True:
            max_weight = max(weights)
            weights = [x / (max_weight) for x in weights]
        nx.draw(graph, positions, edges=edges, edge_color=colors, width=weights, node_size=20)
        plt.savefig(name+".png", dpi=dpi)
        plt.close(fig)


def save_line_graph(xvals, yvals, name, ylabel, xlabel, show = False, dpi=300):
    """
    Function to create and save a line graph
    :param xvals: x values of graph
    :param yvals: y values of graph
    :param name: Title of graph and filename to save graph
    :param ylabel: label for y axis
    :param xlabel: label for x axis
    :param show: whether to display the graph to screen
    :param dpi: dpi of file to save
    :return: nothing
    """
    fig=plt.figure()
    plt.title(name)
    plt.plot(xvals, yvals)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(name + ".png", dpi=dpi)
    if show == True:
        plt.show()
    plt.close(fig)

#----------
# demonstration of using data export/aggregation

# Plot behavior of model as the number of people who are "famous" change

g = []
a = AnalysisAggregator()
famous_values = [0, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]
average_values = []

for value in famous_values:
    results = a.simple_exec(modifications=(("Personality.percent_probability_famous", value),),
                                      num_agents=40, topics=20, data_collector=DataExporter.DataExporter,
                                      time_to_run=20, data_collector_results=a.collector_with_data_map, log_level=10,
                                      processor=AnalysisAggregator.return_raw_data, repeat=1)
    g.append((build_node_graph_affinities(results[0][1]), "Famous %d%% Affinities" % value, True))
    g.append((build_node_graph_friends(results[0][1]), "Famous %d%% Friendships" % value, False))

    results = a.simple_exec(modifications=(("Personality.percent_probability_famous", value),),
                            num_agents=100, topics=20, data_collector=DataExporter.DataExporter,
                            time_to_run=20, data_collector_results=a.collector, log_level=10,
                            processor=AnalysisAggregator.return_overall_averages, repeat=10, final_only = True)
    average_values.append(results[4])  # average number of friends

save_line_graph(famous_values, average_values, "100 Agents - Famous Percent vs Average Friend Count",
                ylabel="Number of Friends", xlabel = "Percent of Population Famous")
save_graph(g)


# Plot the behavior of the model as the number of extroverts vs introverts changes
g = []
a = AnalysisAggregator()
current_run = 0
extrovert_percentage = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
average_values = []

def set_intovert_extrovert_traits(model):
    extroverts = extrovert_percentage[current_run]
    for x in range(len(model.agents)):
        agent = model.agents[x]
        if x < extroverts * len(model.agents) / 100:
            agent.personality.repost_probability = (random.random() * .5) + 0.5
            agent.personality.post_probability = (random.random() * .5) + 0.5
            agent.personality.fame = 100 if random.random() < .80 else agent.personality.fame
            agent.personality.probability_read_reposts = (random.random() * .5) + 0.3
        else:
            agent.personality.repost_probability = random.random() * .5
            agent.personality.post_probability = random.random() * .3
            agent.personality.fame = 100 if random.random() < .95 else agent.personality.fame
            agent.personality.probability_read_reposts = random.random() * .3

for value in extrovert_percentage:
    results = a.simple_exec(force_personalities = set_intovert_extrovert_traits,
                                      num_agents=40, topics=20, data_collector=DataExporter.DataExporter,
                                      time_to_run=20, data_collector_results=a.collector_with_data_map, log_level=10,
                                      processor=AnalysisAggregator.return_raw_data, repeat=1)
    g.append((build_node_graph_affinities(results[0][1]), "Extrovert %d%% Affinities" % value, True))
    g.append((build_node_graph_friends(results[0][1]), "Extrovert %d%% Friendships" % value, False))

    results = a.simple_exec(force_personalities = set_intovert_extrovert_traits,
                            num_agents=100, topics=20, data_collector=DataExporter.DataExporter,
                            time_to_run=20, data_collector_results=a.collector, log_level=10,
                            processor=AnalysisAggregator.return_overall_averages, repeat=10, final_only = True)
    average_values.append(results[4])  # average number of friends
    current_run += 1

save_line_graph(extrovert_percentage, average_values, "100 Agents Extrovert Percent vs Average Friend Count",
                ylabel="Number of Friends", xlabel = "Percent of Population Extroverted")
save_graph(g)



"""

This code will print a simple table of the statistics that come out of return_overall_averages

print("Test           Sent      Dev       Resent      Dev         Friend      Dev         Enemy       Dev         Known       Dev")
for result in result_list:
    print("%s %10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t" %
          (result[0], result[1][0],result[1][1],result[1][2],result[1][3],result[1][4],result[1][5]
           , result[1][6],result[1][7],result[1][8],result[1][9]))
"""