# find the shortest path
from collections import deque
from collections import defaultdict
import itertools
from utils import logger, constant_factory
from pprint import pprint


def get_all_paths(net, start, prev, time):
    def get_paths(node, path):
        paths = []
        for edge in node.adj_edges:
            if edge.tail != start and edge == prev[edge.tail.id]:
                path_ = path + [(edge, time[node.id])]
                paths.append(path_)
                more_paths = get_paths(edge.tail, path_)
                paths.extend(more_paths)
        return paths
    return get_paths(start, [])

def find_shortest_path(net, depart_time, start, end=None):
    if end != None and start == end:
        return {'path': None, 'cost': 0.0, 'time': 0.0}
    # create containers with default values
    queue = deque()
    cost = defaultdict(constant_factory(float('+inf')))
    time = defaultdict(constant_factory(float('+inf')))
    prev = defaultdict(None)
    # set values for the start node
    cost[start.id] = 0.0
    time[start.id] = depart_time
    queue.appendleft(start.id)
    # update the labels
    while len(queue) > 0:
        qtop = queue.pop()
        node = net.nodes[qtop]
        for edge in node.adj_edges:
            edge_flow = net.flows[edge.id][time[node.id]]
            if cost[edge.tail.id] > cost[node.id] + edge.calc_travel_cost(edge_flow):
                # update cost and time labels
                cost[edge.tail.id] = cost[node.id] + edge.calc_travel_cost(edge_flow)
                time[edge.tail.id] = time[node.id] + edge.calc_travel_time(edge_flow)
                # save the link on the shortest path
                prev[edge.tail.id] = edge
                # append the expanded node to the queue
                queue.appendleft(edge.tail.id)
    # extract the shortest path recursively
    if end != None:
        if end.id in prev:
            path = [(prev[end.id], time[prev[end.id].head.id])]
            while path[0][0].head.id != start.id:
                path.insert(0, (prev[path[0][0].head.id], time[prev[path[0][0].head.id].head.id]))
            return {'path': path, 'cost': cost[end.id], 'time': time[end.id]}
        else:
            return {'path': None, 'cost': float('+inf'), 'time': float('+inf')}
    else:
        all_paths = get_all_paths(net, start, prev, time)
        ends = [path[-1][0].tail.id for path in all_paths]
        return dict(zip(ends,all_paths))
