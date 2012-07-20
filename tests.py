# test cases
from pprint import pprint, pformat
from utils import create_objects
from utils import logger
from config import Config
import itertools


def test_config():
    from config import Config
    
    settings = {
        'TICK': 20,
        'HORIZON': 1440,
        # variance tolerance of preferred activitiy timing
        'DELTA': 0.25 * 60.0,
        # the link capacity
        'CAPACITY_ped': 30000,
        'CAPACITY_bus': 120,
        'CAPACITY_sub': 1500,
        # the equivalent utility of unit in-vehicle travel time
        'ALPHA_in': 60.0,
        # the equivalent utility of unit drive travel time
        'ALPHA_drive': 60.0,
        # the equivalent utility of unit waiting time
        'ALPHA_wait': 120.0,
        # the equivalent utility of unit walking time
        'ALPHA_walk': 120.0,
        # the equivalent utility of line transfering 
        'ALPHA_tran': 5.0,
        # the equivalent utility of one dollar
        'ALPHA_fare': 1.0,
        # the unit cost of early arrival (dollar/hour)
        'ALPHA_early': 0.0, # 30.0 * min2h
        # the unit cost of late arrival (dollar/hour)
        'ALPHA_late': 0.0,  # 90.0 * min2h
        # the unit cost of house rent 
        'ALPHA_rent': 1.0,
        # the parameter related to residential location 
        'THETA_location': 0.002,
        # the parameter related to making a trip or not
        'THETA_travel': 0.005,
        # the parameter related to pattern choice
        'THETA_bundle': 0.008,
        # the parameter related to tour choice
        'THETA_tour': 0.01,
        # the parameter related to path choice
        # 'THETA_path: 0.1
        # discount of future utility
        'discount': 1.0,
        # correlation between household members
        # 1-dimension dict, i.e. corr[(person 1,person 2)]
        'corr': {}
        # activity name tokens
        # 'tokens': {
        #     'residence': 'home',
        #     'business': 'work',
        #     'school': 'school'
        # }
    }
    # logger.debug(pformat(settings))
    Config.init(settings)


def test_demand():
    from demand import Demand
    
    dm = Demand()
    activity_data = [
        ['home',             1.0,  600, -0.010, 1.0,   720, (  0, 1440), 360],
        ['work',             0.0, 1600,  0.010, 1.0,   720, (240, 1440), 240],
        ['school',           0.0, 1600,  0.010, 1.0,   720, (240, 1440), 240],
        ['dinner',           0.0,  420,  0.010, 1.0,  1170, (720, 1440),  10],
        ['shopping',         0.0,  500,  0.010, 1.0,  1110, (720, 1440),  10]
    ]
    create_objects(dm.add_activity,activity_data)
    print 'activities:'
    pprint(dm.activities)
    return dm


def test_network():
    from network import Network
    net = Network()
    
    street_data = [
        [1,      3,      40,     3000,      40.0],
        [1,      5,      20,     2000,      15.0],
        [2,      5,      20,     2000,      15.0],
        [2,      4,      60,     4000,      50.0],
        [5,      6,      20,     3000,      20.0],
        [6,      3,      20,     2000,      20.0],
        [6,      4,      20,     2000,      20.0]
    ]
    create_objects(net.add_street, street_data)
    print 'nodes:'
    pprint(net.nodes)
    return net

    
def test_router():
    from router import find_shortest_path
    
    net = test_network()
    net.init_flows()
    path = find_shortest_path(net, 0, net.nodes[1], net.nodes[6])
    print 'path 1 - 6'
    pprint(path)
    paths = find_shortest_path(net, 0, net.nodes[1])
    print 'paths 1 - *'
    pprint(paths)
    return path

def test_landuse():
    from landuse import LandUse
    
    dm = test_demand()
    net = test_network()
    land = LandUse(dm, net)
    location_data = [
        [10,   1,   {'work': 4000, 'home': 1000, 'school': 5000}],
        [20,   2,   {'work': 4000, 'home': 1000, 'school': 5000}],
        [30,   3,   {'work': 4000, 'home': 2000, 'school': 5000}],
        [40,   4,   {'work': 4000, 'home': 2000, 'school': 5000}],
        [50,   5,   {'work': 4000, 'home': 2000, 'school': 5000}],
        [60,   6,   {'work': 4000, 'home': 2000, 'school': 5000}]
    ]
    create_objects(land.add_location, location_data)
    print "%d locations: " % len(land.locations)
    for location in land.locations:
        print "%s" % (str(location))
    return land


def test_population():
    from population import Population
    
    land = test_landuse()
    hh_size = [(1, 1000), (2, 3000), (3,4000), (4, 2000)]
    car_own = [(1, 5000), (2, 3000), (3,2000)]
    
    pop = Population(hh_size, car_own)
    properties = land.get_locations("home")
    pop.create_households(properties)
    
    print 'random residences'
    pprint([(hh, hh.home) for hh in pop.households[:10]])
    pprint([(hh, hh.home) for hh in pop.households[-10:]])
    from collections import defaultdict
    residences = defaultdict(int)
    for hh in pop.households:
        residences[id(hh.home)] += 1
    print 'residences'
    residence_list = sorted(residences.items())
    pprint(residence_list)
    print 'properties'
    property_list = sorted((id(location), capacity) for location, capacity in properties)
    pprint(property_list)
    assert residence_list == property_list, "The assigned residences are not the same as the household properties. "
    
    print "%d households are created. " % len(pop.households)
    print "id of the first household is %d. " % pop.households[0].id
    print "id of the last household is %d. " % pop.households[-1].id
    return pop


def main():
    test_config()
    dm0 = test_demand()
    net0 = test_network()
    path0 = test_router()
    land0 = test_landuse()
    num_hh = test_population()


if __name__ == '__main__':
    main()
