import os
import requests
from datetime import datetime
from dotenv import load_dotenv

def get_std_id():
    # query to get all std_id
    # compare std_id, pick biggest
    # make sure std_id is number not string
    # make sure first 2 digits are less or equal to current year
    return last_id # placeholder

def get_location():
    # from user input get location
    # match known locations or return exception
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
    return location_code # placeholder

def standard_id():
    last_id = get_std_id()
    last_year = last_id // 1000 # first 2 digits
    last_unique = last_id % 1000 # last 3 digits

    current_year = datetime.now().strftime("%y")
    if last_year < int(current_year):
        unique = 1
    else:
        unique = last_unique + 1

    std_id = int(current_year)*1000 + unique
    location_code = get_location()
    complete_id = f"{location_code}-{current_year}-{unique:03d}"
    return std_id, complete_id