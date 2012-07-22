from __future__ import division
import math
import itertools
from config import Config


# debug logging
import logging
logger = logging.getLogger('debug_log')
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='debug.log')


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

def create_objects(creater, args):
    for arg in args:
        creater(*arg)

def add_object2pool(creater, pool, *args):
    id_ = len(pool)
    aug_args = (id_,) + args
    obj = creater(*aug_args)
    pool.append(obj)
    return obj

def constant_factory(value):
    return itertools.repeat(value).next


class Time(object):
    # conversion of timeslice and minutes
    @classmethod
    def min2slice(cls, minute):
        if math.isinf(minute):
            return minute
        return int(math.floor((minute / Config.TICK) + 0.5))

    @classmethod
    def slice2min(cls, timeslice):
        if math.isinf(timeslice):
            return timeslice
        return float(timeslice) * Config.TICK


def main():
    import numpy as np
    ij = (2, 4)
    for i, j in product_range(*ij):
        print (i, j)
    for i, j in np.ndindex(*ij):
        print (i, j)

if __name__ == '__main__':
    main()
