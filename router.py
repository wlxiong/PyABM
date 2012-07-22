# find the shortest path
from collections import deque
from collections import defaultdict
import itertools
from utils import logger, constant_factory
from pprint import pprint


def get_all_shortest_paths(start, prev, time):
    # create a nested function for recursion
    def get_paths(node, path):
        # initialize a path set
        paths = []
        for edge in node.adj_edges:
            # for each edge on the shortest path tree
            if edge.tail != start and edge == prev[edge.tail.id]:
                # augment the path with one more edge
                path_ = path + [(edge, time[node.id])]
                # save the augmented path
                paths.append(path_)
                # search longer paths recursively
                more_paths = get_paths(edge.tail, path_)
                # save the longer paths
                paths.extend(more_paths)
        return paths
    return get_paths(start, [])


def get_shortest_path(start, end, prev, time):
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


def find_shortest_path(net, depart_time, start, end=None):
    if end != None and start == end:
        return {'path': {end.id: None}, 
                'cost': {end.id: 0.0}, 
                'time': {end.id: 0.0}}
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
            edge_flow = net.flows[edge.id][time[node.id]]
            # if the relaxation makes a shorter path
            if cost[edge.tail.id] > cost[node.id] + edge.calc_travel_cost(edge_flow):
                # then update cost and time labels
                cost[edge.tail.id] = cost[node.id] + edge.calc_travel_cost(edge_flow)
                time[edge.tail.id] = time[node.id] + edge.calc_travel_time(edge_flow)
                # and save the edge on the shortest path
                prev[edge.tail.id] = edge
                # and append the expanded node to the queue
                queue.appendleft(edge.tail.id)
    # if end node is given, extract the shortest path to end node recursively
    if end != None:
        # if the end node is reached, there is at least one path
        # if the end node is not reached, the start and end nodes are not connected
        path = get_shortest_path(start, end, prev, time) if end.id in prev else None
        return {'path': {end.id: path}, 
                'cost': {end.id: cost[end.id]}, 
                'time': {end.id: time[end.id]}}
    else:
        # if end node is not given, extract the shortest paths from start to all the other nodes
        all_paths = get_all_shortest_paths(start, prev, time)
        end_ids = [path[-1][0].tail.id for path in all_paths]
        return {'path': dict(zip(end_ids, all_paths)), 'cost': cost, 'time': time}
