from __future__ import division
try:
    import numpypy  # required by PyPy
except ImportError:
    pass
import numpy as np
import math
import random
import itertools
from utils import ndrange, add_object2pool
from config import Config


class Population(object):
    "Population consists of households. "
    def __init__(self, size_freq, fleet_freq):
        self.size_freq, self.fleet_freq = sorted(size_freq), sorted(fleet_freq)
        self.households = []
        self.adults = []
        self.children = []
    
    def _proportional_fit(self, row_sum, col_sum, tolerance=0.01):
        n_row, n_col = row_sum.size, col_sum.size
        # convert to matrices
        row_sum.shape = (n_row, 1)
        col_sum.shape = (1, n_col)
        # the row sum and column sum should be equal
        assert row_sum.sum() == col_sum.sum(), 'Row subsum and column subsum are not equal.'
        # initialize a table
        table = np.ones([n_row, n_col])
        # this table is a upper triangular matrix
        for i, j in ndrange(n_row, n_col):
            if i > j:
                table[i,j] = 0.0
        row_err = float('+inf')
        # check convergence criteria
        while row_err > tolerance:
            # row proportional fitting
            table = row_sum * (table / table.sum(1).reshape(n_row, 1))
            # column proportional fitting
            table = col_sum * (table / table.sum(0).reshape(1, n_col))
            # calculate the differences
            row_diff = table.sum(1).reshape(n_row, 1) - row_sum
            row_err = (row_diff*row_diff).sum()
        return table

    def _rand_assignment(self, capacity):
        slot_assginment = []
        # fill slot_assginment with objects to be assigned
        for slot, capacity in capacity.items():
            slot_assginment.extend(list(itertools.repeat(slot, capacity)))
        # random shuffle the slots, note that the period of random number generator
        # is mostly always smaller than the numbers of permutations
        random.shuffle(slot_assginment)
        return slot_assginment
    
    def _get_assignments(self, capacity, total):
        capsum = sum(capacity.values())
        assert capsum >= total, "%d available alternatives < %d required slots" % (capsum, total)
        # a wrapper for the random assignment
        assignment = self._rand_assignment(capacity)
        # only return the first $size$ locations
        return assignment[0:total]
    
    def add_household(self, size, fleet, it_residence, it_office, it_school, 
                      maintenance=None, discretionary=None):
        # add a new household object
        hh = add_object2pool(Household, self.households, 
                             size, fleet, it_residence.next(),
                             maintenance, discretionary)
        # the number of workers in the household
        wknum = 2 if size > 3 else size
        # the number of students in the household
        stnum = 0 if size < 3 else size - 2
        # create adults and children for the household
        # all the adults are worker and all the children are students
        for _ in xrange(wknum):
            add_object2pool(hh.add_adult, self.adults, hh.residence, it_office.next())
        for _ in xrange(stnum):
            add_object2pool(hh.add_child, self.children, hh.residence, it_school.next())
        return hh
    
    def create_households(self, capacities):
        # calculate the fleet and household size table
        fleet_array = np.array([freq for fleet, freq in self.fleet_freq])
        size_array  = np.array([freq for size, freq in self.size_freq])
        # fill the joint fleet-hhsize table using proportional fitting
        table = self._proportional_fit(fleet_array, size_array)
        # calculate the number of households
        hhnum  = int(round(table.sum()))
        # calculate the number of workers
        # if the size of a household is one, this one person is a worker
        # if the size of a household is larger than one, there a two workers
        wknum = sum([(2 if size > 3 else size) * freq for size, freq in self.size_freq])
        # calculate the number of students, all the other persons are students
        stnum = sum([(0 if size < 3 else size - 2) * freq for size, freq in self.size_freq])
        # assign random dwelling unit to the households
        residences = self._get_assignments(capacities["home"], hhnum)
        # assign random work place to the workers
        offices = self._get_assignments(capacities["work"], wknum)
        # assgin random school to the students
        schools = self._get_assignments(capacities["school"], stnum)
        # create iterators for all the locations
        it_residence, it_office, it_school = iter(residences), iter(offices), iter(schools)
        # create a household pool
        for i, j in ndrange(*table.shape):
            # create households with the same size and fleet
            for _ in xrange(int(round(table[i, j]))):
                self.add_household(self.size_freq[j][0], self.fleet_freq[i][0], 
                                   it_residence, it_office, it_school)


class Household(object):
    def __init__(self, id_, size, fleet, residence, maintenance, discretionary):
        self.id, self.size, self.residence, self.fleet = id_, size, residence, fleet
        self.maintenance, self.discretionary = maintenance, discretionary
        self.adults = []
        self.children = []
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __repr__(self):
        return "HH%d" % self.id
    
    def add_adult(self, id_, residence, office=None):
        adult = Adult(id_, residence, office)
        self.adults.append(adult)
        return adult
    
    def add_child(self, id_, residence, school=None):
        child = Child(id_, residence, school)
        self.children.append(child)
        return child


class Individual(object):
    """ Each individual has his/her own (residence, office/school) pair. 
    """
    def __init__(self, id_, residence):
        self.id, self.residence = id_, residence

    def __repr__(self):
        return "IN%d" % self.id

    def __eq__(self, other):
        return self.id == other.id


class Adult(Individual):
    def __init__(self, id_, residence, office):
        super(Adult, self).__init__(id_, residence)
        self.office = office


class Child(Individual):
    def __init__(self, id_, residence, school):
        super(Child, self).__init__(id_, residence)
        self.school = school

