from __future__ import division
import math
import itertools


# debug logging
import logging
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='debug.log', filemode='w')


def sorted_dict_values(adict):
    keys = adict.keys( )
    keys.sort( )
    return map(adict.get, keys)

def sorted_dict_keys(adict):
    keys = adict.keys( )
    return sorted(keys)

def sorted_dict_items(adict):
    keys = adict.keys( )
    keys.sort( )
    return zip(keys, map(adict.get, keys))

def ndrange(*args):
    return itertools.product(*map(xrange, args))

def create_objects(creater, args_list):
    for args in args_list:
        creater(*args)

# TODO new class: ObjPool
# demand, network, landuse, popoluation can be inherited from it
# then add_object2pool() is a method defined in ObjPool

def add_object2pool(creater, pool, *args):
    id_ = len(pool)
    aug_args = (id_,) + args
    obj = creater(*aug_args)
    pool.append(obj)
    return obj

def constant_factory(value):
    return itertools.repeat(value).next


class Time(object):
    # conversion of tick and minutes
    @classmethod
    def min2tick(cls, minute):
        if math.isinf(minute):
            return minute
        return int(math.floor((minute / cls.TIMEUNIT) + 0.5))

    @classmethod
    def tick2min(cls, tick):
        if math.isinf(tick):
            return tick
        return float(tick) * cls.TIMEUNIT
    
    @classmethod
    def lessthan_maxtick(cls, tick):
        return tick < cls.MAXTICK
    
    @classmethod
    def init(cls, timeleng, timeunit):
        cls.TIMELENG, cls.TIMEUNIT = timeleng, timeunit
        # the maximum value of tick
        cls.MAXTICK = cls.TIMELENG // cls.TIMEUNIT


def main():
    import numpy as np
    ij = (2, 4)
    for i, j in ndrange(*ij):
        print (i, j)
    for i, j in np.ndindex(*ij):
        print (i, j)
    
    Time.init(1000, 10)
    print "max tick: %d" % Time.MAXTICK

if __name__ == '__main__':
    main()
