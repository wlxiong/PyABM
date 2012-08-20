# Markov scheduler for activity and travel
import itertools
from collections import namedtuple
from config import Config
from utils import Time
from utils import logger


# state variables are stored in namedtuple
State = namedtuple('State', 'tick, activity, location, elapsed, joint, todo')


def traverse_indvidual_states(person, locations):
    for tick in xrange(Time.min2tick(Config.MAXTICK)-1,-1,-1):
        for activity in person.program:
            if not activity.within_time_window(tick):
                continue
            if activity.name == "work" or activity.name == "school":
                activity_locations = [person.get_workplace()]
            elif activity.name == "home":
                activity_locations = [person.get_residence()]
            else:
                activity_locations = locations[activity.name]
            for location in activity_locations:
                for elapsed in xrange(tick):
                    if activity.within_time_window(tick - elapsed):
                        yield (tick, activity, location, elapsed, None, None)

def traverse_indvidual_transitions(person, locations, network, router,
                                   tick, activity, position, elapsed, joint, todo):
    for activity in person.program:
        if activity.name == "work" or activity.name == "school":
            activity_locations = [person.get_workplace()]
        elif activity.name == "home":
            activity_locations = [person.get_residence()]
        else:
            activity_locations = locations[activity.name]
        for destination in activity_locations:
            path, cost, time = router.get_shortest_path(tick, position.id, destination.id)
            yield (activity, destination, path, cost, time)
        

def individual_schedule(pop, net, land, router, demand):
    locations = land.get_locations()
    for hh in pop.households[1:100]:
        logger.debug(hh)
        for person in itertools.chain(hh.adults, hh.children):
            logger.debug(person)
            for state in traverse_indvidual_states(person, locations):
                tick, activity, position, elapsed, joint, todo = state
                logger.debug(state)
                for trans in traverse_indvidual_transitions(person, locations, net, router, *state):
                    next_activity, destination, path, travel_cost, travel_time = trans
                    logger.debug(trans)
                    
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

