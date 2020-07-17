# Taylor Maxfield, 001227054

import csv
import datetime
import pathlib

import PackageHashTable
import DistanceTable
import deliverystatus
import Truck
import calc

# Constants
NOT_AT_DEPOT = deliverystatus.DeliveryStatus.NOT_AT_DEPOT.value
AT_DEPOT = deliverystatus.DeliveryStatus.AT_DEPOT.value
IN_ROUTE = deliverystatus.DeliveryStatus.IN_ROUTE.value
DELIVERED = deliverystatus.DeliveryStatus.DELIVERED.value

todays_date = datetime.date.today()

SPECIFIC_PACKAGE_MODE = "Specific package mode"
REGULAR_MODE = "Regular mode"


# Class used to store mode user chooses and the time of the delivery they wish to see
class UserModeAndTime:
    def __init__(self, mode, time):
        self.mode = mode
        self.time = time


# Gets what mode and time the user wants
# RUNTIME COMPLEXITY is O(1)
def get_user_mode_and_time():
    is_input_valid = False
    while is_input_valid is False:
        user_choice = input("PROGRAM OPTIONS\n"
                            "1 - View status of packages at a specific time\n" +
                            "2 - Run program and see status of packages every ten minutes until all are delivered\n" +
                            "Which option do you choose? 1 or 2: ")
        if user_choice == "1":
            while is_input_valid is False:
                input_time = input("What time (e.g. 9:38 AM): ")
                # Makes sure time has AM or PM at the end in order to properly make a datetime object to store the time the user wishes to view the package status
                if input_time[-2:].upper() == "AM" or input_time[-2:].upper() == "PM":
                    specific_time_string = todays_date.isoformat() + " " + input_time
                    specific_time = datetime.datetime.strptime(specific_time_string, "%Y-%m-%d %I:%M %p")
                    print(specific_time_string)
                    return UserModeAndTime(SPECIFIC_PACKAGE_MODE, specific_time)
                else:
                    print("ERROR: time must include AM or PM at end (e.g. 10:30 AM), try again --")

        elif user_choice == "2":
            return UserModeAndTime(REGULAR_MODE, None)
        else:
            print("\nERROR: invalid input, try again --\n")


# Recalculates the route for a truck from the current hub in transit to and after
# RUNTIME COMPLEXITY is O(N^2)
def recalculate_route(truck):
    # TODO see how to make it so the total distance is correct, and that the distance the truck is
    #  from the hub it is in transit to carries over

    index_of_last_hub_visited = truck.index_of_hub_in_transit_to - 1
    index_of_hub_in_transit_to = truck.index_of_hub_in_transit_to

    # To preserve the intent of the route (i.e. return to HUB to load more packages), any hub with an address of
    # "HUB" from index_of_hub_in_transit_to to the end must be kept in same position. Therefore stores index
    # for later reinsertion
    # RUNTIME COMPLEXITY is O(N)
    indexes_of_HUB_hubs = []
    for index, hub in enumerate(truck.current_route[index_of_hub_in_transit_to:]):
        if hub == "HUB":
            # Because only iterating over elements AFTER index_of_last_hub_visited (which will be index 0 of hubs),
            # 1 must be added to index to preserve original position
            indexes_of_HUB_hubs.append(index + 1)

    # For the calculation to work, the first index of hubs must be the index of the hub that was just visited and the
    # second index must be the index of the hub about to be visited
    hubs = [truck.current_route[index_of_last_hub_visited],
            truck.current_route[index_of_hub_in_transit_to]]
    # TESTS
    # print("////////////////////////////////////////////////////////////////////////////////////////////")
    # print("// index of last hub:", (truck.index_of_hub_in_transit_to - 1), ", last hub:",
    #       truck.current_route[truck.index_of_hub_in_transit_to - 1], "|", "index of current hub in transit to:",
    #       (truck.index_of_hub_in_transit_to), ", current hub in transit to:",
    #       truck.current_route[truck.index_of_hub_in_transit_to])

    # Adds all hubs that have not been visited to hubs.
    # RUNTIME COMPLEXITY is O(N^2) because during each iteration, all the hubs must be checked
    for package in truck.packages:
        if (package.delivery_status != DELIVERED) and (package.delivery_address not in hubs):
            hubs.append(package.delivery_address)

    # inserts "HUB" hubs at correct index
    # RUNTIME COMPLEXITY is O(N^2) because it has a nested for-loop
    for i in range(len(hubs)):
        for j in indexes_of_HUB_hubs:
            if i == j:
                hubs.insert(j, "HUB")
    # TESTS
    # print("// hubs preprocessed before recalculation:", hubs)
    # print("// hubs[1:] passed as hubs to calculate_route_for truck for route recalculation", hubs[1:])

    # Calculates the best route through all hubs that have not been visited (i.e. all hubs after index 0)
    # RUNTIME COMPLEXITY is that of calculate_route_for_truck which is O(N^2)
    hubs[1:] = calc.calculate_route_for_truck(hubs[1:], truck.distance_table, truck.packages,
                                              truck.current_time,
                                              Truck.SPEED_IN_MILES_PER_MINUTE)
    # TESTS
    # print("///////////////////////////// RECALCULATED ROUTE:", hubs)
    # print("////////////////////////////////////////////////////////////////////////////////////////////")

    # Assigns the trucks current route to recalculated route stored in hubs
    truck.current_route = hubs
    # Because truck has new route the index must be set back to 1
    truck.index_of_hub_in_transit_to = 1


