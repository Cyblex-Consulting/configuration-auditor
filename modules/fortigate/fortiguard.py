import csv
import os

# FortiGuard App Control ID CSVs live in this module's libs/ submodule.
_LIBS_DIR = os.path.join(os.path.dirname(__file__), "libs", "FortigateAppControlID")


class Fortiguard:

    def __init__(self, verbose=False):

        print("[+] Loading fortiguard items")

        # Load fortiguard categories from files
        self.category_ids = {}
        self.category_names = {}
        i = 0
        with open(os.path.join(_LIBS_DIR, "Categories.csv"), "r+") as data:
            for line in csv.reader(data, delimiter=";"):
                if i > 0:
                    # Do not take into account column titles
                    self.category_ids[line[1]] = line[0]
                    self.category_names[line[0]] = line[1]
                i += 1

        print(f'[-] {i} categories imported')
        
        
        # Load fortiguard applications from files
        self.application_ids = {}
        self.application_names = {}
        i = 0
        with open(os.path.join(_LIBS_DIR, "Applications.csv"), "r+") as data:
            for line in csv.reader(data, delimiter=";"):
                if i > 0:
                    # Do not take into account column titles
                    self.application_ids[line[1]] = line[0]
                    self.application_names[line[0]] = line[1]
                i += 1

        print(f'[-] {i} applications imported')
        
    def category_id_from_name(self, name):
        if name in self.category_names.keys():
            return self.category_names[name]
        else:
            return None
    
    def category_name_from_id(self, id):
        if id in self.category_ids.keys():
            return self.category_ids[id]
        else:
            return None
    
    def application_id_from_name(self, name):
        if name in self.application_names.keys():
            return self.application_names[name]
        else:
            return None
    
    def application_name_from_id(self, id):
        if id in self.application_ids.keys():
            return self.application_ids[id]
        else:
            return None
    