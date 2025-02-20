import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from amore.var import locations as ll
from random import randrange as rr # TO REMOVE after feature is finished

"""
Utils for AMORE to read and elaborate internal ID's
"""

def get_location():
    # city from user input
    city = random.choice(['Salerno','Roma','Napoli']) # placeholder to try diff locations
    #city = "Salerno" # placeholder to try multiple ID's
    location_code = ll.location_to_code(city)
    return location_code

def get_std_id(loc_code):
    # query to get all std_id FROM LOCATION
    # compare std_id, pick biggest
    # make sure std_id is number not string
    # make sure first 2 digits are less or equal to current year
    last_id = 25000 + rr(1,999,1) # placeholder to try higher ID's
    return last_id
    
def id_generator():
    location_code = get_location()
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

if __name__=="__main__":
    print("Debug mode.")
    id_array = id_generator()
    std_id = id_array[0]
    complete_id = id_array[1]
    last_id = id_array[2]
    print(f"Last ID: {last_id}, STD-ID: {std_id}, Name: {complete_id}")
# TO REMOVE when this file is ready
else: 
    print("Feature not ready yet.")
