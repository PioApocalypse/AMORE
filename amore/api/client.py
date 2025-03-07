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
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file
"""
ED: about the key - would it be better to just implement a login page?
The software would save the api key of each user locally in cache and
discard it as soon as the user logs out...
"""

# =========================================================================================================================================
# == EXPERIMENT SECTION ===================================================================================================================
# =========================================================================================================================================

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
        verify=ssl_verification
    )

    response.raise_for_status()
    return response.json()

# =========================================================================================================================================
# == RESOURCES SECTION ====================================================================================================================
# =========================================================================================================================================

def get_new_sample():
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
        verify=ssl_verification
    )
    
    # returns 'id' from entry whose 'id' is max among all entries in response.json()
    # thank god someone on stackoverflow had my same problem...
    new_sample = max(response.json(), key=lambda ev: ev['id'])
    return new_sample


def patch_sample(new_elabid, new_userid, body, std_id, position, batch, subholder, proposal):
    # like before, different url
    API_URL = os.getenv('ELABFTW_BASE_URL')
    API_KEY = os.getenv('API_KEY')
    items_url = f"{full_elab_url}items/{new_elabid}/"

    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "custom_id": None,
        "body": body,
        "metadata": ('{ "extra_fields": {'
            ' "Owner": { "type": "users", "value": "'+str(new_userid)+'", "required": true },'
            ' "Position": { "type": "items", "value": "'+str(position)+'" },'
            ' "Proposal": { "type": "items", "value": "'+str(proposal)+'" },'
            ' "Substrate Batch": { "type": "items", "value": "'+str(batch)+'" },'
            ' "Substrate Holder": { "type": "text", "value": "'+str(subholder)+'" },'
            ' "STD-ID": { "type": "number", "value": "'+str(std_id)+'" }'
            ' } }'),
    }

    # try:
    response = requests.patch(
        url=items_url,
        headers=header,
        json=payload,
        verify=ssl_verification
    )
    # response.raise_for_status()
    # return 0
    # except:
    #     print('An error occurred during item patching.')
    #     return 1


def create_sample(title, tags, body, std_id, position, batch, subholder, proposal): 
    items_url = f"{full_elab_url}""items/"
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "template": 10, # 10 defines this item as 'sample' in our database
        "title": title,
        "tags": tags
    }
    
    # try:
        # request item creation with template, title, status and tags as instructed by user
    response = requests.post(
        url=items_url,
        headers=header,
        json=payload,
        verify=ssl_verification
    )
    # get new sample metadata as dictionary:
    new_sample = get_new_sample()
    # get [elabftw] id of newly created sample:
    new_elabid = new_sample['id']
    # get userid of newly created sample
    new_userid = new_sample['userid']

    # patch new sample to inject metadata not accepted by post request:
    patch_sample(
        new_elabid=new_elabid,
        new_userid=new_userid,
        body=body,
        std_id=std_id,
        position=position,
        batch=batch,
        subholder=subholder,
        proposal=proposal,
        )

    # get std-id [yyxxx] and std-name [Aa-yy-xxx] of newly created sample:
    new_stdname = new_sample['title'][:9]
    return new_elabid, new_stdname # for confirmation message to user
    # except:
    #     print('An error occurred during item creation.')
    #     return 1

def batch_pieces_decreaser(batch):
    batch_url = f"{full_elab_url}items/{batch}/"
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    # Step 1: get metadata from batch id
    batch_data = requests.get(
        headers=header,
        url=batch_url,
        verify=ssl_verification
    )

    # Step 2: parse metadata from batch id
    batch_meta = json.loads(batch_data.json()['metadata']) # dictionary containing metadata

    # Step 3: decrease available pieces
    pieces_before = batch_meta['extra_fields']['Available pieces']['value']
    pieces_after = int(pieces_before) -1

    # Step 4: replace avail.pieces value with decreased value in metadata dictionary
    batch_meta['extra_fields']['Available pieces']['value'] = pieces_after
    
    # Step 5: patch batch with new metadata
    payload_batch = {
        "metadata": json.dumps(batch_meta)
    }
    response = requests.patch(
        url=batch_url,
        headers=header,
        json=payload_batch,
        verify=ssl_verification
    )
    return response

# =========================================================================================================================================
# == DATA FOR FORM BUILDING SECTION =======================================================================================================
# =========================================================================================================================================

def get_positions():
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
    
    # from response parse only useful info - which is title for the enduser and id for the create_sample client function
    positions = [
        {'id': item.get('id'), 'title': item.get('title')[4:]} # WARNING! .get method avoids KeyError exceptions - but it's really bad if eLab allows missing title or id
        for item in response.json() # which is an array of json objects/dictionaries
    ]
    return positions # which is a list of dictionaries with 'id' and 'title'

def get_substrate_batches():
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q=&cat=9&limit=9999' # dove 9 = "SUBSTRATE BATCH"
    
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    
    # from response parse only useful info - which is title for the enduser and id for the create_sample client function
    batches = [
        {'id': item.get('id'), 'title': item.get('title')}
        for item in response.json()
        if int(json.loads(item['metadata'])['extra_fields']['Available pieces']['value'].replace('', '0')) > 0 # which is an array of json objects/dictionaries
    ]
    # !!! WARNING !!! .get method avoids KeyError exceptions - but it's really bad anyways if eLab allows missing title or id.
    # Also note that previous if statement is exceptionally weird: json.loads returns dictionary, then I get the 'value' of extra field 'Available pieces'.
    # Unfortunately, that value is still a fucking string and it can be empty; I replace empty string with 0 and turn str to int. THEN it checks if it's >0.
    return batches # which is a list of dictionaries with 'id' and 'title'

def get_proposals():
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q=&cat=15&limit=9999' # dove 15 = "PROPOSAL"
    
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    
    # from response parse only useful info - which is title for the enduser and id for the create_sample client function
    proposals = [
        {'id': item.get('id'), 'title': item.get('title')}
        for item in response.json() # which is an array of json objects/dictionaries
    ]
    # !!! WARNING !!! .get method avoids KeyError exceptions - but it's really bad anyways if eLab allows missing title or id
    return proposals # which is a list of dictionaries with 'id' and 'title'


# disaster prevention
if __name__ == "__main__":
    print('This file is not meant to be executed as main program.')
    #return 1