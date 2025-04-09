import os
import sys
import json
import requests
from amore.api import client

'''
This approach assumes that every item from category "SAMPLE POSITIONS"
on our eLabFTW is a different machine. This method keeps track of sample
position by assigning items to a metadata field in eLabFTW whose key is
the name/identifier of the slot. Example:

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

class Position:
    def __init__(self,
                 title,
                 id,
                 metadata):
        self.title = title
        self.id = id
        self.meta = json.loads(metadata) # was this the right syntax ???
        #self.data = [ item.strip() for item in self.title.replace("POS","",1).split("-") ]
    def getsectors(self):
        dic = self.meta.get("extra_fields") # all keys in extra_fields must be names of slots
        return [ key for key in dic ]
    def getslots(self):
        dic = self.meta.get("extra_fields") # all keys in extra_fields must be names of slots
        slotlist = []
        for key in dic: # for every sector in extra fields
            for slot in dic.get(key): # for every slot in sector
                slotname = f"{self.title}-{key}-{slot}"
                slotsample = dic.get(key).get(slot)
                response = {
                    "slot": slotname,
                    "sample": slotsample
                }
                slotlist.append(response) # object containing full location of the slot ("slot" key) and the sample associated ("sample" key)
        return slotlist
    """
    Note for self: a method can call another method like this:

        def mymethod(self):
            # shit happens
            return integer
        def addone(self):
            return self.method_1() + 1
    """
    def getmachine(self):
        return self.title # if we opt for the "every machine is an item" approach
        #return self.data[0] # if we opt for the "every slot of every machine is an item" approach
    def getsample(self, slot, sector="LOST"):
        sector_slots = self.meta.get(sector)
        locate_sample = sector_slots.get(slot) or ""
        if locate_sample #or locate_sample != "None":
            return locate_sample
        return None
    def isthisloss(self):
        if self.data[-1].lower() == "lost":
            # I  II
            # II  L
            return True
        return False
    def dump(self):
        s = {
            "title": self.title,
            "id": self.id,
            "avail": self.avail,
            "machine": self.getmachine(),
            "slot": self.getslot(),
            "sector": self.getsector(),
            "lost": self.isthisloss()
            }
        return s

def parse_slots(dictlist):
    # 0. If somehow in prod scientists will still use longdash as separator:
    dictlist = [ { 'title': item.get('title').replace("–","-"), 'id': item.get('id') } for item in dictlist ]
    # Now iterate through elements of dictlist:
    for item in dictlist:
        # 1. Split element title by "-", creating list.
        split_title = item.get('title').split("-")
        # 2. Strip every element in list to remove opening/trailing spaces.
        stripped = [ i.strip() for i in split_title ]
        # 3. Add every element in list into values of original dictionary with keys 'instrument', 'sector', 'slot'.
        if stripped[-1].lower() == "lost": # lost is treated as a sector and not a slot
            item["instrument"] = stripped[0]
            item["sector"] = "LOST"
        elif len(stripped) == 2: # instrument and slot only, for smaller instruments
            item["instrument"] = stripped[0]
            item["slot"] = stripped[-1]
        elif len(stripped) >= 3: # instrument, sector and slot, for larger instruments (only really supports up to lenght 3)
            item["instrument"] = stripped[0]
            item["sector"] = stripped[-2]
            item["slot"] = stripped[-1]
    return dictlist


def list_available_slots(dictlist):
    parsed_dictlist = parse_slots(dictlist)
    mylist = []
    for item in parsed_dictlist:
        if item.get('sector') == "LOST":
            mylist.append( item.get('title') )
        else:
            id = item.get('id')
            endpoint = f"{API_URL}api/v2/items/{id}/items_links/" 
            header = { "Authorization": API_KEY, "Content-Type": "application/json" }
            response = requests.get( url=endpoint, headers=header, verify=True ).json() # returns 403 forbidden if I don't have write permission (github.com/elabftw/elabftw/issue/5577)
            if isinstance(response, list) and len(response) == 0:
                mylist.append( item.get('title') ) #{ 'title': item.get('title'), 'id': id} )

    return mylist


with open('config.json') as cfg:
    config = json.load(cfg)

API_KEY = config.get('API_KEY')
API_URL = config.get('ELABFTW_BASE_URL')
#actualpos = client.get_positions(API_KEY)
#print(list_available_slots(actualpos))
