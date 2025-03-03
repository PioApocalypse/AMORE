import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

"""
Variables will be only imported from env for testing purposes.
Later on, I will also implement url and key selection. Probably. Possibly.
"""

# ED: import .env variables api url and api key
# PLEASE DO NOT push api keys to public repos
load_dotenv()
API_URL = os.getenv('ELABFTW_BASE_URL')
API_KEY = os.getenv('API_KEY')
full_elab_url = f"{API_URL}api/v2/"
"""
ED: about the key - would it be better to just implement a login page?
The software would save the api key of each user locally in cache and
discard it as soon as the user logs out...
"""

# ========================
# == EXPERIMENT SECTION ==
# ========================

def create_experiment(title, date, status, tags, b_goal, b_procedure, b_results):
    # a post request needs url, header and payload
    experiments_url = f"{full_elab_url}""experiments/"
    
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "date": date,
        "status": status,
        "tags": tags, # "tag 1|tag 2|tag 3"
        "body": f"<h1>Goal:</h1>\n<p>{b_goal}</p>\n<h1>Procedure:</h1>\n<p>{b_procedure}</p>\n<h1>Results:</h1>\n<p>{b_results}</p>\n",
        "category_title": "Deposition", # hardcoded deposition, might reprogram it later
    }

    response = requests.post(
        url=experiments_url,
        headers=header,
        json=payload,
        verify=os.getenv('VERIFY_SSL')
    )

    response.raise_for_status()
    return response.json()

# =======================
# == RESOURCES SECTION ==
# =======================

def get_new_sample():
    API_URL = os.getenv('ELABFTW_BASE_URL')
    API_KEY = os.getenv('API_KEY')
    every_id = []
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?limit=9999'
    
    response = requests.get(
    headers=header,
    url=search_query,
    verify=True
    )
    
    # returns 'id' from entry whose 'id' is max among all entries in response.json()
    # thank god someone on stackoverflow had my same problem...
    new_sample = max(response.json(), key=lambda ev: ev['id'])
    return new_sample

'''
def patch_sample(title, date, status, tags, body, substrate_batch, position):
    # like before, different url
    items_url = f"{full_elab_url}""items/0/"
    
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "body": body,
        "metadata": '{ "extra_fields": { "STD-ID": { "type": "number", "value": "'+str(std_id)+'" } } }', # todo: add other fields
        "custom_id": None
    }

    try:
        response = requests.post(
        url=items_url,
        headers=header,
        json=payload,
        verify=True
        )
        response.raise_for_status()
        return 0
    except:
        print('An error occurred during item patching.')
        return 1
'''

def create_sample(title, status, tags): #, substrate_batch, position):
    items_url = f"{full_elab_url}""items/"
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "template": 10, # 10 defines this item as 'sample' in our database
        "title": title,
        "status": status,
        "tags": tags
    }
    
    try:
        # request item creation with template, title, status and tags as instructed by user
        response = requests.post(
            url=items_url,
            headers=header,
            json=payload,
            verify=True
        )
        # get new sample metadata as dictionary:
        new_sample = get_new_sample()
        # get [elabftw] id of newly created sample:
        new_elabid = new_sample['id']

        # patch_sample(new_elabid)

        # get std-id [yyxxx] and std-name [Aa-yy-xxx] of newly created sample:
        new_stdid = json.loads(new_sample["metadata"])["extra_fields"]["STD-ID"]["value"]
        new_stdname = new_sample["title"][:9]
        print(f"{new_elabid},{new_stdid},{new_stdname}") # DEBUG
        
        return new_elabid, new_stdid, new_stdname
    except:
        print('An error occurred during item creation.')
        return 1



# disaster prevention
if __name__ == "__main__":
    print('This file is not meant to be executed as main program.')
    #return 1