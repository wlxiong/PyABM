# Markov scheduler for activity and travel
import itertools
from collections import namedtuple
from config import Config
from utils import Time
from utils import logger


# state variables are stored in namedtuple
State = namedtuple('State', 'tick, activity, location, elapsed, joint, todo')

class Scheduler(object):
    @classmethod
    def activity_locations(cls, person, activity, land):
        if activity.name == "work" or activity.name == "school":
            return [person.get_workplace()]
        elif activity.name == "home":
            return [person.get_residence()]
        else:
            return land.get_locations(activity.name)
    
    @classmethod
    def individual_states(cls, person, land):
        for tick in xrange(Time.MAXTICK-1,-1,-1):
            for activity in person.program:
                if activity.within_time_window(tick):
                    for location in cls.activity_locations(person, activity, land):
                        for elapsed in xrange(tick):
                            if activity.within_time_window(tick - elapsed):
                                yield (tick, activity, location, elapsed, None, None)

    @classmethod
    def individual_transitions(cls, person, network, land, router,
                               tick, activity, position, elapsed, joint, todo):
        for activity in person.program:
            for destination in cls.activity_locations(person, activity, land):
                path, tcost, ttime = router.get_shortest_path(tick, position.id, destination.id)
                yield (activity, destination, path, tcost, ttime)

    @classmethod
    def individual_schedule(cls, demand, network, land, router, population):
        for hh in population.households[:1000]:
            if hh.id % 200 == 0:
                print " %d." % hh.id
            # logger.debug((hh, hh.program))
            for person in itertools.chain(hh.adults, hh.children):
                # logger.debug((person, person.program))
                for state in cls.individual_states(person, land):
                    tick, activity, position, elapsed, joint, todo = state
                    # logger.debug(state)
                    for trans in cls.individual_transitions(person, network, land, router, *state):
                        next_activity, destination, path, travel_cost, travel_time = trans
                        # logger.debug(trans)
                        # arrival time at next activity destination
                        arrival_time = tick + travel_time + 1
                        # activity_util = demand.get_activity_util(activity, tick, elapsed)
                        # Config.discount * 

        
        # for person in enum_commodity():
        #     # print "    %s" % comm
        #     # backtrack from the ending to the beginning
        #     for tick in xrange(Time.min2tick(conf.TIMELENG)-1,-1,-1):
        #         for state in enum_state(comm, tick):
        #             these_util = {}
        #             for transition, starting_time, travel_cost, schedule_delay in \
        #                 enum_transition(comm, tick, state):

    @classmethod
    def household_schedule(cls):
        pass
    
    def __init__(self, demand, network, land, router, population):
        self.demand, self.network, self.land, self.router, self.population = \
            demand, network, land, router, population
