# configuration
from __future__ import division
import math


class Config(object):
    # total minutes in 24 hours
    DAY = 1440
    # equivalent minutes of a tick
    TICK = 20
    
    @classmethod
    def init(cls, settings):
        for var in settings:
            setattr(cls, var, settings[var])
        # the maximum value of timeslice
        cls.MAXTICK = cls.HORIZON // cls.TICK
        # convert time unit from minute to hour
        cls.min2hr = 1.0/60.0
        cls.ALPHA_in    *= cls.min2hr
        cls.ALPHA_drive *= cls.min2hr
        cls.ALPHA_wait  *= cls.min2hr
        cls.ALPHA_walk  *= cls.min2hr


def main():
    print Config.TICK, Config.DAY


if __name__ == '__main__':
    main()

