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

def parse_slots(dictlist):
    # 0. If somehow in prod scientists will still use longdash as separator:
    dictlist = [ { 'title': item.get('title').replace("–","-"), 'id': item.get('id') } for item in dictlist ]
    # Now iterate through elements of dictlist:
    for item in dictlist:
        # 1. Split element title by "-", creating list.
        split_title = item.get('title').split("-")
        # 2. Strip every element in list to remove opening/trailing spaces.
        stripped = [ i.strip() for i in split_title ]
        # 3. Add every element in list into values of original dictionary with keys 'instrument', 'area', 'slot'.
        if stripped[-1].lower() == "lost": # lost is treated as an area and not a slot
            item["instrument"] = stripped[0]
            item["area"] = "LOST"
        elif len(stripped) == 2: # instrument and slot only, for smaller instruments
            item["instrument"] = stripped[0]
            item["slot"] = stripped[-1]
        elif len(stripped) >= 3: # instrument, area and slot, for larger instruments (only really supports up to lenght 3)
            item["instrument"] = stripped[0]
            item["area"] = stripped[-2]
            item["slot"] = stripped[-1]
    return dictlist


def list_available_slots(dictlist):
    parsed_dictlist = parse_slots(dictlist)
    mylist = []
    for item in parsed_dictlist:
        id = item.get('id')
        print(id)
        endpoint = f"{API_URL}api/v2/items/{id}/items_links/0/"
        header = { "Authorization": API_KEY, "Content-Type": "application/json" }
        response = requests.get( url=endpoint, headers=header, verify=True )
        mylist.append( response.json() )

    return mylist


with open('config.json') as cfg:
    config = json.load(cfg)

API_KEY = config.get('API_KEY')
API_URL = config.get('ELABFTW_BASE_URL')
actualpos = client.get_positions(API_KEY)
print(list_available_slots(actualpos))