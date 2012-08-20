# configuration
from __future__ import division
import math


class Config(object):
    @classmethod
    def init(cls, settings):
        for var in settings:
            # initialize the object attributes with settings
            setattr(cls, var, settings[var])
        # convert time unit from minute to hour
        cls.min2hr = 1.0/60.0
        cls.ALPHA_in    *= cls.min2hr
        cls.ALPHA_drive *= cls.min2hr
        cls.ALPHA_wait  *= cls.min2hr
        cls.ALPHA_walk  *= cls.min2hr


def main():
    print Config.TIMEUNIT, Config.TIMELENG


if __name__ == '__main__':
    main()

