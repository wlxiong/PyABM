# find the shortest path
from collections import deque
from collections import defaultdict
import itertools
from utils import logger, constant_factory, Time
from pprint import pprint
from config import Config

class Router(object):
    @classmethod
    def create_all_shortest_paths(cls, start, prev, time):
        # create a nested function for recursion
        def create_paths(node, path):
            # initialize a path set
            paths = {}
            for edge in node.adj_edges:
                # for each edge on the shortest path tree
                if edge.tail != start and edge == prev[edge.tail.id]:
                    # augment the path with one more edge
                    path_ = path + [(edge, time[node.id])]
                    # save the augmented path
                    paths[edge.tail.id] = path_
                    # search longer paths recursively
                    more_paths = create_paths(edge.tail, path_)
                    # save the longer paths
                    paths = dict(paths.items() + more_paths.items())
            return paths
        return create_paths(start, [])
    
    @classmethod
    def create_shortest_path(cls, start, end, prev, time):
        path = []
        # start from the end node
        path_head = end.id
        # go backward until arrive at the start node
        while path_head != start.id:
            # agument the path with a edge and arrival time
            prev_edge = prev[path_head]
            path_head = prev_edge.head.id
            path.insert(0, (prev_edge, time[path_head]))
        return path
    
    @classmethod
    def find_shortest_path(cls, net, depart_time, start, end=None):
        if end != None and start == end:
            return {end.id: (None, 0.0, 0.0)}
        # creater a FIFO queue for searching
        queue = deque()
        # create containers with default values
        cost = defaultdict(constant_factory(float('+inf')))
        time = defaultdict(constant_factory(float('+inf')))
        prev = defaultdict(None)
        # set values for the start node
        cost[start.id] = 0.0
        time[start.id] = depart_time
        queue.appendleft(start.id)
        # continue until the queue is empty
        while len(queue) > 0:
            # pop out the first object in the queue
            qtop = queue.pop()
            node = net.nodes[qtop]
            # relax each adjacent edges
            for edge in node.adj_edges:
                # get the traffic flow on the edge
                if Time.lessthan_maxtick(time[node.id]):
                    edge_flow = net.flows[edge.id][time[node.id]]
                else:
                    edge_flow = 0.0
                # if the relaxation makes a shorter path
                travel_time = edge.calc_travel_time(edge_flow)
                travel_cost = edge.calc_travel_cost(travel_time)
                if cost[edge.tail.id] > cost[node.id] + travel_cost:
                    # then update cost and time labels
                    cost[edge.tail.id] = cost[node.id] + travel_cost
                    time[edge.tail.id] = time[node.id] + travel_time
                    # and save the edge on the shortest path
                    prev[edge.tail.id] = edge
                    # and append the expanded node to the queue
                    queue.appendleft(edge.tail.id)
        # if end node is given, extract the shortest path to end node recursively
        if end != None:
            # if the end node is reached, there is at least one path
            # if the end node is not reached, the start and end nodes are not connected
            path = cls.create_shortest_path(start, end, prev, time) if end.id in prev else None
            return {end.id: (path, cost[end.id], time[end.id])}
        else:
            # if end node is not given, extract the shortest paths from start to all the other nodes
            paths = cls.create_all_shortest_paths(start, prev, time)
            # no path is defined for a ring and the travel time/cost is zero
            tuples = {start.id: (None, 0.0, 0.0)}
            for id_ in paths:
                # wrap the path, cost and time in a tuple
                tuples[id_] = (paths[id_], cost[id_], time[id_])
            return tuples
    
    def __init__(self, network, land):
        self.network, self.land = network, land
        self.paths = defaultdict(dict)
    
    def build_shortest_paths(self):
        for tick in xrange(Time.MAXTICK):
            for origin in self.network.locations.values():
                self.paths[tick][origin.id] = self.find_shortest_path(self.network, tick, origin)
    
    def get_shortest_path(self, depart_time, start, end):
        return self.paths[depart_time][start][end]
    
