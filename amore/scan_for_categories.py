import requests
import os
import json
from datetime import datetime
# Global variables:
with open('config.json') as cfg:
    config = json.load(cfg)

API_URL = config.get('ELABFTW_BASE_URL')
types_endpoint = f"{API_URL}api/v2/items_types/"
ssl_verification = str(config.get('VERIFY_SSL')).lower() == 'true' # this way you can toggle SSL verification in .env file

def check_apikey(KEY=""):
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

'''
Function to scan the endpoint and save in a dictionary with 'title' as key and 'id' as value:
'''
def scan_for_categories(API_KEY):
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
        API_KEY = config.get('API_KEY') # or str(input("Enter a valid API key - it won't be stored: ")) # if not provided it's taken from environment variable
        try:
            check_apikey(API_KEY) # if it checks out it's all good
            break
        except Exception as e:
            if "read-only" in str(e):
                break
            print(str(e))
            if x == 1:
                raise Exception("Too many attempts.")
            x -= 1

    categories = scan_for_categories(API_KEY)
    with open('amore/var/categories.json', 'w') as cat:
        json.dump(categories, cat)
        print("Categories file updated.")
    API_KEY = ""