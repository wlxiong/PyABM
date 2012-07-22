from collections import defaultdict


class LandUse(object):
    "Land use pattern determines where the socioeconomic activities take place. "
    def __init__(self, demand, network):
        self.demand, self.network = demand, network
        self.location_capacities = defaultdict(dict)
        self.activity_capacities = defaultdict(dict)
    
    def add_location(self, centroid_id, access_id, activity_capacity):
        # create a new location, multiple by 100 to offset node id
        location = self.network.get_location(centroid_id)
        # create an access link for the location
        self.network.add_sidewalk(location.id, access_id)
        # assign activities to the location
        for name, capacity in activity_capacity.items():
            activity = self.demand.activities[name]
            self.location_capacities[activity][location] = capacity
            self.activity_capacities[location][activity] = capacity
    
    def get_location_capacities(self, keys=None):
        capacities = {}
        if keys == None:
            keys = self.demand.activities.keys()
        for key in keys:
            activity = self.demand.activities[key]
            capacities[key] = self.location_capacities[activity]
        return capacities
    
    def get_activity_capacities(self, keys=None):
        capacities = {}
        if keys == None:
            keys = self.network.locations.keys()
        for key in keys:
            location =  self.network.locations[key]
            capacities[key] = self.activity_capacities[location]
        return capacities
