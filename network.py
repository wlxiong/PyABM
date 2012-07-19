# The basic structure for transport network
from __future__ import division
try:
    import numpypy  # required by PyPy
except ImportError:
    pass
import numpy as np
import math
from config import Config
from utils import Time

class Network(object):
    "Network is a pool of nodes and edges. "
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.trans = []
    
    def get_node(self, id_):
        if id_ not in self.nodes:
            self.nodes[id_] = Node(id_)
        return self.nodes[id_]
    
    def get_stop(self, id_):
        if id_ not in self.nodes:
            self.nodes[id_] = Stop(id_)
        return self.nodes[id_]
    
    def add_oneway_street(self, head_id, tail_id, drive_time, capacity, length):
        head = self.get_node(head_id)
        tail = self.get_node(tail_id)
        id_ = len(self.edges)
        self.edges.append(Street(id_, head, tail, drive_time, capacity, length, Config.ALPHA_drive))
    
    def add_street(self, head_id, tail_id, drive_time, capacity, length):
        self.add_oneway_street(head_id, tail_id, drive_time, capacity, length)
        self.add_oneway_street(tail_id, head_id, drive_time, capacity, length)
    
    def add_oneway_sidewalk(self, head_id, tail_id, walk_time, capacity):
        head = self.get_node(head_id)
        tail = self.get_node(tail_id)
        id_ = len(self.edges)
        self.edges.append(Sidewalk(id_, head, tail, walk_time, capacity, Config.ALPHA_walk))
        
    def add_sidewalk(self, head_id, tail_id, walk_time=5.0, capacity=Config.CAPACITY_ped):
        self.add_oneway_sidewalk(head_id, tail_id, walk_time, capacity)
        self.add_oneway_sidewalk(tail_id, head_id, walk_time, capacity)

    def _get_timetable(self, offset, headway, dwell_time, total_run, in_vehicle_time):
        " Generate the timetable with given parameters. "
        timetable = [None] * total_run
        sum_in_vehicle_time = [sum(in_vehicle_time[0:i+1]) for i in xrange(len(in_vehicle_time))]
        for run in xrange(total_run):
            move_time = lambda tt: tt + headway*run + offset + dwell_time
            timetable[run] = map(move_time, [0] + sum_in_vehicle_time)
        return timetable
    
    def add_transit(self, offset, headway, n_run, stop_id_list, time_list, fare_matrix, capacity):
        # get stop list
        stop_list = []
        for stop_id in stop_id_list:
            stop = self.get_stop(stop_id)
            stop_list.append(stop)
        # get timetable
        timetable = self._get_timetable(offset, headway, 0, n_run, time_list)
        id_ = len(self.trans)
        self.trans[id_] = Transit(id_, timetable, stop_list, fare_matrix, capacity)
    
    def init_flows(self):
        self.flows = np.zeros([len(self.edges), Config.MAXTICK])


class Node(object):
    " node is a base class here. bust stop, street intersection and activity location are derived from it. "
    def __init__(self, id_):
        self.id = id_
        self.adj_edges = []

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "ND%d" % self.id

    def add_adj_edge(self, edge):
        self.adj_edges.append(edge)


class Edge(object):
    "Edge is the base class for road and sidewalk. "
    def __init__(self, id_, head, tail):
        self.id, self.head, self.tail = id_, head, tail

    def __eq__(self, other):
        return self.id == other.id
    
    def __repr__(self):
        return "ED%d" % self.id
    
    def __str__(self):
        return "(%s, %s)" % (self.head, self.tail)

    def calc_travel_time(self, move_flow):
        raise NotImplementedError

    def calc_travel_cost(self, travel_time):
        raise NotImplementedError


class Street(Edge):
    """ Street is the connection between zones (residential location, economic activity area)
        and hubs (i.e. transit stop, parking lot) in transport network. 
    """
    def __init__(self, id_, head, tail, drive_time, capacity, length, cost_unit):
        super(Street, self).__init__(id_, head, tail)
        self.drive_time, self.capacity, self.length, self.cost_unit = drive_time, capacity, length, cost_unit
        self.head.add_adj_edge(self)

    def calc_travel_time(self, flow):
        if flow / self.capacity > 4.0:
            print "  !! %s: %s / %s > 4.0" % (self, flow, self.capacity)
            # raise PendingDeprecationWarning('Street capacity excess (20x)! ')
        self.travel_timeslice = Time.min2slice(self.drive_time*(1.0 + .15*math.pow(flow/self.capacity, 4.0)))
        return self.travel_timeslice

    def calc_travel_cost(self, drive_time):
        return drive_time * self.cost_unit


class Sidewalk(Edge):
    """ Sidewalk is the connection between zones (residential location, economic activity area)
        and hubs (i.e. transit stop, parking lot) in transport network. 
    """
    def __init__(self, id_, head, tail, walk_time, capacity, cost_unit):
        super(Sidewalk, self).__init__(id_, head, tail)
        self.head.add_adj_edge(self)
        self.walk_time, self.capacity, self.cost_unit = walk_time, capacity, cost_unit

    def calc_travel_time(self, flow):
        if flow > self.capacity * 8:
            print "%s: %s / %s" % (self, flow, self.capacity)
            # raise PendingDeprecationWarning('Sidewalk capacity excess (8x)! ')
        self.travel_timeslice = Time.min2slice(self.walk_time*(1.0 + .15*math.pow(flow/self.capacity, 4.0)))
        return self.travel_timeslice

    def calc_travel_cost(self, walk_time):
        return walk_time * self.cost_unit


class Stop(Node):
    "A stop has a id and a list of lines passing by it. "
    def __init__(self, id_):
        super(Stop, self).__init__(id_)


class Transit(object):
    "A transit line is an ordered list of stops, associated with a timetable. "
    def __init__(self, id_, timetable, stop_list, fare_matrix, capacity):
        self.id = id_
        self.timetable = timetable
        self.stops_on_line, self.fare_matrix, self.capacity = stop_list, fare_matrix, capacity
        self.stop_order = {}
        for order, each_stop in enumerate(self.stops_on_line):
            each_stop.add_adj_edge(self)
            self.stop_order[each_stop] = order

    def __str__(self):
        return " line %s: %s " % (self.id, self.stops_on_line)
    
    def __repr__(self):
        return "TR%d" % self.id

    def calc_arrival_time(self, time, origin, dest):
        " Return the arrival time and waiting since time (min). "
        try:
            i_origin = self.stop_order[origin]
        except KeyError:
            raise KeyError('Cannot find the stop on the line. ')
        if dest in self.stop_order:
            i_dest = self.stop_order[dest]
            if i_dest > i_origin:
                for run in xrange(len(self.timetable)):
                    if time <= self.timetable[run][i_origin]:
                        wait_time = self.timetable[run][i_origin] - time
                        arrival_time = self.timetable[run][i_dest]
                        return (arrival_time, wait_time)
        return (float('inf'), float('inf'))

    def calc_travel_cost(self, in_vehicle_time, move_flow):
        if move_flow > self.capacity * 8:
            print "%s: %s / %s" % (self, move_flow, self.capacity)
            # raise PendingDeprecationWarning('Transit line capacity excess (8x)! ')
        self.travel_cost = in_vehicle_time*(1.0 + .15*math.pow(move_flow/self.capacity, 4.0))
        return self.travel_cost
