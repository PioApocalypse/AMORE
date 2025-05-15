import json
import os

class Header:
    '''
    Short class for handling HTTP requests headers.
    To create an object of this class: header = Header(API_KEY, content)
    Where: 'API_KEY' is the value for Authorization;
           'content' is the value for Content-Type.

    Content-Type's default value is "application/json", anything else
    (text/html, multipart/form-data...) must be provided explicitly.
    If set to None the header will only contain the Authorization key.
    '''
    def __init__(self, API_KEY, content="application/json"):
        '''
        Init method. Allows self.Key and self.ContentType attributes.
        The attributes return the values of the respective input variables.
        '''
        self.Key = API_KEY
        self.ContentType = content
    def dump(self):
        '''
        Dumps an header dictionary with Authorization and Content-Type
        set as instructed; can be fed directly to an HTTP request.

        If 'content' is set to None the Content-Type is omitted.
        '''
        if self.ContentType == None:
            header = { "Authorization": self.Key }
            return header
        header = {"Authorization": self.Key,
                  "Content-Type": self.ContentType}
        return header

class Tracker:
    '''
    Class for handling "Sample Locator" eLabFTW experiments via AMORE.
    To create an object of this class: tracker = Tracker(dictionary)
    Where: dictionary = json.load[s](...).
    '''
    def __init__(self, dictionary):
        '''
        Init method. Allows self.title, self.id, self.meta,
        self.groups and self.positions.

        meta is the content of the metadata field (str to dict);
        groups and positions both get objects from self.meta:
        groups gets the extra_fields_groups dict with names and
        ID's of metadata groups (full names of instruments or
        chambers); positions gets the extra_fields dict with name,
        group_id and associated sample of every slot.
        '''
        self.title = dictionary.get("title")
        self.id = dictionary.get("id")
        self.links = dictionary.get("items_links")
        self.meta = json.loads(dictionary.get("metadata"))
        # Replicate original dictionary:
        self.all = dictionary
        # self.groups and self.positions are taken from self.meta
        # They are convenient for code readability but not necessary:
        self.groups = self.meta.get("elabftw").get("extra_fields_groups")
        self.positions = self.meta.get("extra_fields")
    def getinstruments(self):
        '''Gets list of every instrument's name.'''
        instruments = [ item.get("name") for item in self.groups ]
        return instruments
    def getsamples(self):
        '''
        Gets list of selected data about samples present in any
        instrument, regardless of their positions. Data returned is
        a dictionary with ID, Standard ID and name of the sample.
        '''
        samples = [ { "id": item.get("entityid"),
            "std-id": item.get("title")[:9],
            "name": item.get("title")[10:].replace("-","",1).strip() }
            for item in self.links ]
        return samples
    def getslots(self):
        '''
        Returns list of objects containing relevant data about every
        single slot, available or not.
        '''
        slotlist = []
        groups = self.groups
        for position in self.positions:  # for every slot in extra fields
            slotgroup = self.positions.get(position).get("group_id") # ID, not name of sector
            if slotgroup != ("" or None):
                slotinstrument = [ item.get("name")
                    for item in self.groups
                    if item.get("id") == slotgroup ][0] # actual name of sector
                slotsample = self.positions.get(position).get("value") # ID, not title of sample
                splitname = position.replace(" ","").split("-")
                slotinstcode = splitname[0]
                slotcode = splitname[-1]
                match len(splitname):
                    case 2:
                        slotsector = "Main"
                    case 3:
                        slotsector = splitname[1]
                    case _:
                        s = " - " # separator
                        slotsector = s.join(splitname[1:-1]) # join back everything that isn't instrument or slot
                available = (slotsample is None or slotsample == "")
                try:
                    samplestdid = [ item.get("std-id")
                    for item in self.getsamples()
                    if item.get("id") == int(slotsample) ][0] # actual name of sample
                except:
                    samplestdid = None
                try:
                    samplename = [ item.get("name")
                    for item in self.getsamples()
                    if item.get("id") == int(slotsample) ][0] # actual name of sample
                except:
                    samplename = None
                response = {
                    "name": position,
                    "shortname": position.replace(" ",""),
                    "slot": slotcode,
                    "sector": slotsector,
                    "inst_name": slotinstrument,
                    "inst_code": slotinstcode,
                    "sample_id": slotsample, # again: ID not title
                    "sample_stdid": samplestdid, # our standard-ID
                    "sample_name": samplename, # THIS is the title
                    "available": available # this is boolean not string
                }
                slotlist.append(response) # object containing full location of the slot ("name" key), instrument name ("inst" key) and the sample associated if any ("sample" key)
        return slotlist
    def shortlist(self):
        '''Trimmed version of "getslots()" with fewer keys.'''
        slotlist = self.getslots()
        shortlist = [ {
            "name": item.get("name"),
            "shortname": item.get("shortname"),
            "slot": item.get("slot"),
            "sector": item.get("sector"),
            "inst_name": item.get("inst_name"),
            "inst_code": item.get("inst_code") }
            for item in slotlist ]
        return shortlist
    def getavailable(self):
        '''Returns list of available slots.'''
        available = []
        for position in self.getslots():
            if position.get("available") == True:
                available.append(position)
        return available
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
        for position in self.getslots():
            if position.get("sector").lower() == "lost": # case insensitive, just to be safe
                lost.append(position)
        return lost # unordered list

if __name__=="__main__":
    try:
        filenames = [ i for i in os.listdir("tests/")
            if i.startswith("sample_locator_") and i.endswith(".json") ]
        if not filenames:
            raise FileNotFoundError(f"No sample_locator_*.json found in ./tests.")
        filename = sorted(filenames, key=lambda x: x, reverse=True)[0]
        with open(f"tests/{filename}", 'r') as f:
            dic = json.load(f)
            tracker = Tracker(dic)
        print(tracker.getslots()[0:3])
    except FileNotFoundError:
        print(f"No directory ./tests found.\n"
            f"Did you remember to run this script in AMORE's root folder?\n"
            f"Did you remember to export PYTHONPATH?")
    