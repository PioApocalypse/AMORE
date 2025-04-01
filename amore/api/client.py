import os
import requests
import json
from datetime import datetime
# from amore.var.categories import categories as cat
from .utils import normalize_to_int as to_int
from .utils import normalize_position_name as norm_pos_name
from flask import session, request

# Import ENV variables api url and boolean ssl verification
# PLEASE DO NOT push api keys to public repos
API_URL = os.getenv('ELABFTW_BASE_URL')
full_elab_url = f"{API_URL}api/v2/" # API endpoint root for eLabFTW
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

if os.path.isfile('amore/var/categories.json'):
    with open('amore/var/categories.json', 'r') as catfile:
        cat = json.load(catfile)
else:
    print(f'No "amore/var/categories.json" file found.\nPlease run amore/scan_for_categories.py.')

'''
=========================================================================================================================================
== EXPERIMENT SECTION ===================================================================================================================
=========================================================================================================================================
'''
'''
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
'''
'''
=========================================================================================================================================
== RESOURCES SECTION ====================================================================================================================
=========================================================================================================================================
'''

def get_new_sample(API_KEY):
    every_id = []
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{full_elab_url}items?limit=9999'
    
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    
    # returns 'id' from entry whose 'id' is max among all entries in response.json()
    # thank god someone on stackoverflow had my same problem...
    new_sample = max(response.json(), key=lambda ev: ev['id'])
    return new_sample


def patch_sample(API_KEY, new_elabid, new_userid, body, std_id, position, batch, subholder, proposal):
    # like before, different url
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
    return 0


def upload_attachments(API_KEY, new_elabid, attachments):
    uploads_url = f"{full_elab_url}items/{new_elabid}/uploads"
    for field_name, (filename, file) in attachments:
        header = {"Authorization": API_KEY}
        files = {field_name: (filename, file)}
        try:
            response = requests.post(
                url=uploads_url,
                headers=header,
                files=files,
                verify=ssl_verification
            )
        except Exception as e:
            raise Exception(f"Exception during file upload: {str(e)}")
    return 0


def create_sample(API_KEY, title, tags, body, std_id, position, batch, subholder, proposal, attachments=None): 
    items_url = f"{full_elab_url}""items/"
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "template": cat.get("sample"), # 10 defines this item as 'sample' in our database
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
    new_sample = get_new_sample(API_KEY)
    # get [elabftw] id of newly created sample:
    new_elabid = new_sample['id']
    # get userid of newly created sample
    new_userid = new_sample['userid']
    # patch new sample to inject metadata not accepted by post request:
    patch_sample(
        API_KEY=API_KEY,
        new_elabid=new_elabid,
        new_userid=new_userid,
        body=body,
        std_id=std_id,
        position=position,
        batch=batch,
        subholder=subholder,
        proposal=proposal,
        )
    # upload attachments
    if attachments:
        upload_attachments(API_KEY=API_KEY, new_elabid=new_elabid, attachments=attachments)
    # get std-id [yyxxx] and std-name [Aa-yy-xxx] of newly created sample:
    # new_stdname = new_sample['title'][:9]
    return 0 # for confirmation message to user

def batch_pieces_decreaser(API_KEY, batch):
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
    available = batch_meta['extra_fields']['Available pieces']['value']
    remaining = int(available) -1

    # Step 4: replace avail.pieces value with decreased value in metadata dictionary
    batch_meta['extra_fields']['Available pieces']['value'] = remaining
    
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
    # Bonus: return remaining pieces to warn user if number is too low or zero
    return remaining

'''
=========================================================================================================================================
== ADDING/MOVING TO POSITIONS ===========================================================================================================
=========================================================================================================================================
'''

def add_to_position(API_KEY, sample_id, position_id): # POST to empty position
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    position_url = f'{API_URL}api/v2/items/{position_id}/items_links/{sample_id}'
    add = requests.post(
        headers=header,
        url=position_url,
        verify=ssl_verification
    )
    return 0

def move_to_position(API_KEY, sample_id, old_position_id, new_position_id): # DELETE from old position then POST to empty position
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    old_position_url = f'{API_URL}api/v2/items/{old_position_id}/items_links/{sample_id}'
    new_position_url = f'{API_URL}api/v2/items/{new_position_id}/items_links/{sample_id}'
    delete = requests.delete(
        headers=header,
        url=old_position_url,
        verify=ssl_verification  
    )
    add = requests.post(
        headers=header,
        url=new_position_url,
        verify=ssl_verification
    )
    return 0

'''
=========================================================================================================================================
== DATA FOR FORM BUILDING SECTION =======================================================================================================
=========================================================================================================================================
'''

def get_positions(API_KEY):
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q=&cat={cat.get("sample position")}&limit=9999' # "SAMPLE POSITION" should be id = 17
    
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    
    # from response parse only useful info - which is title for the enduser and id for the create_sample client function
    unsorted_positions = [
        {'id': item.get('id'), 'title': norm_pos_name(item.get('title'))} # WARNING! .get method avoids KeyError exceptions - but it's really bad if eLab allows missing title or id
        for item in response.json() # which is an array of json objects/dictionaries
    ]
    positions = sorted(unsorted_positions, key=lambda item: (item['title'], item['id']) ) # sort by title first, id second - although no two items should have the same name for any reason
    return positions # which is a list of dictionaries with 'id' and 'title'

def get_substrate_batches(API_KEY):
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q=&cat={cat.get("substrates batch")}&limit=9999' # "SUBSTRATES BATCH" should be id = 9
    
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    
    # from response parse only useful info - which is title for the enduser and id for the create_sample client function
    batches = [
        {'id': item.get('id'), 'title': item.get('title')}
        for item in response.json()
        if to_int( json.loads(item['metadata'])['extra_fields']['Available pieces']['value'] ) > 0 # which is an array of json objects/dictionaries
    ]
    # !!! WARNING !!! .get method avoids KeyError exceptions - but it's really bad anyways if eLab allows missing title or id.
    # Also note that previous if statement is exceptionally weird: json.loads returns dictionary, then I get the 'value' of extra field 'Available pieces'.
    # Unfortunately, that value is still a fucking string and it can be empty; I replace empty string with 0 and turn str to int. THEN it checks if it's >0.
    return batches # which is a list of dictionaries with 'id' and 'title'

def get_proposals(API_KEY):
    header = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    search_query = f'{API_URL}api/v2/items?q=&cat={cat.get("proposal")}&limit=9999' # "PROPOSAL" should be id = 15
    
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