from collections import defaultdict


class LandUse(object):
    "Land use pattern determines where the socioeconomic activities take place. "
    def __init__(self, demand, network):
        self.demand, self.network = demand, network
        self.capacities = defaultdict(dict)
        self.activities = defaultdict(list)
        self.locations = defaultdict(list)
    
    def add_location(self, centroid_id, access_id, activity_capacity):
        # create a new location, multiple by 100 to offset node id
        location = self.network.get_location(centroid_id)
        # create an access link for the location
        self.network.add_sidewalk(location.id, access_id)
        # assign activities to the location
        for name, capacity in activity_capacity.items():
            activity = self.demand.get_activity(name)
            self.capacities[name][location] = capacity
            self.activities[location.id].append(activity)
            self.locations[name].append(location)
    
    def get_capacities(self, key=None):
        if key == None:
            return dict(self.capacities)
        else:
            return self.capacities[key]
    
    def get_activities(self, key=None):
        if key == None:
            return dict(self.activities)
        else:
            return self.activities[key]
    
    def get_locations(self, key=None):
        if key == None:
            return dict(self.locations)
        else:
            return self.locations[key]