# Enables user to change delivery requirements for packages
# RUNTIME COMPLEXITY is O(N^2)
def show_user_options(truck):
    # finds out if user wishes to make a change
    print("Options for Truck <" + str(truck.TRUCK_NUMBER) + ">:")
    make_a_change = input((" " * 4) + "Do you wish to change a package's delivery requirements? y or n: ")

    if (make_a_change.upper() == "Y") or (make_a_change.upper() == "YES"):

        # gets which package to change
        # RUNTIME COMPLEXITY is that of package_hash_table.get() which is O(N)
        done = False
        while done is False:
            which_package = package_hash_table.get(int(input((" " * 4) + "Enter the packages ID: ")))
            if which_package is None:
                print((" " * 4) + "ERROR: Invalid ID, try again --")
            else:
                done = True

        # gets which requirement to change
        done = False
        while done is False:
            what_change = input(
                (" " * 8) + "1 - delivery deadline\n" +
                (" " * 8) + "2 - special note\n" +
                (" " * 8) + "3 - wrong address\n" +
                (" " * 8) + "Which option do you wish to change? 1 or 2 or 3: " +
                "")
            # changes package's deadline
            # RUNTIME COMPLEXITY is that of recalculate_route() which is O(N^2)
            if what_change == "1":
                valid_input = False
                while valid_input is False:
                    user_input_deadline = input((" " * 12) + "Enter new deadline (e.g. 10:27 AM): ")
                    if user_input_deadline[-2:].upper() == "AM" or user_input_deadline[-2:].upper() == "PM":
                        which_package.delivery_deadline = user_input_deadline
                        valid_input = True
                    else:
                        print((" " * 12) + "ERROR: deadline must include AM or PM at end (e.g. 10:30 AM), try again --")
                done = True
                # recalculates route because a deadline has changes so hubs need to be reordered
                recalculate_route(truck)

            # changes package's special note
            # RUNTIME COMPLEXITY is that of recalculate_route() which is O(N^2)
            elif what_change == "2":
                special_note = input((" " * 12) + "Enter special note: ")
                which_package.special_note = special_note
                done = True
                recalculate_route(truck)

            # changes package's delivery address
            elif what_change == "3":
                if which_package.special_note == "Wrong address listed":
                    new_address = input((" " * 12) + "Enter new address: ")
                    which_package.delivery_address = new_address
                    done = True
                else:
                    print((" " * 8) + "ERROR: Package's special note does not state \"Wrong address listed\", " +
                          "therefore address cannot be changed until special note is changed --")
            else:
                print((" " * 12) + "ERROR: Invalid option (must be 1 or 2), try again --")


# prints all the information about all the packages
# RUNTIME COMPLEXITY is O(1)
def print_packages_status(packages):
    for package in packages:
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


# PACKAGE FILE
# -------------------------------------------------------------------------------------------------
# gets package csv file stored in current working directory in folder "csv_files"
package_file = pathlib.Path.cwd() / pathlib.Path('csv_files', 'WGUPS Package File (1).csv')

