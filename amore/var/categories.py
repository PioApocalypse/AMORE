"""
The problem with templates is that they're extremely subjective:
suppose I decide to reset my eLabFTW database before going in prod,
after creating my new categories I will have a bunch of new category
ID's that I will have to type down somewhere. To solve this problem
I thought of two solutions:
    1. Make another client function whose sole purpose is - upon installing
       AMORE - to scan the /items_types endpoint and store a list of objects
       with 'name' and 'category_id' as keys.
    2. Hardcoding (default).
"""
import requests
import os
import json

# Global variables:
API_URL = os.getenv('ELABFTW_BASE_URL')
types_endpoint = f"{API_URL}api/v2/items_types/"
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

'''
Function to scan the endpoint and store the result:
'''
"""
def scan_for_categories(API_KEY):
    header = {"Authorization": API_KEY, "Content-Type": "application/json"}
    response = requests.get(
        url=types_endpoint,
        headers=header,
        verify=ssl_verification)
    categories = [
        {'id': item.get('id'), 'title': item.get('title')}
        for item in response.json() ] # list of categories
    TO BE CONTINUED
"""

# Hardcoded (titles in lower):
categories = {
    "compound": 2,
    "substrates batch": 9,
    "sample": 10,
    "pld target": 11,
    "process instrument": 12,
    "measurement instrument": 13,
    "proposal": 15,
    "sample position": 17
}

def cat(title):
    title = title.lower()
    return categories.get(title)