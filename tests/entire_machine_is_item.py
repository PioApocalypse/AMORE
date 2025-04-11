import os
import sys
import json
import requests
from amore.api import client

'''
This approach assumes that every item from category "SAMPLE POSITIONS"
on our eLabFTW represents a different machine. This method keeps track
of sample position by assigning items to a metadata field in eLabFTW
whose key is the name/identifier of the slot. Example:

    "extra_fields": {
        "main sector": {
            "position 1": "Na-25-001",
            "position 2": "Na-25-002",
            ...
        },
        "other sector": {
            "position 3": "Na-25-003",
            ...
        },
        ...
        "LOST": {
            "lost 1": "Na-24-000",
            "lost 2": "other lost sample",
            ...
        }
    }
'''

positions = [
    "PLD1-Auxillary",
    "PLD1-Heater",
    "PLD1 - Chamber",
    "SPM - D - 1",
    "SPM-D-2",
    "SPM-D-3",
    "PLD1-LOST",
    "SPM-Lost",
    "Intro-1",
    "Intro-2",
    "Intro-lost" ]

class Instrument:
    def __init__(self,
                 title,
                 id,
                 metadata):
        self.title = title
        self.id = id
        self.meta = metadata # testing
        #self.meta = json.loads(metadata) # in practice
        self.extra = self.meta.get("extra_fields") or [""] # all keys in extra_fields must be names of slots
        self.groups = self.meta.get("elabftw").get("extra_fields_groups") or [""] # list of dictionaries containing every sector's id and name
    def getsectors(self): # returns list of sector ids and names
        sectors = [ { "id": item.get("id"), "name": item.get("name") } for item in self.groups ]
        return sectors
        #dic = self.meta.get("extra_fields_groups")[0]
        #return [ item.get('name') for item in dic ]
    def getslots(self):
        slotlist = []
        for slot in self.extra: # for every slot in extra fields
            slotname = f"{self.title} - {slot}"
            slotsample = self.extra.get(slot).get("value") # id, not title of sample - to get title requests.get is necessary
            slotgroup = self.extra.get(slot).get("group_id") # id, not name of sector
            slotsector = [item.get("name")
                for item in self.getsectors()
                if item.get("id") == slotgroup][0] # actual name of sector
            response = {
                "name": slotname,
                "sector": slotsector,
                "sample": slotsample # again: id not title
            }
            slotlist.append(response) # object containing full location of the slot ("name" key), sector name ("sector" key) and the sample associated ("sample" key)
        return slotlist
    def getmachine(self): # equivalent to self.title
        return self.title # if we opt for the "every machine is an item" approach
        #return self.data[0] # if we opt for the "every slot of every machine is an item" approach
    def getavailable(self):
        slotlist = self.getslots()
        available = [ { "name": f"{self.title} - LOST", "sector": "LOST", "sample": "" } ]
        for slot in slotlist:
            if slot.get("sample") == "":
                available.append(slot)
        return available
    def isthisloss(self): # returns full titles
        if self.data[-1].lower() == "lost":
            # I  II
            # II  L
            return True
        return False
    # def dump(self):
    #     for item in self.getslots():

    #     s = {
    #         "title": self.title,
    #         "id": self.id,
    #         "avail": self.avail,
    #         "machine": self.getmachine(),
    #         "slot": self.getslot(),
    #         "sector": self.getsector(),
    #         "lost": self.isthisloss()
    #         }
    #     return s

# def list_available_slots(dictlist):
#     parsed_dictlist = parse_slots(dictlist)
#     mylist = []
#     for item in parsed_dictlist:
#         if item.get('sector') == "LOST":
#             mylist.append( item.get('title') )
#         else:
#             id = item.get('id')
#             endpoint = f"{API_URL}api/v2/items/{id}/items_links/" 
#             header = { "Authorization": API_KEY, "Content-Type": "application/json" }
#             response = requests.get( url=endpoint, headers=header, verify=True ).json() # returns 403 forbidden if I don't have write permission (github.com/elabftw/elabftw/issue/5577)
#             if isinstance(response, list) and len(response) == 0:
#                 mylist.append( item.get('title') ) #{ 'title': item.get('title'), 'id': id} )

#     return mylist


# with open('config.json') as cfg:
#     config = json.load(cfg)

# API_KEY = config.get('API_KEY')
# API_URL = config.get('ELABFTW_BASE_URL')
#actualpos = client.get_positions(API_KEY)
#print(list_available_slots(actualpos))

with open('tests/machines.json') as f:
    machines = json.load(f)

machinesObj = []
for machine in machines:
    machineObj = Instrument(machine.get('title'), machine.get('id'), machine.get('metadata')) # machineObj is class 'position'
    machinesObj.append(machineObj)

# My list of slots is now created, let's put it to good use: checking if a slot is clear or not.
available = []
not_available = []
available_test = []
for machineObj in machinesObj:
    slots = machineObj.getslots() # list of objects with 'name', 'sector' and 'sample' keys
    for slot in slots:
        if slot.get('sample'):
            not_available.append(slot)
        else:
            available.append(slot)
    available_test.append(machineObj.getavailable())
print(available)
print(available_test)
# print(not_available)
