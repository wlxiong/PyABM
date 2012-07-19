from __future__ import division
try:
    import numpypy  # required by PyPy
except ImportError:
    pass
import numpy as np
import math
import random
import itertools
from utils import ndrange
from config import Config


class Population(object):
    "Population consists of households. "
    def __init__(self, household_size, car_ownership):
        self.household_size, self.car_ownership = sorted(household_size), sorted(car_ownership)
        self.households = []
    
    def _proportional_fit(self, row_sum, col_sum, tolerance=0.01):
        n_row, n_col = row_sum.size, col_sum.size
        row_sum.shape = (n_row, 1)
        col_sum.shape = (1, n_col)
        assert row_sum.sum() == col_sum.sum(), 'Row subsum and column subsum are not equal.'
        table = np.ones([n_row, n_col])
        for i, j in itertools.product(xrange(n_row), xrange(n_col)):
            if i > j:
                table[i,j] = 0.0
        row_err = float('+inf')
        while row_err > tolerance:
            table = row_sum * (table / table.sum(1).reshape(n_row, 1))
            table = col_sum * (table / table.sum(0).reshape(1, n_col))
            row_diff = table.sum(1).reshape(n_row, 1) - row_sum
            row_err = (row_diff*row_diff).sum()
        return table

    def _rand_assignment(self, slot_size):
        slots = []
        for slot, size in slot_size:
            slots.extend(list(itertools.repeat(slot, size)))
        random.shuffle(slots)
        return slots
    
    def _get_location_assignment(self, locations, size):
        # a wrapper for the random assignment
        assignment = self._rand_assignment(locations)
        return assignment[0:size]
    
    def create_households(self, properties):
        # calculate the fleet and household size table
        fleet = np.array([freq for car, freq in self.car_ownership])
        hhsize = np.array([freq for size, freq in self.household_size])
        table = self._proportional_fit(fleet, hhsize)
        # assign random residential location to the households
        dwellings = self._get_location_assignment(properties, int(round(table.sum())))
        # create household pool
        itdwellings = iter(dwellings)
        for fleet, hhsize in ndrange(*table.shape):
            for i in xrange(int(round(table[fleet, hhsize]))):
                self.add_household(hhsize, fleet, itdwellings.next())
    
    def add_household(self, size, fleet, home):
        id_ = len(self.households)
        hh = Household(id_, size, fleet, home)
        self.households.append(hh)
        
    
    def get_home(self, arg):
        pass
    
    def get_work(self, arg):
        pass
    
    def get_school(self, arg):
        pass


class Household(object):
    def __init__(self, id_, size, fleet, home):
        self.id, self.size, self.home, self.fleet = id_, size, home, fleet
        self.adults = []
        self.children = []
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __repr__(self):
        return "HH%d" % self.id
    
    def add_adult(self, home, work=None, maintenance=None, discretionary=None):
        self.adults.append(Adult(home, work))
    
    def add_child(self, home, school=None, discretionay=None):
        self.children.append(Child(home, school))


class Individual(object):
    """ Each individual has his/her own (home, work/school) pair. 
    """
    def __init__(self, id_, home, mandatory):
        self.id, self.home, self.mandatory = id_, home, mandatory

    def __repr__(self):
        return "IN%d" % self.id

    def __eq__(self, other):
        return self.id == other.id


class Adult(Individual):
    def __init__(self, id_, home, work, discretionary, maintenance):
        super.__init__(id_, home, work)


class Child(Individual):
    def __init__(self, id_, home, school, discretionary):
        super.__init__(id_, home, school)