# RUNTIME COMPLEXITY is O(N)
with open(package_file) as package_csv_file:
    reader = csv.reader(package_csv_file, delimiter=',')
    info_for_packages = [package_info for package_info in reader]

# IMPORTANT VARIABLE: Stores info for packages
package_hash_table = PackageHashTable.PackageHashTable(40)

# places each package_info into package_hash_table
# RUNTIME COMPLEXITY is O(N^2) because it contains a for-loop that contains an operation whose complexity is O(N)
for package_info in info_for_packages:
    package_id_number = int(package_info[0])
    delivery_address = package_info[1]
    delivery_deadline = package_info[5]
    delivery_city = package_info[2]
    delivery_zip_code = package_info[4]
    package_weight = int(package_info[6])
    # TODO find out how to get "Must be delivered with 15, 19" to appear in package_info[6!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    note = package_info[7]

    # if special note says "Delayed on flight" then the package is not at the depot.
    if "Delayed on flight" in note:
        delivery_status = NOT_AT_DEPOT
    else:
        delivery_status = AT_DEPOT

    # puts in hash table
    # RUNTIME COMPLEXITY for package_hash_table.put() is O(N)
    package_hash_table.put(package_id_number, delivery_address, delivery_deadline, delivery_city, delivery_zip_code,
                           package_weight, delivery_status)

    # puts valid note in the special_note field of the corresponding package
    # RUNTIME COMPLEXITY for package_hash_table.get() is O(N)
    if note != "":
        package_hash_table.get(package_id_number).special_note = note

# DISTANCE FILE
# --------------------------------------------------------------------------------------
# gets distance csv file stored in current working directory in folder "csv_files"
distance_file = pathlib.Path.cwd() / pathlib.Path('csv_files', 'WGUPS Distance Table.csv')

# RUNTIME COMPLEXITY is O(N)
with open(distance_file) as distance_csv_file:
    reader = csv.reader(distance_csv_file, delimiter=',')
    info_for_hubs = [hub_info for hub_info in reader]

# stores at which index the address is stored in a hub_info item
ADDRESS_INDEX = 0
address_list = []

# gets all the addresses in info_for_hubs and stores them in address_list
for hub_info in info_for_hubs:
    # gets substring of address in hub_info that does not contain zip code
    if hub_info[ADDRESS_INDEX] == ' HUB':
        address_list.append(hub_info[ADDRESS_INDEX][1:])
    else:
        address_list.append(hub_info[ADDRESS_INDEX][1:-8])

# IMPORTANT VARIABLE: distance_table stores distances between hubs
distance_table = DistanceTable.DistanceTable()

# places all pairs of hubs and their distances in distance_table
# RUNTIME COMPLEXITY is O(N^2) because it contains a nested for-loop
for hub_info in info_for_hubs:
    hub1 = hub_info[ADDRESS_INDEX][1:-8]
    # Iterates over each entry after address_index in hub_info and and puts hub1, hub2 and distance in distance_table.
    # Breaks when '' encountered because that signifies that no more distances are stored
    for i in range((ADDRESS_INDEX + 1), len(hub_info)):
        distance = hub_info[i]
        if distance != '':
            hub2 = address_list[i - 1]
            distance_table.put(hub1, hub2, distance)
        else:
            break

# TRUCKS
# ------------------------------------------------------------------------------------------------------------
# IMPORTANT VARIABLES: truck1 and truck2
START_TIME = datetime.datetime(todays_date.year, todays_date.month, todays_date.day, hour=8)  # start time is 8 am

# TEST
# print("###############################################")

# GETS PACKAGES FOR FIRST ROUTE FROM package_hash_table
# RUNTIME COMPLEXITY is O(N^2) because package_hash_table.get() has a complexity of O(N) and it is executed N times
package_ids_for_truck_1 = [14, 15, 16, 34, 20, 21, 19, 13, 39, 27, 35]
packages_for_truck_1 = [package_hash_table.get(package_id_number) for package_id_number in package_ids_for_truck_1]
package_ids_for_truck_2 = [24, 22, 18, 11, 23]
packages_for_truck_2 = [package_hash_table.get(package_id_number) for package_id_number in package_ids_for_truck_2]

