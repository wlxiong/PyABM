class LandUse(object):
    "Land use pattern determines where the socioeconomic activities take place. "
    def __init__(self, demand, network):
        self.demand, self.network = demand, network
        self.locations = []
    
    def add_location(self, centroid_id, access_id, capacity):
        # create virutal node and access link for the location
        centroid = self.network.get_node(centroid_id)
        self.network.add_sidewalk(centroid_id, access_id)
        # add a new location
        id_ = len(self.locations)
        location = Location(id_, centroid)
        self.locations.append(location)
        # assign activities to the location
        for name, capacity in capacity.items():
            activity = self.demand.activities[name]
            location.add_activity(activity, capacity)
            activity.add_location(location, capacity)
        return location
    
    def get_locations(self, name):
        return self.demand.activities[name].locations


class Location(object):
    "A location is a place where people participate various activities. "
    def __init__(self, id_, centroid):
        self.id, self.centroid = id_, centroid
        self.activities = []
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __repr__(self):
        return "LC%d" % self.id
    
    def __str__(self):
        return "%d: %s" % (self.id, self.activities)
    
    def add_activity(self, activity, capacity):
        self.activities.append((activity, capacity))
    

