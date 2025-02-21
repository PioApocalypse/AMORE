import os
import requests
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
VERIFY = os.getenv('VERIFY_SSL')
full_elab_url = f"{API_URL}api/v2/"
"""
ED: about the key - would it be better to just implement a login page?
The software would save the api key of each user locally in cache and
discard it as soon as the user logs out...
"""

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
        verify=VERIFY
    )

    response.raise_for_status()
    return response.json()

# =====================

def create_sample(title, body, status, tags, std_id, substrate_batch, position):
    items_url = f"{full_elab_url}""items/"
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "template": 10, # 10 defines this item as 'sample' in our database
        "title": title,
        "body": body,
        "status": status,
        "tags": tags,
        "metadata": '{ "extra_fields": { "STD-ID": { "type": "number", "value": "'+str(std_id)+'" } } }', # todo: add other fields
    }
    
    try:
        response = requests.post(
            url=items_url,
            headers=header,
            json=payload,
            verify=False
        )
        # figure out what's wrong with the following code which returns error:
        #response.raise_for_status()
        return 0 # response.json()
    except:
        print('An error occurred.')
        return 1


# =====================
'''
def populate_sample(title, date, status, tags, body, substrate_batch, position):
    # like before, different url
    items_url = f"{full_elab_url}""items/0/"
    
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "date": date,
        "status": status,
        "tags": tags, # "tag 1|tag 2|tag 3"
        "body": body,
        "category": 10, # 10 defines this item as 'sample' in our database
        "metadata": {
            "substrate_batch": substrate_batch,
            "position": position
        }
    }

    response = requests.post(
        url=items_url,
        headers=header,
        json=payload,
        verify=False
    )

    response.raise_for_status()
    return response.json()
'''

# disaster prevention
if __name__ == "__main__":
    print('This file is not meant to be executed as main program.')