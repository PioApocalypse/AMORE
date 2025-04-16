import os
import sys
import json
import requests
from amore.api import client

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
                 avail=False):
        self.title = title
        self.id = id
        self.avail = avail
        self.data = [ i.strip() for i in title.replace("POS", "").split("-") ]
    def getmachine(self):
        return self.data[0]
    def getslot(self):
        slot = self.data[-1]
        if slot.lower() == "lost":
            return "LOST"
        return slot
    def getsector(self):
        l = len(self.data)
        if l < 3:
            return None
        elif l == 3:
            return self.data[1]
        else:
            sectorname = ""
            for i in self.data[1:l-1]:
                sectorname += f" - {i}"
            return sectorname[3:]
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
actualpos = client.get_positions(API_KEY)
print(list_available_slots(actualpos))