import json

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
        instrument, regardless of its position. Data returned is
        a dictionary with ID, standard-ID and name of the sample.
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
                    if item.get("id") == slotsample ][0] # actual name of sample
                    samplename = [ item.get("name")
                    for item in self.getsamples()
                    if item.get("id") == slotsample ][0] # actual name of sample
                except:
                    samplestdid = None
                    samplename = None
                response = {
                    "name": position,
                    "slot": slotcode,
                    "sector": slotsector,
                    "inst_name": slotinstrument,
                    "inst_code": slotinstcode,
                    "sample_id": slotsample, # again: ID not title
                    "sample_stdid": samplestdid, # our standard-ID
                    "sample_name": samplename, # THIS is the title
                    "available": available
                }
                slotlist.append(response) # object containing full location of the slot ("name" key), instrument name ("inst" key) and the sample associated if any ("sample" key)
        return slotlist
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