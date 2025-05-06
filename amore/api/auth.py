import os
import requests
from datetime import datetime

API_URL = os.getenv('ELABFTW_BASE_URL')
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification if ENV var VERIFY_SSL is True, TRUE, true...

'''
Use this file for AND ONLY FOR storing functions for authentication.
'''

"""
How do I check if an API key 1. is valid and 2. has read-write permissions?
eLabFTW has an endpoint for calling pre-existent API keys associated to one's account
The keys are always stored encrypted, no way to recover them if lost - thank god
Encryption method is bcrypt, SALT is unknown and on server so no way to check if hash corresponds
The only way is making a GET request to the apikey endpoint and look for the one that's been just used
/tests/api_get.py
"""

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
    try:
        response = requests.get(
            url=endpoint,
            headers=header,
            verify=ssl_verification,
        )
    except requests.exceptions.ConnectionError as ce:
        if "NewConnectionError" in str(ce):
            raise ConnectionError("Your eLabFTW server might currently be down.")
        else:
            raise Exception("General connection error.")

    # Check zero: is the request not accepted by the server?
    if response.status_code // 100 == 5:
        raise Exception("There's a problem on the server. Try asking the sysadmin.")
    # First check: is the API key invalid? If so server returns 4xx error and no further check is required.
    if response.status_code // 100 == 4:
        raise Exception("Invalid API key.")

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
    ).json()
    user = {
        "fullname": response.get("fullname"),
        "userid": response.get("userid")
    }
    return user