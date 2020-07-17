
class SpecialNote:
    def __init__(self, package_id, note):
        self.package_id = package_id
        self.note = note


class SpecialNotesTable:
    # requirements is a list of tuples of form (package_id, special_note_string)
    def __init__(self):
        self.truck_notes = []
        self.delayed_notes = []
        self.delivery_notes = []
        self.address_notes = []

    def put(self, package_id_number, note):
        # Creates a SpecialNote and puts it into a table.
        # new_string only contains the important information of the string
        note_string = note
        if "Can only be on truck" in note_string:
            new_string = note_string[21:]
            note_to_add = SpecialNote(package_id_number, new_string)
            self.truck_notes.append(note_to_add)
        elif "Delayed on flight" in note_string:
            new_string = note_string[51:]
            note_to_add = SpecialNote(package_id_number, new_string)
            self.truck_notes.append(note_to_add)
        elif "Must be delivered with" in note_string:
            new_string = note_string[23:]
            # stores package ID's of packages that the package must be delivered with as a list
            packages_that_package_must_be_delivered_with = str.split(new_string, sep=",")
            note_to_add = SpecialNote(package_id_number, packages_that_package_must_be_delivered_with)
            self.truck_notes.append(note_to_add)
        elif "Wrong address" in note_string:
            new_string = "Wrong address"
            note_to_add = SpecialNote(package_id_number, new_string)
            self.truck_notes.append(note_to_add)

    def update(self, package_id, note):
        # if note exists in one of the tables, then deletes it and puts in new note

        truck_notes = self.truck_notes[:]
        for i in range(len(truck_notes)):
            if truck_notes[i].package_id == package_id:
                del self.truck_notes[i]
                self.put(package_id, note)
                return

        delayed_notes = self.delayed_notes[:]
        for i in range(len(delayed_notes)):
            if delayed_notes[i].package_id == package_id:
                del self.delayed_notes[i]
                self.put(package_id, note)
                return

        delivery_notes = self.delivery_notes[:]
        for i in range(len(delivery_notes)):
            if delivery_notes[i].package_id == package_id:
                del self.delivery_notes[i]
                self.put(package_id, note)
                return

        address_notes = self.truck_notes[:]
        for i in range(len(address_notes)):
            if address_notes[i].package_id == package_id:
                del self.address_notes[i]
                self.put(package_id, note)
                return

        self.put(package_id, note)
        return