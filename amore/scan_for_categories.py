import requests
import os
import json
from amore.api.auth import check_apikey

# Global variables:
API_URL = os.getenv('ELABFTW_BASE_URL')
types_endpoint = f"{API_URL}api/v2/items_types/"
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

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
        API_KEY = str(input("Enter a valid API key - it won't be stored: ")) or os.getenv('TMP_API_KEY') # if not provided it's taken from environment variable
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