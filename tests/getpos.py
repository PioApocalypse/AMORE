import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
load_dotenv()
API_URL = os.getenv('ELABFTW_BASE_URL')
API_KEY = os.getenv('API_KEY')
full_elab_url = f"{API_URL}api/v2/"
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

def get_positions(): # get every item in category 17 (SAMPLE POSITION)
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    search_query = f'{API_URL}api/v2/items?q=&cat=17&limit=9999' # dove 17 = "SAMPLE POSITION"
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    return response.json()

def get_linked_items(item_id): # get linked item for specified resource 
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    items_links = f'{API_URL}api/v2/items/{item_id}/items_links'
    response = requests.get(
        headers=header,
        url=items_links,
        verify=ssl_verification
    )
    print(item_id)
    print(response.json())
    linked_items = [
        {'id': item.get('entityid'), 'full_id': item.get('title')[:9], 'title': item.get('title')[12:] }
        for item in response.json()
    ]
    return linked_items # list of dicts containing only data on linked resource, not parent resource

'''
HOW DO I DEFINE AN AVAILABLE POSITION? It must be capable of holding at least another new resource. That means one or both (OR) of two things:
1. Resource has "LOST", "OOC", etc. in its name (hard part)
2. Resource has no associated resources
In this order because it allows for decreased number of requests, therefore it's less heavy on the server
'''

def get_available_positions():
    available_positions = []
    all_positions = get_positions()

    for item in all_positions:
        name = item.get('title').lower() # lower to make it caps insensitive
        print(name)
        if "lost" in name or "ooc" in name: # 1st condition
            available_positions.append(item)
        else:
            position_id = item.get('id')
            linked_items = get_linked_items(position_id)
            if len(linked_items) == 0:
                available_positions.append(item)
            else:
                pass


    # all_positions = [
    #     { 'id': item.get('id'), 'title': item.get('title') }
    #     for item in get_positions()
    # ]
    return available_positions

if __name__=="__main__":
    result = get_available_positions()
    print(result)