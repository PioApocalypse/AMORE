import requests
import os
import json
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from amore.api.client import sample_locator

# Global variables:

if os.path.isfile('config.json'):
    with open('config.json') as cfg:
        config = json.load(cfg)
    API_URL = config.get('ELABFTW_BASE_URL') #or os.environ('ELABFTW_BASE_URL') # software will eventually return error if no URL is provided
elif os.path.isfile('.env'):
    load_dotenv()
    API_URL = os.getenv('ELABFTW_BASE_URL')
else:
    raise FileNotFoundError(f"One of these files is required: config.json or .env.\nRead the official documentation for more.")

types_endpoint = f"{API_URL}api/v2/items_types/"

if not os.getenv('VERIFY_SSL'):
    if config.get('VERIFY_SSL'):
        ssl_verification = str(config.get('VERIFY_SSL')).lower() == 'true' # this way you can toggle SSL verification in .env file
    else:
        ssl_verification = True # in case VERIFY_SSL is not provided
else:
    ssl_verification = str(os.getenv('VERIFY_SSL')).lower() == 'true'

def check_apikey(KEY="", ssl_verification=True):
    # No sense proceeding if the user somehow submitted an empty key...
    if KEY == "":
        raise Exception('You submitted an empty key.')
    # Request section
    endpoint = f"{API_URL}api/v2/apikeys"
    header = {
        "Authorization": KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(
        url=endpoint,
        headers=header,
        verify=ssl_verification,
    )
    # Check zero: is the request not accepted by the server?
    if response.status_code // 100 == 5:
        raise Exception('There''s a problem on the server. Try asking the sysadmin.')
    # First check: is the API key invalid? If so server returns 4xx error and no further check is required.
    if response.status_code // 100 == 4:
        raise Exception('Invalid API key.')

    # Get last used API key - the one you made your request with - and see if it can write.
    apikeys = [
        { 'date': item.get('last_used_at'), 'rw': item.get('can_write') }
        for item in response.json() ]
    last_used = max(apikeys, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'))
    key_can_write = last_used['rw']
    # Last check: is the key read only?
    if key_can_write == 0:
        raise Exception(f"API key is read-only, not read/write.<br>Please use (eventually create) one with read/write permissions.")
    
    # If AND ONLY IF the key exists, is valid and is not read-only, return user's full name:
    endpoint = f"{API_URL}api/v2/users/me/"
    response = requests.get(
        url=endpoint,
        headers=header,
        verify=ssl_verification,
    )
    user = response.json()['fullname']
    return user

def scan_for_categories(API_KEY):
    '''Function to scan the endpoint and save in a dictionary with 'title' as key and 'id' as value.'''
    header = {"Authorization": API_KEY, "Content-Type": "application/json"}
    response = requests.get(
        url=types_endpoint,
        headers=header,
        verify=ssl_verification)
    categories = { item['title'].lower(): item['id'] for item in response.json() }
    return categories


if __name__=="__main__":
    x = 3 # number of possible attempts
    while x > 0: # loop to decrease attempts
        API_KEY = os.getenv('API_KEY') or config.get('API_KEY') or str(input("Enter a valid API key - it won't be stored: ")) # if not provided it's taken from environment variable OR from input
        print(API_KEY)
        try:
            check_apikey(API_KEY, ssl_verification) # if it checks out it's all good
            break
        except Exception as e:
            if "read-only" in str(e):
                break
            print(str(e))
            if x == 1:
                raise Exception("Too many attempts.")
            x -= 1

    categories = scan_for_categories(API_KEY)
    with open('amore/var/categories.json', 'w') as f:
        json.dump(categories, f)
        print("Categories file updated.")
    slots = sample_locator(API_KEY).shortlist()
    with open('amore/var/slots.json', 'w') as f:
        json.dump(slots, f, indent=1)
        print("Slots file updated.")
    API_KEY = ""
