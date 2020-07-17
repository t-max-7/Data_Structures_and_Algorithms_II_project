

# Class that contains a table that store DistanceRelationship objects consisting of a frozenset containing a pair of
# hubs and the distance between them.
class DistanceTable:

    def __init__(self):
        self.table_size = 378
        self.table = [[] for i in range(self.table_size)]

    # Method for adding a DistanceRelationship to the table
    # RUNTIME COMPLEXITY is O(N) because has a for loop
    def put(self, hub1, hub2, distance):
        pair_of_hubs = frozenset([hub1, hub2])
        distance_relationship_to_add = DistanceRelationShip(pair_of_hubs, float(distance))
        # Hashes frozenset storing hub pair.
        key = hash(distance_relationship_to_add.pair_of_hubs) % self.table_size

        # If distance_relationship_to_add's pair of hubs is equal to one already in table
        # then it replaces the existing one
        for index, existing_distance_relationship in enumerate(self.table[key]):
            if distance_relationship_to_add.pair_of_hubs == existing_distance_relationship.pair_of_hubs:
                self.table[key][index] = distance_relationship_to_add
                return
        self.table[key].append(distance_relationship_to_add)

    # Method for getting a DistanceRelationship that corresponds to a pair of hubs
    # RUNTIME COMPLEXITY is O(N) because it has a for-loop
    def get(self, hub1, hub2):
        pair_of_hubs = frozenset([hub1, hub2])
        key = hash(pair_of_hubs) % self.table_size

        for distance_relationship in self.table[key]:
            if distance_relationship.pair_of_hubs == pair_of_hubs:
                return distance_relationship
        return None

    # Method that returns the distance between two hubs
    # RUNTIME COMPLEXITY is that of self.get() which is O(N)
    def find_distance_between_hubs(self, hub1, hub2):
        if self.get(hub1, hub2) is None:
            return None
        else:
            return self.get(hub1, hub2).distance


# Class storing pairs of hubs and the distance between them
class DistanceRelationShip:
    def __init__(self, pair_of_hubs, distance):
        self.pair_of_hubs = pair_of_hubs
        self.distance = distance
