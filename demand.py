# Activity class
from __future__ import division
from mpmath import fp
from utils import Time
from collections import OrderedDict


class Demand(object):
    "Demand is a pool of activities. "
    def __init__(self):
        self.activities = OrderedDict()
        self.programs = OrderedDict()
        self.activity_utils = OrderedDict()

    def add_activity(self, name, U0, Um, Sigma, Lambda, Xi, time_window, min_duration=0.0):
        id_ = len(self.activities)
        self.activities[name] = Activity(id_, name, U0, Um, Sigma, Lambda, Xi, time_window, min_duration)
    
    def add_program(self, id_, activity_names):
        activities = [self.activities[name] for name in activity_names]
        self.programs[id_] = tuple(activities)
    
    def get_activity(self, name):
        try:
            return self.activities[name]
        except KeyError, e:
            raise e
    
    def build_activity_util(self):
        for name, activity in self.activities.items():
            print name
            args = [(tick, elapsed) for tick in xrange(Time.MAXTICK)
                                    for elapsed in xrange(tick)
                                    if  activity.within_time_window(tick - elapsed)]
            ticks, elapsed = tuple(zip(*args))
            utils = map(activity.discrete_util, ticks, elapsed)
            self.activity_utils[name] = dict(zip(args, utils))
    
    def get_activity_util(self, activity, tick=None, elapsed=0.0):
        if tick == None:
            return self.activity_utils[activity.name]
        else:
            return self.activity_utils[activity.name][(tick, elapsed)]


class Activity(object):
    "Each activity is specified as a set of confeters which determine its marginal utility. "
    def __init__(self, id_, name, U0, Um, Sigma, Lambda, Xi, time_window, min_duration):
        ''' U0 is the baseline utility level of acivity. 
            Um is the maximum utility of activity. 
            Sigma determines the slope or steepness of the curve. 
            Lambda determines the relative position of the inflection point. 
            Xi determines the time of day at which the marginal utility reaches the maximum. 
            time_window is the interval of starting time for this activity (a 2-tuple). 
            min_duration is the minimum duration for this activity. 
        '''
        # activity name
        self.id, self.name = id_, name
        # utility function parameters
        self.U0, self.Um, self.Sigma, self.Lambda, self.Xi = U0, Um, Sigma, Lambda, Xi
        # temproal constraints
        self.time_window = (Time.min2tick(time_window[0]), Time.min2tick(time_window[1]))
        self.min_duration = Time.min2tick(min_duration)

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.id == other.id

    def _marginal_util(self, time, elapsed=0.0):
        "The marginal activity utility is a function of the current time and the elapsed time. "
        nominator = self.Sigma*self.Lambda*self.Um
        denominator = (fp.exp( self.Sigma*(time-self.Xi) ) *
            fp.power(1.0+fp.exp( -self.Sigma*(time-self.Xi) ), self.Lambda+1.0) )
        return self.U0 + nominator/denominator

    def discrete_util(self, tick, elapsed=0.0):
        lower = Time.tick2min(tick) - Time.TIMEUNIT/2.0
        upper = lower + Time.TIMEUNIT
        if tick == 0:
            util = fp.quad(self._marginal_util, [0.0, Time.TIMEUNIT/2.0]) + \
                   fp.quad(self._marginal_util, [Time.TIMELENG-Time.TIMEUNIT/2.0, Time.TIMELENG])
        else:
            util = fp.quad(self._marginal_util, [lower, upper])
        return util
    
    def calc_schedule_delay(self, tick):
        return 0.0
    
    def within_time_window(self, tick):
        return tick > self.time_window[0] and tick < self.time_window[1]


class Mandatory(Activity):
    def __init__(self, id_, name, U0, Um, Sigma, Lambda, Xi, time_window, min_duration, 
                 pref_timing, penalty_buffer, early_penalty, late_penalty):
        super(Mandatory, self).__init__(self, id_, name, U0, Um, Sigma, Lambda, Xi, time_window, min_duration)
        self.pref_timing, self.penalty_buffer = pref_timing, penalty_buffer
        self.early_penalty, self.late_penalty = early_penalty, late_penalty
    
    def calc_schedule_delay(self, tick):
        early_time = self.pref_timing - Time.tick2min(tick)
        late_time  = Time.tick2min(tick) - self.pref_timing
        if early_time > self.penalty_buffer:
            return early_time * self.early_penalty
        if late_time > self.penalty_buffer:
            return late_time * self.late_penalty
        return 0.0
        
