"""
CSS 458 Spring Quarter 2016
Social Nodes Project

Amritpal Sandhu, Billy Savanh, Kevin Rogers, and David Larsen

Module containing the necessary logic to export the states of the simulation for use in data analysis for
batch testing
"""

class DataExporter(object):
    def __init__(self, model, send_results = None):
        self.model = model
        self.data_map = {}
        self.round_totals = []
        self.last_seen_post_count = 0
        self.last_seen_recv_count = 0
        self.send_results = send_results

    def collector_turn(self, round, previous_person):
        if previous_person not in self.data_map.keys():
            facet_list = []
            next_facet = previous_person.personality.facets
            while (next_facet != None):
                facet_list.append(next_facet)
                next_facet = next_facet.next_facet

            self.data_map[previous_person] = {
                'personality': previous_person.personality,
                'facets': facet_list,
                'location': previous_person.location,
                'interests': previous_person.personality.interests,
                'post_prob': previous_person.personality.post_probability,
                'repost_prob': previous_person.personality.repost_probability,
                'prob_read_repost': previous_person.personality.probability_read_reposts,
                'fame': previous_person.personality.fame,
                'rounds': []
            }

        round = {
            'online': previous_person.online,
            'sent': (self.last_seen_post_count == self.model.messages_sent),
            'reposts': self.model.messages_received - self.last_seen_recv_count,
            'friends': set(previous_person.friends),
            'enemies': set(previous_person.enemies),
            'friends_count': len(previous_person.friends),
            'enemies_count': len(previous_person.enemies),
            'affinity_map': dict(previous_person.affinity_map)
        }

        self.data_map[previous_person]['rounds'].append(round)
        self.last_seen_post_count = self.model.messages_sent
        self.last_seen_recv_count = self.model.messages_received

    def collector_round(self, round):
        num_friends = 0
        num_enemies = 0
        num_knowledge_connections = 0
        for agent in self.model.online_agents:
            num_friends += len(agent.friends)
            num_enemies += len(agent.enemies)
            num_knowledge_connections += len(agent.affinity_map)


        round_total = {
            'num_messages_sent': self.last_seen_post_count,
            'num_messages_received': self.last_seen_recv_count,
            'num_online_agents': len(self.model.online_agents),
            'num_total_friend': num_friends,
            'num_total_enemies': num_enemies,
            'num_knowledge': num_knowledge_connections
        }

        self.round_totals.append(round_total)

        self.last_seen_post_count = 0
        self.last_seen_recv_count = 0

        #
        # Useful for debugging
        if len(self.data_map) < 40:
            print ("uhoh")
            print (len(self.data_map))
            print (len(self.data_map.keys()))
            print ("----")
            print (self.col_ran)
            print (self.data_map.keys())
            print("*")
            print (len(self.model.agents))
            print("*")
            print (self.model.agents)
            x = [x for x in self.model.agents if x not in self.data_map.keys()]
            print (x)
            for xx in x:
                print (xx.online)
                print (self.model.agents.index(xx))
            exit()
        #

    def finalize(self):
        #print (self.data_map)
        #print (self.round_totals)
        if self.send_results != None:
            self.send_results(self.model, self.round_totals, self.data_map)
