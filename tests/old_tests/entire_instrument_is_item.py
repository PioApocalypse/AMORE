import os
import sys
import json
import requests
from amore.api import client

'''
This approach assumes that every item from category "SAMPLE POSITIONS"
on our eLabFTW represents a different instrument. This method keeps track
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
    '''Class created to handle different instruments within eLabFTW.'''
    def __init__(self,
                 title,
                 id,
                 metadata):
        '''
        Init method. Allows self.title, self.id, self.meta,
        self.extra, self.groups.

        meta is the content of the metadata field (dict);
        extra and groups both get objects from self.meta:
        extra gets the extra_fields dict, groups gets the
        extra_fields_groups dict.
        '''
        self.title = title
        self.id = id
        self.meta = metadata # testing
        #self.meta = json.loads(metadata) # in practice
        self.extra = self.meta.get("extra_fields") or [""] # all keys in extra_fields must be names of slots
        self.groups = self.meta.get("elabftw").get("extra_fields_groups") or [""] # list of dictionaries containing every sector's id and name
    def getsectors(self):
        '''
        Returns list of dictionaries with every sector's ID and name.
        '''
        sectors = [ { "id": item.get("id"), "name": item.get("name") } for item in self.groups ]
        return sectors # unordered list
    def getslots(self):
        '''
        Returns list of dictionaries with full location of
        the slot ("name"), name of its sector ("sector"),
        and the sample associated to it ("sample").
        '''
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
        return slotlist # unordered list
    def getinstrument(self):
        '''Equivalent to self.title.'''
        return self.title
    def isthisloss(self):
        '''
        Returns list of slots (see "getslots()") whose
        "sector" is equal to "LOST" (case insensitive).

        These slots all contain the IDs of samples lost
        within the chambers of the instruments, which can
        be listed with:
        
            [ item.get("sample")
            for item in Istrument.isthisloss() ]

        I  II
        II  L
        iykyk
        '''
        lost = []
        for slot in self.getslots():
            if slot.get("sector").lower() == "lost":
                lost.append(slot)
        return lost # unordered list
    def freelost_number(self): 
        '''
        Returns number (integer) of the smallest available
        slot in the instrument's LOST sector.

        E.g.: if LOST - 1 through LOST - 5 are assigned it
        returns 6 - even if slot LOST - 3 is unassigned.

        Takes as input "isthisloss()" method's output.
        '''
        lost = self.isthisloss()
        latest_lost = max(lost, key=lambda x: int(x.get("name").split("-")[-1]))
        latest_lost_number = int(latest_lost.get("name").split("-")[-1])
        return latest_lost_number +1
    def freelost(self):
        '''
        Returns object of empty slot of the LOST sector of
        the instrument, whose name is that of the smallest
        available LOST slot (see "freelost_number()").

        E.g.: if LOST - 1 through LOST - 5 are assigned it
        returns:
        
            { "name": "<inst> - LOST - 6",
            "sector": "LOST", "sample": "" }
            
        ...even if slot LOST - 3 is unassigned.
        '''
        freelost = {
            "name": f"{self.title} - LOST - {self.freelost_number()}",
            "sector": "LOST",
            "sample": ""
        }
        return freelost
    def getavailable(self):
        '''
        Returns list of slots (see "getslots()") whose
        "sample" value is empty (""); it always includes
        the smallest available LOST sector slot (see
        "freelost()").
        '''
        slotlist = self.getslots()
        available = [ self.freelost() ]
        for slot in slotlist:
            if slot.get("sample") == "":
                available.append(slot)
        return available # unordered list
    def dump(self):
        '''
        Returns list of dictionaries which is a full dump
        of every single existent slot of every single
        instrument available as a resource on eLabFTW.

        Every element of the list contains:
            - "instrument_id": Instrument.itemID
            - "instrument_title": Instrument.title
            - "sector_name": Sector.name
            - "slot_name": Slot.name
            - "sample_id": Sample.itemID (if present)

        Remember:   items have titles and IDs,
                    metadata have names.
        '''
        dump = []
        slot_list = self.getslots()
        for slot in slot_list:
            obj = {
                "instrument_id": self.id,
                "instrument_title": self.title,
                "sector_name": slot.get("sector"),
                "slot_name": slot.get("name"),
                "sample_id": slot.get("sample") # where do I turn this into a sample title?
            }
            dump.append(obj)
        return dump # unordered list

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

with open('tests/instruments.json') as f:
    instruments = json.load(f)

instruments_list = []
for instrument in instruments:
    obj = Instrument(instrument.get('title'), instrument.get('id'), instrument.get('metadata')) # instrumentObj is of class 'Instrument'
    instruments_list.append(obj)

# My list of slots is now created, let's put it to good use: checking if a slot is clear or not.
available = []
not_available = []
available_test = []
lost = []
freelost = []
for obj in instruments_list: # two iterations are necessary: one for every instrument taken from eLab...
    for item in obj.isthisloss(): # ...the other for the methods whose output is a list, like isthisloss()...
        lost.append(item)
    for item in obj.getavailable(): # ...or getavailable().
        available_test.append(item)
    freelost.append(obj.freelost_number()) # freelost_number() returns an integer therefore it doesn't require an iteration.
print(f"LOST: {lost}\n")
# print(available)
print(f"AVAILABLE: {available_test}\n")
# print(not_available)
print(f"SMALLEST FREE LOST: {freelost}\n")