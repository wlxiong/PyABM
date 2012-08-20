# test cases
from pprint import pprint, pformat
from utils import create_objects
from utils import logger
from config import Config
import itertools


def test_config():
    from config import Config
    
    settings = {
        'TIMEUNIT': 20,
        'TIMELENG': 1440,
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
    # in-home activities and out-of-home activities
    #   madantory activities: work/business, school/college
    #   maintenance activities: escort passengers, shopping
    #   discretionary activities: eating out, visiting friends
    activity_data = [
        ['home',             1.0,  600, -0.010, 1.0,   720, (  0, 1440), 360],
        ['work',             0.0, 1600,  0.010, 1.0,   720, (240, 1440), 240],
        ['school',           0.0, 1600,  0.010, 1.0,   720, (240, 1440), 240],
        ['eating',           0.0,  420,  0.010, 1.0,  1170, (720, 1440),  10],
        ['shopping',         0.0,  500,  0.010, 1.0,  1110, (720, 1440),  10],
        ['visiting',         0.0,  500,  0.010, 1.0,  1110, (720, 1440),  10],
        ['escorting',         0.0,  500,  0.010, 1.0,  1110, (720, 1440),  10]
    ]
    create_objects(dm.add_activity, activity_data)
    print 'activities:'
    pprint(dm.activities.items())
    
    # intra-household interactions
    #   entire day level: 
    #     staying at home, absent together
    #     non-madantory DAP together (day-off for major shopping)
    #   episode level:
    #     shared activity
    #     escorting (children to school)
    #     allocation of maintenance task (shopping)
    #     car allocation
    # types of joint travel
    #   fully-joint tour, joint outbound, joint inbound
    #   drop-off/get-off, pick-up/get-in
    program_data = [
        [0, []],
        [1, ['shopping']],
        [3, ['eating']],
        [2, ['visiting']],
        [4, ['shopping', 'visiting']],
        [5, ['shopping', 'eating']]
    ]
    create_objects(dm.add_program, program_data)
    print 'programs:'
    pprint(dm.programs.items())
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


def test_drawing():
    from drawing import GNetwork
    
    net = test_network()
    gnet = GNetwork(net)
    gnet.draw('gnet.png')


def test_landuse(dm, net):
    from landuse import LandUse
    
    land = LandUse(dm, net)
    location_data = [
        # centriod, access, activities
        [100, 1,   {'work': 4000, 'home': 1000, 'school': 5000, 'shopping': 10000, 'eating': 10000}],
        [200, 2,   {'work': 4000, 'home': 1000, 'school': 5000, 'shopping': 10000, 'visiting': 10000}],
        [300, 3,   {'work': 4000, 'home': 2000, 'school': 5000, 'eating':   10000, 'visiting': 10000}],
        [400, 4,   {'work': 4000, 'home': 2000, 'school': 5000, 'shopping': 10000}],
        [500, 5,   {'work': 4000, 'home': 2000, 'school': 5000, 'eating':   10000}],
        [600, 6,   {'work': 4000, 'home': 2000, 'school': 5000, 'visiting': 10000}]
    ]
    create_objects(land.add_location, location_data)
    print "location capacities"
    pprint(land.locations.items())
    print "activity capacities"
    pprint(land.activities.items())
    return land


def test_router(net, land):
    from router import Router
    
    net.init_flows()
    print 'edges'
    pprint([(edge, str(edge)) for edge in net.edges])
    path = Router.find_shortest_path(net, 0, net.nodes[1], net.nodes[6])
    print 'path 1 - 6'
    pprint(path)
    path = Router.find_shortest_path(net, 0, net.nodes[6], net.nodes[1])
    print 'path 6 - 1'
    pprint(path)
    paths = Router.find_shortest_path(net, 0, net.nodes[1])
    print 'paths 1 - *'
    pprint(paths)
    paths = Router.find_shortest_path(net, 0, net.nodes[100])
    print 'paths 100 - *'
    pprint(paths)
    router = Router(net, land)
    router.build_shortest_paths()
    path = router.get_shortest_path(0, 100, 100)
    print 'path 100 - 100'
    pprint(path)
    path = router.get_shortest_path(0, 100, 200)
    print 'path 100 - 200'
    pprint(path)
    path = router.get_shortest_path(0, 100, 600)
    print 'path 100 - 600'
    pprint(path)
    return router


def test_population(dm, land):
    def count_objects(pool, target):
        from collections import defaultdict
        
        print "random objects"
        print pformat([(obj, obj.__getattribute__(target)) for obj in pool[:5]])
        print pformat([(obj, obj.__getattribute__(target)) for obj in pool[-5:]])
        print "object groups"
        counts = defaultdict(int)
        for obj in pool:
            counts[repr(obj.__getattribute__(target))] += 1
        print "%d targets" % len(pool)
        return sorted(counts.items())
    
    from population import Population
    
    # total number of households: 10,000
    prog = [(0, 1000), (1, 2000), (2, 3000), (3, 2000), (4, 1000), (5, 1000)]
    hhsize = [(1, 1000), (2, 3000), (3,4000), (4, 2000)]
    fleet = [(1, 5000), (2, 3000), (3,2000)]
    print "\nhousehold program choice"
    pprint(prog)
    print "\nhousehold size"
    pprint(hhsize)
    print "\nhousehold fleet size"
    pprint(fleet)
    
    pop = Population(hhsize, fleet, prog)
    pop.create_households(land, dm)
    
    print "\nhousehold programs"
    pprint(count_objects(pop.households, "program"))
    print "\nindividual programs"
    pprint(count_objects(pop.individuals, "program"))
    print "\nresidences"
    pprint(count_objects(pop.households, "residence"))
    print "\noffices"
    pprint(count_objects(pop.adults, "office"))
    print "\nschools"
    pprint(count_objects(pop.children, "school"))
    
    print "\n%d households are created. " % len(pop.households)
    print "id of the first household is %d. " % pop.households[0].id
    print "id of the last household is %d. " % pop.households[-1].id
    return pop


def test_scheduler(land, pop):
    import scheduler
    
    scheduler.traverse_indvidual_states(pop.adults[0], land)
    scheduler.traverse_indvidual_states(pop.children[0], land)
    scheduler.individual_schedule(pop, net, router, land, None)


def main():
    test_config()
    dm0 = test_demand()
    net0 = test_network()
    # gnet0 = test_drawing()
    land0 = test_landuse(dm0, net0)
    path0 = test_router(net0, land0)
    # pop0 = test_population(dm0, land0)
    # test_scheduler()


if __name__ == '__main__':
    main()