# first address must be HUB because that is starting point for trucks
addresses_for_truck_1 = ["HUB"]
addresses_for_truck_2 = ["HUB"]

# Sets the status for all the packages in both trucks to IN_ROUTE
# and appends their first route addresses to the addresses_for_truck_<number> list
# RUNTIME COMPLEXITY is O(N^2) because it contains a nested for-loop
for address in address_list:
    for package in packages_for_truck_1:
        package.delivery_status = IN_ROUTE
        if package.delivery_address == address:
            addresses_for_truck_1.append(address)
    for package in packages_for_truck_2:
        package.delivery_status = IN_ROUTE
        if package.delivery_address == address:
            addresses_for_truck_2.append(address)

# TESTS
# print("## addresses_1", addresses_for_truck_1)
# print("## len(addresses_1)", len(addresses_for_truck_1))
# print("## addresses_2", addresses_for_truck_2)
# print("## len(addresses_2)", len(addresses_for_truck_2))

# calculates first route for trucks
# RUNTIME COMPLEXITY is that of calc.calulate_route_for_truck() which is O(N^2)
first_route_for_truck_1 = calc.calculate_route_for_truck(addresses_for_truck_1, distance_table, packages_for_truck_1,
                                                         START_TIME,
                                                         Truck.SPEED_IN_MILES_PER_MINUTE)
first_route_for_truck_2 = calc.calculate_route_for_truck(addresses_for_truck_2, distance_table, packages_for_truck_2,
                                                         START_TIME,
                                                         Truck.SPEED_IN_MILES_PER_MINUTE)
# TESTS
# print("################ initial chosen route_1", first_route_for_truck_1)
# print("################ initial chosen route_2", first_route_for_truck_2)
# dis = 0
# for i in range(len(first_route_for_truck_1) - 1):
#     dis += distance_table.find_distance_between_hubs(first_route_for_truck_1[i], first_route_for_truck_1[i + 1])
#     print("# distance between hubs in route_1",
#           distance_table.find_distance_between_hubs(first_route_for_truck_1[i], first_route_for_truck_1[i + 1]))
# print("## total distance truck_1 should cover", dis)
# dis = 0
# for i in range(len(first_route_for_truck_2) - 1):
#     dis += distance_table.find_distance_between_hubs(first_route_for_truck_2[i], first_route_for_truck_2[i + 1])
#     print("# distance between hubs in route_2",
#           distance_table.find_distance_between_hubs(first_route_for_truck_2[i], first_route_for_truck_2[i + 1]))
# print("## total distance truck_2 should cover", dis)

# CREATES TRUCKS and sets their current route and packages to the first route and initial packages
truck_1 = Truck.Truck(1, START_TIME, distance_table)
truck_1.current_route = first_route_for_truck_1
truck_1.packages = packages_for_truck_1

truck_2 = Truck.Truck(2, START_TIME, distance_table)
truck_2.current_route = first_route_for_truck_2
truck_2.packages = packages_for_truck_2


# Gets everything ready for second route calculation which will be made at runtime
# RUNTIME COMPLEXITY is O(N^2) because package_hash_table.get() has a complexity of O(N) and it is executed N times
package_ids_for_truck_1 = [12, 17, 28, 2, 33, 7, 29, 10]
packages_for_truck_1 = [package_hash_table.get(package_id_number) for package_id_number in package_ids_for_truck_1]
package_ids_for_truck_2 = [25, 26, 31, 32, 6, 4, 40, 1, 5, 37, 38, 8, 9, 30, 3, 36]
packages_for_truck_2 = [package_hash_table.get(package_id_number) for package_id_number in package_ids_for_truck_2]

addresses_for_truck_1 = ["HUB"]
addresses_for_truck_2 = ["HUB"]

# appends packages delivery addresses for second route to the addresses_for_truck_<number> list
# RUNTIME COMPLEXITY is O(N^2) because it contains a nested for-loop
for address in address_list:
    for package in packages_for_truck_1:
        if (package.delivery_address == address) and (address not in addresses_for_truck_1):
            addresses_for_truck_1.append(address)
    for package in packages_for_truck_2:
        if (package.delivery_address == address) and (address not in addresses_for_truck_2):
            addresses_for_truck_2.append(address)

