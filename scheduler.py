# Markov scheduler for activity and travel
import itertools
from pprint import pformat
from collections import namedtuple, defaultdict
from config import Config
from utils import Time
from utils import logger
from utils import constant_factory

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
                        for elapsed in xrange(tick + 1):
                            if activity.within_time_window(tick - elapsed):
                                yield (tick, activity, location, elapsed, None, None)

    @classmethod
    def individual_transitions(cls, person, network, land, router,
                               tick, activity, position, elapsed, joint, todo):
        for activity in person.program:
            for destination in cls.activity_locations(person, activity, land):
                # travel starts at the beginning of the next tick, tick + 1
                # tcost is the travel cost and, 
                # ttime is the arrival time at next activity destination
                path, tcost, ttime = router.get_shortest_path(tick + 1, position.id, destination.id)
                yield (activity, destination, path, tcost, ttime)

    @classmethod
    def individual_schedule(cls, demand, network, land, router, population):
        # save in-home activity into a local variable
        home = demand.activities["home"]
        for hh in population.households[:2]:
            if hh.id % 100 == 0:
                print " %d." % hh.id
            logger.info((hh, hh.program))
            for person in itertools.chain(hh.adults, hh.children):
                logger.info((person, person.program, person.get_residence()))
                # save the person's residence into a local variable
                residence = person.get_residence()
                # a dict with default value +inf
                state_utils = defaultdict(constant_factory(float('-inf')))
                # initialize the absorbing states
                for elapsed in xrange(Time.MAXTICK + 1):
                    if home.within_time_window(Time.MAXTICK - elapsed):
                        # absorbing states consists of maximum tick and in-home activity
                        absorbing_state = (Time.MAXTICK, home, residence, elapsed, 
                                           None, None)
                        state_utils[absorbing_state] = 0.0
                for state in cls.individual_states(person, land):
                    tick, activity, position, elapsed, joint, todo = state
                    # logger.debug(("state:", state))
                    for trans in cls.individual_transitions(person, network, land, router, *state):
                        next_activity, destination, path, travel_cost, arrival_time = trans
                        # logger.debug(("trans:", trans))
                        # elapsed time depends on the activity transition
                        if next_activity == activity and position == destination:
                            next_elapsed = elapsed + 1
                        else:
                            next_elapsed = 0
                        # transition to the next state
                        next_state = (arrival_time, next_activity, destination, next_elapsed, None, None)
                        # logger.debug(("next state:", next_state))
                        # skip, if the arrival time is too late or the state is not feasible
                        if arrival_time > Time.MAXTICK or next_state not in state_utils:
                            continue
                        # get activity utility
                        activity_util = demand.get_activity_util(activity, tick, elapsed)
                        # calculate state utility
                        state_util = activity_util - travel_cost + Config.discount * state_utils[next_state]
                        # the maximum state utility and the associated choice
                        if state_utils[state] < state_util:
                            state_utils[state] = state_util
                            person.transitions[state] = next_state
                # logger.debug(pformat(person.transitions))
                # the initial state starts at the mid night and in home
                current_state = (0, home, residence, 0, None, None)
                person.states.append(current_state)
                while current_state[0] < Time.MAXTICK:
                    current_state = person.transitions[current_state]
                    person.states.append(current_state)
                logger.info(pformat(person.states))
                


    @classmethod
    def household_schedule(cls):
        pass
    
    def __init__(self, demand, network, land, router, population):
        self.demand, self.network, self.land, self.router, self.population = \
            demand, network, land, router, population
