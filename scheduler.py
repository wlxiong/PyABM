# Markov scheduler for activity and travel
import itertools
from collections import namedtuple
from config import Config
from utils import Time
from utils import logger


# state variables are stored in namedtuple
State = namedtuple('State', 'tick, activity, location, elapsed, joint, todo')


def activity_locations(person, activity, land):
    if activity.name == "work" or activity.name == "school":
        return [person.get_workplace()]
    elif activity.name == "home":
        return [person.get_residence()]
    else:
        return land.get_locations(activity.name)


def individual_states(person, land):
    for tick in xrange(Time.MAXTICK-1,-1,-1):
        for activity in person.program:
            if activity.within_time_window(tick):
                for location in activity_locations(person, activity, land):
                    for elapsed in xrange(tick):
                        if activity.within_time_window(tick - elapsed):
                            yield (tick, activity, location, elapsed, None, None)


def individual_transitions(person, land, network, router,
                           tick, activity, position, elapsed, joint, todo):
    for activity in person.program:
        for destination in activity_locations(person, activity, land):
            path, tcost, ttime = router.get_shortest_path(tick, position.id, destination.id)
            yield (activity, destination, path, tcost, ttime)


def individual_schedule(pop, net, land, router, demand):
    for hh in pop.households[:1000]:
        if hh.id % 200 == 0:
            print " .%d" % hh.id
        # logger.debug((hh, hh.program))
        for person in itertools.chain(hh.adults, hh.children):
            # logger.debug((person, person.program))
            for state in individual_states(person, land):
                tick, activity, position, elapsed, joint, todo = state
                # logger.debug(state)
                for trans in individual_transitions(person, land, net, router, *state):
                    next_activity, destination, path, travel_cost, travel_time = trans
                    # logger.debug(trans)
                    # arrival time at next activity destination
                    arrival_time = tick + travel_time + 1
                    
                    
    print "individual_schedule()"
        
    # for person in enum_commodity():
    #     # print "    %s" % comm
    #     # backtrack from the ending to the beginning
    #     for tick in xrange(Time.min2tick(conf.TIMELENG)-1,-1,-1):
    #         for state in enum_state(comm, tick):
    #             these_util = {}
    #             for transition, starting_time, travel_cost, schedule_delay in \
    #                 enum_transition(comm, tick, state):


def household_schedule():
    pass

