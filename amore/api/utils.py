import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from random import randrange as rr # TO REMOVE after feature is finished

"""
Utils for AMORE to read and elaborate internal ID's
"""

def get_std_id():
    # query to get all std_id
    # compare std_id, pick biggest
    # make sure std_id is number not string
    # make sure first 2 digits are less or equal to current year
    last_id = 25000 + rr(1,999,1) # placeholder
    return last_id
    
def get_location():
    # from user input get location
    # match known locations or return exception
    location_name = "Napoli" # placeholder
    match location_name:
        case "Napoli":
            location_code = "Na"
        case "Salerno":
            location_code = "Sa"
        case "Genova":
            location_code = "Ge"
        case "Roma":
            location_code = "Rm"
        case "L'Aquila":
            location_code = "Aq"
        case _:
            print("Your location doesn't match any place in the code and will be treated as an exception.")
            location_code = "Xx"
    return location_code

def id_generator():
    last_id = get_std_id()
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
    location_code = get_location()
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
