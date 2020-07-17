import datetime

import deliverystatus

# Constants
DELIVERED = deliverystatus.DeliveryStatus.DELIVERED.value
# Truck can go 18 miles/hour therefore can go 18/60 = 0.3 miles/min
SPEED_IN_MILES_PER_MINUTE = 0.3


# Class to simulate a truck delivering packages
class Truck:
    # START_TIME should be a datetime.datetime object which stores time IN 24 HOUR CLOCK FORMAT!!
    #                                                              -------------------------
    def __init__(self, TRUCK_NUMBER, START_TIME, distance_table):
        self.TRUCK_NUMBER = TRUCK_NUMBER
        self.START_TIME = START_TIME
        self.distance_table = distance_table

        self.current_route = []
        # set to 1 because truck is already at hub at index 0
        self.index_of_hub_in_transit_to = 1

        self.packages = []
        # TODO figure out what to put here
        self.current_time = START_TIME

        self.miles_till_reach_next_hub = -1
        self.total_miles_traveled = 0

        self.visited_all_assigned_hubs = False
        self.miles_past_truck_stopping_point = 0

    # Method that updates the instance variable of the truck object
    # based on the duration of time that has transpired after the truck's start time.
    # new_time should be a datetime.datetime object which stores time IN 24 HOUR CLOCK FORMAT!!
    #                                                                -------------------------
    # RUNTIME COMPLEXITY is O(N^2) because of the use of the update_truck_position() method
    # TODO see if can make update() pause truck positon while at hub until the time that delayed packages arrives

    def update(self, new_time):
        # calculates distance traveled from current_time to new_time
        elapsed_time = new_time - self.current_time  # elapsed_time is a timedelta object
        elapsed_time_in_minutes = (elapsed_time.total_seconds() / 60)
        miles_traveled = SPEED_IN_MILES_PER_MINUTE * elapsed_time_in_minutes

        # Updates truck's position after traveling miles_traveled, which also updates what packages are delivered
        # and what the next hub the truck is heading towards is. Method requires non-updated time.
        self.update_truck_position(miles_traveled, self.current_time)

        # updates current time
        self.current_time = new_time

        # updates total distance traveled
        self.total_miles_traveled += miles_traveled

    # Method that delivers packages, updates index_of_hub_in_transit_to, and updates miles_till_reach_next_hub
    # Returns number of hubs that have been visited after update to truck position
    # RUNTIME COMPLEXITY is O(N^2)
    def update_truck_position(self, miles_traveled, start_time):
        # used for first time this function is called
        # RUNTIME COMPLEXITY is O(N) because of the use of the distance_table.find_distance_between_hubs method
        if self.miles_till_reach_next_hub == -1:
            self.miles_till_reach_next_hub = self.distance_table.find_distance_between_hubs(self.current_route[0],
                                                                                            self.current_route[1])
        # Calculates time_of_delivery, delivers packages, increments INDEX_OF_HUB_IN_TRANSIT_TO, and sets
        # self.miles_till_reach_next_hub equal to the miles_away of the hub the truck is in transit to.
        # Must do this differently depending on how many miles have been traveled

        # In this case truck has arrived exactly at next hub
        # RUNTIME COMPLEXITY is O(N) because of use of the deliver_packages()
        # and update_miles_till_reach_next_hub() methods
        if miles_traveled == self.miles_till_reach_next_hub:
            # TODO CHECK TIME IS RIGHT
            time_of_delivery = start_time + datetime.timedelta(
                minutes=(self.miles_till_reach_next_hub / SPEED_IN_MILES_PER_MINUTE))
            self.deliver_packages(self.index_of_hub_in_transit_to, time_of_delivery)
            self.index_of_hub_in_transit_to += 1
            self.update_miles_till_reach_next_hub()

            return 1

        # In this case truck has gone past next hub
        # RUNTIME COMPLEXITY is O(N^2) because the worst case calls update_truck_position() N times
        elif miles_traveled > self.miles_till_reach_next_hub:
            # TODO CHECK TIME IS RIGHT
            miles_traveled = miles_traveled - self.miles_till_reach_next_hub

            time_of_delivery = start_time + datetime.timedelta(
                minutes=(self.miles_till_reach_next_hub / SPEED_IN_MILES_PER_MINUTE))
            self.deliver_packages(self.index_of_hub_in_transit_to, time_of_delivery)
            self.index_of_hub_in_transit_to += 1
            # Passes miles_traveled to self.update_miles_till_reach_next_hub because there is a chance that the Truck
            # may visit all hubs during this iteration. If this is true then the Truck will stop at a distance
            # before the current value stored in self.total_distance_traveled
            self.update_miles_till_reach_next_hub(miles_traveled)

            if self.visited_all_assigned_hubs is False:
                # miles_traveled = miles_traveled - self.miles_till_reach_next_hub
                return 1 + self.update_truck_position(miles_traveled, time_of_delivery)
            else:
                return 1

        # In this case truck has not yet reached next hub
        # RUNTIME COMPLEXITY O(1)
        else:
            self.miles_till_reach_next_hub -= miles_traveled

            return 0

    # Sets all packages whose address is the current hub to delivered and sets their time of delivery
    # RUNTIME COMPLEXITY is O(N) because has a for-loop
    def deliver_packages(self, index_of_hub_arrived_at, time_of_delivery):
        for index, package in enumerate(self.packages):
            if (package.delivery_status != DELIVERED
            ) and (
                    package.delivery_address == self.current_route[index_of_hub_arrived_at]):
                self.packages[index].delivery_status = DELIVERED
                self.packages[index].delivery_time = time_of_delivery

        # prints the time when truck arrives at HUB to pick up more packages
        if (self.visited_all_assigned_hubs is False) and self.current_route[index_of_hub_arrived_at] == "HUB":
            print(
                "**************************************************************************************************************************")
            print("Truck <" + str(self.TRUCK_NUMBER) + "> Reached HUB to pick up delayed packages at", time_of_delivery)
            print(
                "**************************************************************************************************************************")

            # gets user's acknowledgement
            user_input = "None"
            while user_input.upper() != "OK":
                user_input = input("Type OK to continue: ")

    # Method that tests if all hubs have been visited and if not sets self.miles_till_reach_next_hub equal to the
    # distance between current hub and the next hub the truck is in transit to.
    # RUNTIME COMPLEXITY is O(N) because of the use of the distance_table.find_distance_between_hubs method
    def update_miles_till_reach_next_hub(self, miles_past_truck_stopping_point=0):
        if self.index_of_hub_in_transit_to < len(self.current_route):
            current_hub = self.current_route[self.index_of_hub_in_transit_to - 1]
            hub_in_transit_to = self.current_route[self.index_of_hub_in_transit_to]

            # RUNTIME COMPLEXITY of find_distance_between_hubs is O(N)
            self.miles_till_reach_next_hub = self.distance_table.find_distance_between_hubs(current_hub,
                                                                                            hub_in_transit_to)
        # if index_of_hub_in_transit_to is >= than len(self.current_route) then the truck has visited all assigned hubs.
        # Because the truck stops once all hubs are visited but the full distance that the truck would have visited
        # is stored in self.total_miles_traveled, miles_passed_truck_stopping_point must be subtracted from it
        else:
            self.visited_all_assigned_hubs = True
            self.miles_past_truck_stopping_point = miles_past_truck_stopping_point
            self.total_miles_traveled -= miles_past_truck_stopping_point

    # Method that prints truck's package information and whether it has completed its route
    # RUNTIME COMPLEXITY O(1)
    def print_status(self):
        print(" _________________________________________________________________________________________________")
        print("|" + (" " * 3) + "Truck <" + str(self.TRUCK_NUMBER) + "> Information for Packages" + (" " * 60) + "|")
        print("|_________________________________________________________________________________________________|")

        for package in self.packages:
            print("package ID:", package.package_id_number,
                  "| delivery address:", package.delivery_address,
                  "| city:", package.delivery_city,
                  "| state:", "UT",
                  "| zip:", package.delivery_zip_code,
                  "| delivery deadline:", package.delivery_deadline,
                  "| mass KILO:", package.package_weight,
                  "| special note:", package.special_note,
                  "| delivery status:", package.delivery_status,
                  "| delivery time:", package.delivery_time,
                  )
        print()
        if self.index_of_hub_in_transit_to < len(self.current_route):
            print("Current route:", self.current_route)
            print("Truck <" + str(self.TRUCK_NUMBER) + "> is in transit to hub <" + self.current_route[
                self.index_of_hub_in_transit_to] + "> at index <" + str(
                self.index_of_hub_in_transit_to) + "> which is <" +
                  str(self.miles_till_reach_next_hub) + "> miles away")

        else:
            print("ROUTE COMPLETE:", self.visited_all_assigned_hubs)

        print("Total miles Truck <" + str(self.TRUCK_NUMBER) + "> has traveled:", self.total_miles_traveled)
