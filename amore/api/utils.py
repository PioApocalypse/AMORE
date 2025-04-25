import os
import requests
import json
from datetime import datetime
from amore.var import locations as ll
from flask import session
import random # TO REMOVE after feature is finished
#from random import randrange as rr # TO REMOVE after feature is finished
#from random import choice as rc # TO REMOVE after feature is finished

'''
===================================================
Utils for AMORE to read and elaborate internal ID's
===================================================
'''

def get_std_id(loc_code):
    API_URL = os.getenv('ELABFTW_BASE_URL')
    API_KEY = session.get('api_key')
    # API_KEY = os.getenv('API_KEY')
    every_id = []
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q={loc_code}-&limit=9999'
    
    response = requests.get(
    headers=header,
    url=search_query,
    verify= os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

    )

    for i in response.json():
        try:
            every_id.append(int(json.loads(i['metadata'])['extra_fields']['STD-ID']['value']))
        except:
            pass
    #last_id = 25000 + random.randrange(1,999,1) # placeholder to try higher ID's
    
    if every_id == []:
        last_id = 0
    else:
        last_id = max(every_id)
    # print(every_id) #for debugging to be removed
    # print(last_id)  #for debugging to be removed
    return last_id
    
def id_generator(city):
    location_code = ll.location_to_code(city)
    last_id = get_std_id(location_code)
    last_year = last_id // 1000 # first 2 digits
    last_unique = last_id % 1000 # last 3 digits
    if last_unique > 998:
        print("Number of samples created this year exceeds 1000.\nSomething clearly isn't working as intended.\nPlease contact your sysadmin.")
        return 1

    current_year = datetime.now().strftime("%y")
    if last_year < int(current_year):
        unique = 1
    else:
        unique = last_unique + 1
    std_id = int(current_year)*1000 + unique
    complete_id = f"{location_code}-{current_year}-{unique:03d}"
    return std_id, complete_id, last_id # last_id only for testing purposes

'''
===========================
Sanification, normalization
===========================
'''

def normalize_position_name(position_name):
    if position_name[0:3] == "POS":
        noPOS = position_name[3:].strip()
        while noPOS[0] in ["-", "/", "\\", "|", ":", "#", "*", "—"]:
            noPOS = noPOS[1:].strip()
        return noPOS
    else:
        return position_name

def normalize_to_int(value):
    '''Function to normalize a value which is usually a string with a number or an empty string to integer.'''
    if value == '':
        value = 0
    elif not isinstance(value, int):
        try:
            value = int(value)
        except:
            # returns 0 on error
            value = 0
    return value

'''
=========================
Handling attachment files
=========================
'''

def attachment_handler(uploads):
    attachments = []
    UPLOAD_FOLDER = ".uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True) # create temporary uploads folder
    for file in uploads:
        if file.filename == "": # if empty continue
            continue
        # get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        # check for 100 MB limit
        if file_size > 100 * 1024 * 1024:
            raise Exception(f"File '{file.filename}' exceeds the 100 MB size limit.", "error")
        # save in tmp folder
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # append to attachments list
        attachments.append(("file", (file.filename, open(file_path, "rb"))))
    return(attachments)

def tmp_remover(attachments):
    for _, (_, file) in attachments:
        file.close()
        os.remove(file.name)

'''
=============
Miscellaneous
=============
'''

def slots_shortlist():
    filename = "amore/var/slots.json"
    if os.path.isfile(filename):
        with open(filename) as f:
            shortlist = json.load(f)
        return shortlist
    else:
        raise FileNotFoundError(f"No {filename} file found.\nPlease run amore/scan_elab.py.")


if __name__=="__main__":
    print("Debug mode.")
    id_array = id_generator()
    std_id = id_array[0]
    complete_id = id_array[1]
    last_id = id_array[2]
    print(f"Last ID: {last_id}, STD-ID: {std_id}, Name: {complete_id}")