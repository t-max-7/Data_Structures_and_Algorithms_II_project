# Class for storing package information
class Package:
    def __init__(self, package_id_number, delivery_address, delivery_deadline, delivery_city, delivery_zip_code,
                 package_weight, delivery_status):
        self.package_id_number = package_id_number
        self.delivery_address = delivery_address
        self.delivery_deadline = delivery_deadline
        self.delivery_city = delivery_city
        self.delivery_zip_code = delivery_zip_code
        self.package_weight = package_weight
        # delivery_status should be a deliverystatus.DeliveryStatus. one of the enum types .value
        self.delivery_status = delivery_status

        self.special_note = None
        self.delivery_time = None


# Class with a table to store packages
class PackageHashTable:
    def __init__(self, table_size):
        self.table_size = table_size
        self.table = [[] for i in range(self.table_size)]

    # Method that inserts Packages into hash table and returns None. If Package with matching package_id_number is
    # already in the table then that Package is replaced and returned by method
    # RUNTIME COMPLEXITY is O(N) because it has a for-loop
    def put(self, package_id_number, delivery_address, delivery_deadline, delivery_city, delivery_zip_code,
            package_weight, delivery_status):

        key = hash(package_id_number) % self.table_size
        package_to_add = Package(
            package_id_number, delivery_address, delivery_deadline, delivery_city, delivery_zip_code, package_weight,
            delivery_status)
        # If both Packages' package_id_number match then replaces package with package_to_add and returns old_package
        for index, package in enumerate(self.table[key]):
            if package.package_id_number == package_to_add.package_id_number:
                old_package = self.table[key][index]
                self.table[key][index] = package_to_add
                return old_package
        # If Package has unique package_id_number then method appends package_to_add to list at the bucket located at
        # index key
        self.table[key].append(package_to_add)
        return None

    # Method that looks up and returns Package based on package_id_number. If Package is not found then it returns None
    # RUNTIME COMPLEXITY is O(N) because it has a for-loop
    def get(self, package_id_number):
        key = hash(package_id_number) % self.table_size
        package_found = False
        for package in self.table[key]:
            if package.package_id_number == package_id_number:
                package_found = True
                return package
        # TODO see if there is a better way to do this. Make sure it is commented
        if package_found is False:
            return None

    # Method that returns all packages stored in table as a list
    # RUNTIME COMPLEXITY is O(N^2) because has a nested for-loop
    def get_list_of_packages(self, print_package_status=False):
        packages = []
        for row in self.table:
            for package in row:
                packages.append(package)

                if print_package_status is True:
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
        return packages
