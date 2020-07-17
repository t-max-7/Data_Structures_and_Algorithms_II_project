import math
import datetime

import deliverystatus

DELIVERED = deliverystatus.DeliveryStatus.DELIVERED.value

# Class that stores a delivery address, the time that the address must be reached,
# and the distance from the starting HUB the address is
class DeadlineDistance:
    def __init__(self, delivery_address, delivery_deadline, distance_from_start_of_route):
        self.delivery_address = delivery_address
        self.delivery_deadline = delivery_deadline
        self.distance_from_start = distance_from_start_of_route


# TODO do delayed
# Returns route for a truck using a nearest neighbor algorithm that takes deadlines for delivery into account;
# start_time should be a datetime.datetime object
# RUNTIME COMPLEXITY is the runtime complexity of the highest order term which is O(N^2)
def calculate_route_for_truck(hubs, distance_table, packages, start_time, speed_of_truck_miles_per_minute, distance=0):
    # Makes hubs a copy so that it doesn't modify original list.
    # RUNTIME COMPLEXITY O(N)
    hubs = hubs[:]
    # Removes and stores first_hub because it must be first hub in route, so it cannot be subject to the same
    # manipulations that follow
    first_hub = hubs.pop(0)

    # Fills a list with UNIQUE DeadlineDistance objects from the packages' delivery deadlines. Therefore any duplicates
    # are not added.
    # RUNTIME COMPLEXITY is O(N^2) because there is a nested for-loop
    deadline_distances = []
    for package in packages:
        # Addresses of packages that have EOD deadline or have already been delivered are not added
        if package.delivery_deadline != "EOD" and package.delivery_status != DELIVERED:
            # Creates a datetime object from the package's delivery deadline
            todays_date = datetime.date.today()
            delivery_deadline_string = todays_date.isoformat() + " " + package.delivery_deadline
            delivery_deadline_datetime = datetime.datetime.strptime(delivery_deadline_string, "%Y-%m-%d %I:%M %p")
            # time_since_start is a datetime.timedelta object
            time_since_start_when_deadline_will_be_reached = delivery_deadline_datetime - start_time
            # Calculates package's delivery address's distance from HUB
            miles_till_reach_delivery_deadline = (time_since_start_when_deadline_will_be_reached.total_seconds() / 60) \
                                                 * speed_of_truck_miles_per_minute

            # Creates a DeadlineDistance object to add to deadline_distances list
            deadline_distance_to_add = DeadlineDistance(package.delivery_address, delivery_deadline_datetime,
                                                        miles_till_reach_delivery_deadline)

            # Checks if deadline_distance_to_add has the same address as a deadline_distance in deadline_distances.
            # If so then the one with earliest deadline will be stored in deadline_distances.
            # If deadline_distance_to_add is stored then removes the hub from hubs with the matching delivery_address
            match_less_than_current_found = False
            for deadline_distance in deadline_distances[:]:
                if deadline_distance.delivery_address == deadline_distance_to_add.delivery_address:
                    if deadline_distance_to_add.delivery_deadline < deadline_distance.delivery_deadline:
                        deadline_distances.remove(deadline_distance)
                        deadline_distances.append(deadline_distance_to_add)
                        match_less_than_current_found = True
                    break

            if match_less_than_current_found is False:
                deadline_distances.append(deadline_distance_to_add)

            if deadline_distance_to_add.delivery_address in hubs:
                hubs.remove(deadline_distance_to_add.delivery_address)

    # Sorts deadline_distances by delivery_deadline and distance from hub
    # then puts their addresses into hubs_with_deadlines.
    # RUNTIME COMPLEXITY should be O(N log N) assuming this implementation of Python uses Timsort
    deadline_distances.sort(key=lambda a: (a.delivery_deadline, distance_table.find_distance_between_hubs("HUB", a.delivery_address)))
    hubs_with_deadlines = [deadline_distance.delivery_address for deadline_distance in deadline_distances]

    # Prepends previously stored original first hub from hubs to hubs_with_deadlines
    # TEST: print("!! hubs_with_deadlines", hubs_with_deadlines)
    hubs_with_deadlines = [first_hub] + hubs_with_deadlines

    # Removes last hub from hubs_with_deadlines and prepends it to hubs
    hubs = [hubs_with_deadlines.pop()] + hubs

    # TEST: print("!! last hub with deadline:", hubs[0])

    # makes route_for_truck a list where the first element was the original first element of hubs,
    # the middle elements are the hubs with deadlines ordered from earliest deadline to latest deadline,
    # and the last elements are the hubs without deadlines ordered according to the output of nearest_neighbor_route()
    # i.e [original_first_element, hubs_with_deadlines..., hubs_without_deadlines...]
    # RUNTIME complexity is that of nearest_neighbor_route which is O(N^2)
    nearest_neighbor_path = nearest_neighbor_route(hubs, distance_table)
    route_for_truck = hubs_with_deadlines + nearest_neighbor_path

    # TESTS
    # print("!! hubs_with_deadlines", hubs_with_deadlines, "nearest_neighbor_route", nearest_neighbor_path)
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! route_for_truck", route_for_truck)

    return route_for_truck


# Nearest neighbor algorithm that calculates route based on which hub is the closest to current one
# RUNTIME COMPLEXITY is O(N^2)
def nearest_neighbor_route(hubs, distance_table):
    # makes hubs a copy so that it doesn't modify original list. RUNTIME COMPLEXITY is O(N)
    hubs = hubs[:]

    # TESTS
    # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    # print("<< starting hubs:", hubs)

    route = []

    # makes first hub in hubs the starting point in route, and removes it from hub
    starting_point = hubs[0]
    route.append(starting_point)
    del hubs[0]


    # Compares route[i] to all other hubs not already in route, to find the closest hub. That hub is then placed in
    # the next index of route and deleted from hubs so it is not compared in the next iteration.
    # RUNTIME COMPLEXITY is O(N^2) because has a nested for-loop
    original_length_of_hubs = len(hubs)
    i = 0
    for i in range(original_length_of_hubs):
        min_distance = math.inf
        closest_hub = None
        index_of_closest_hub = 0

        for j in range(len(hubs)):
            distance_between_hubs = distance_table.find_distance_between_hubs(hubs[j], route[i])
            if distance_between_hubs < min_distance:
                min_distance = distance_between_hubs
                closest_hub = hubs[j]
                index_of_closest_hub = j

        route.append(closest_hub)  # will be in route[i+1]
        del hubs[index_of_closest_hub]

        # TESTS
        # print("<< final hubs", hubs)
        # print("<< final route", route)

    # TESTS
    # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    return route