# TESTS
# print("## 2nd addresses_1", addresses_for_truck_1)
# print("## 2nd len(addresses_1)", len(addresses_for_truck_1))
# print("## 2nd addresses_2", addresses_for_truck_2)
# print("## 2nd len(addresses_2)", len(addresses_for_truck_2))
#
# print("###############################################")

# creates list of all times from 8:00:00 to 17:59:59 for use in main method
# RUNTIME COMPLEXITY is O(1) because it is the same no matter how large input is
times = []
for i in range(8, 17):
    for j in range(0, 60, 1):
        for k in range(0, 60, 1):
            times.append(
                datetime.datetime(todays_date.year, todays_date.month, todays_date.day, hour=i, minute=j, second=k))


# MAIN
# ------------------------------------------------------------------------------------------------------------
# TIME COMPLEXITY of entire program is O(N^3) because that is the highest order term in the program
def main(truck_1, truck_2):
    # variables used to determine when important events during delivery have occurred
    all_packages_delivered = False
    first_route_for_truck_1_completed = False
    first_route_for_truck_2_completed = False

    # stores time when delayed packages will arrive in a time object
    time_delayed_packages_will_arrive = datetime.time(hour=9, minute=5)

    # Stores old route's length so we can know when new route has started
    old_route_for_truck_1_length = len(truck_1.current_route)
    old_route_for_truck_2_length = len(truck_2.current_route)

    # gets which mode and possibly which time the user wants
    # RUNTIME COMPLEXITY is that of get_user_mode_and_time() which is O(1)
    user_mode_and_time = get_user_mode_and_time()

    is_time_to_print_status = False

    # Loops through the times stored in times, which are from 8:00:00 to 17:59:59, untill all packages have been
    # delivered RUNTIME COMPLEXITY is O(N^3) because it contains a for-loop that does N operations with a time
    # complexity of O(N^2)
    ending_time = None
    for time in times:
        if all_packages_delivered is False:

            # Sets Boolean value that determines when to print the status of the packages
            if user_mode_and_time.mode == REGULAR_MODE:
                is_time_to_print_status = (time.minute % 10 == 0) and (time.second % 60 == 0)
            elif user_mode_and_time.mode == SPECIFIC_PACKAGE_MODE:
                is_time_to_print_status = (time == user_mode_and_time.time)

            # Sets all delayed packages' status to AT_DEPOT when the time has come when they have arrived at depot
            # RUNTIME COMPLEXITY is O(N)
            if time == time_delayed_packages_will_arrive:
                for package in package_hash_table.get_list_of_packages():
                    if "Delayed on flight" in package.special_note:
                        package.delivery_status = AT_DEPOT

            # Truck 1
            # ----------------------------------------------------------------------------------------------------------
            # updates truck 1's distance_traveled and hub-in-transit-to
            # RUNTIME COMPLEXITY is that of update() which is O(N^2)
            if truck_1.visited_all_assigned_hubs is False:
                truck_1.update(time)

            # Prints the packages' status differently depending on which mode the user is in
            # RUNTIME COMPLEXITY is O(1)
            if is_time_to_print_status and user_mode_and_time.mode == REGULAR_MODE:
                print()
                print(
                    "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = "
                    "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = "
                    "= = = = = = = = = =")
                truck_1.print_status()
                print()
                print("Current Time:", time)
                print()

            elif is_time_to_print_status and user_mode_and_time.mode == SPECIFIC_PACKAGE_MODE:
                print()
                print(
                    "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = "
                    "= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = "
                    "= = = = = = = = = =")
                package_hash_table.get_list_of_packages(print_package_status=True)
                print()
                print("Current Time:", time)
                print()
                print((" " * 8) + "TOTAL COMBINED MILES:",
                      str(truck_1.total_miles_traveled + truck_2.total_miles_traveled))
                print()

            # Adds second route when truck_1 at hub before last hub in route, then sets
            # first_route_for_truck_1_completed to True so this is never done again.
            # RUNTIME COMPLEXITY is that of calc.calculate_route_for_truck() which is O(N^2)
            if (truck_1.index_of_hub_in_transit_to == (len(truck_1.current_route) - 1)) and (
                    first_route_for_truck_1_completed is False):
                truck_1.current_route += calc.calculate_route_for_truck(addresses_for_truck_1, distance_table,
                                                                        packages_for_truck_1, START_TIME,
                                                                        Truck.SPEED_IN_MILES_PER_MINUTE)
                truck_1.packages += packages_for_truck_1
                first_route_for_truck_1_completed = True

            # Sets newly picked up package's status to IN_ROUTE
            # RUNTIME COMPLEXITY is O(N) because it contains a for-loop
            if truck_1.index_of_hub_in_transit_to >= old_route_for_truck_1_length + 1:
                for package in truck_1.packages:
                    if package.delivery_status != DELIVERED:
                        package.delivery_status = IN_ROUTE

            # Gives user opportunity to change delivery requirements
            # RUNTIME COMPLEXITY is that of show_user_options() which is O(N^2)
            if is_time_to_print_status:
                show_user_options(truck_1)
                print()

            # Truck 2
            # ---------------------------------------------------------------------------------------------
            # updates truck 1's distance_traveled and hub-in-transit-to
            # RUNTIME COMPLEXITY is is that of update() which is O(N^2)
            if truck_2.visited_all_assigned_hubs is False:
                truck_2.update(time)

            # RUNTIME COMPLEXITY is O(1)
            if is_time_to_print_status and user_mode_and_time.mode == REGULAR_MODE:
                truck_2.print_status()
                print()
                print("Current Time:", time)
                print()

            # Adds second route when truck_2 at hub before last hub in route then sets
            # first_route_for_truck_2_completed to True so this is never done again
            # RUNTIME COMPLEXITY is that of calc.calculate_route_for_truck() which is O(N^2)
            if (truck_2.index_of_hub_in_transit_to == len(truck_2.current_route) - 1) and (
                    first_route_for_truck_2_completed is False):
                truck_2.current_route += calc.calculate_route_for_truck(addresses_for_truck_2, distance_table,
                                                                        packages_for_truck_2, START_TIME,
                                                                        Truck.SPEED_IN_MILES_PER_MINUTE)
                truck_2.packages += packages_for_truck_2
                first_route_for_truck_2_completed = True

            # Sets newly picked up package's status to IN_ROUTE
            # RUNTIME COMPLEXITY is O(N) because it contains a for-loop
            if truck_2.index_of_hub_in_transit_to == old_route_for_truck_2_length + 1:
                for package in truck_2.packages:
                    if package.delivery_status != DELIVERED:
                        package.delivery_status = IN_ROUTE

            # Gives user opportunity to change delivery requirements
            # RUNTIME COMPLEXITY is that of show_user_options() which is O(N^2)
            if is_time_to_print_status and user_mode_and_time.mode == REGULAR_MODE:
                show_user_options(truck_2)

            # checks if all packages have been delivered. If so then time for loop will end do to last else
            # RUNTIME COMPLEXITY is O(N) because it contains a for-loop
            all_packages_delivered = True
            for package in package_hash_table.get_list_of_packages():
                if package.delivery_status != DELIVERED:
                    all_packages_delivered = False
                    break

            # # TODO unnecessary if use one above
            # if first_route_for_truck_1_completed and truck_1.visited_all_assigned_hubs and \
            #         first_route_for_truck_2_completed and truck_2.visited_all_assigned_hubs:
            #     all_packages_delivered = True

       # Breaks out of for loop when all packages have been delivered
        else:
            ending_time = time
            break

    # Prints final information and combined miles traveled for both trucks
    # TIME COMPLEXITY is O(1)
    print()
    package_hash_table.get_list_of_packages(print_package_status=True)
    if user_mode_and_time.time != None:
        print()
        print("Current Time:", user_mode_and_time.time)
    print()
    print((" " * 8) + "***********************************************************************")
    print((" " * 8) + " ALL PACKAGES DELIVERED AT:", ending_time)
    print((" " * 8) + " TOTAL COMBINED MILES:", str(truck_1.total_miles_traveled + truck_2.total_miles_traveled))
    print((" " * 8) + "***********************************************************************")



# calls main function
main(truck_1, truck_2)
# -------------------------------------------------------------------------------------------------------------------
