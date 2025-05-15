import os
import requests
import json
from datetime import datetime
# from amore.var.categories import categories as cat
from .utils import normalize_to_int as to_int
from ..classes import Tracker, Header

# Import ENV variables api url and boolean ssl verification
# PLEASE DO NOT push api keys to public repos
API_URL = os.getenv('ELABFTW_BASE_URL')
full_elab_url = f"{API_URL}api/v2/" # API endpoint root for eLabFTW
experiments_url = f"{full_elab_url}experiments" # API endpoint /experiments
items_url = f"{full_elab_url}items" # API endpoint /items
ssl_verification = os.getenv('VERIFY_SSL').lower() == 'true' # this way you can toggle SSL verification in .env file

filename = "amore/var/categories.json"
if os.path.isfile(filename):
    with open(filename, 'r') as catfile:
        cat = json.load(catfile)
else:
    raise FileNotFoundError(f"No {filename} file found.\nPlease run amore/scan_elab.py.")

'''
=========================================================================================================================================
== EXPERIMENT SECTION / SAMPLE LOCATION =================================================================================================
=========================================================================================================================================
'''
'''
def create_experiment(title, date, status, tags, b_goal, b_procedure, b_results):
    header = Header(API_KEY).dump()
    payload = {
        "title": title,
        "date": date,
        "status": status,
        "tags": tags, # list: [tag1, tag2, tag3]
        "body": f"<h1>Goal:</h1>\n<p>{b_goal}</p>\n<h1>Procedure:</h1>\n<p>{b_procedure}</p>\n<h1>Results:</h1>\n<p>{b_results}</p>\n",
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

def sample_locator(API_KEY):
    '''
    Function which looks up "sample locator" among eLabFTW's Experiments,
    selects the first one with matching title (caps-insensitive) and returns
    a Tracker-class object with data taken from said Experiment.
    See help(Tracker) or file "amore/classes.py" for more info.

    Raises Exception if no Experiment matching the exact name "Sample Locator"
    is found on eLabFTW.
    '''
    search_query = f"{experiments_url}?q=%22sample+locator%22"
    header = Header(API_KEY).dump()
    response = requests.get(
        headers=header,
        url=search_query,
        verify=ssl_verification
    )
    if len(response.json()) != 0:
        for item in response.json():
            if item.get("title").lower() == "sample locator":
                locator_id = item.get("id")
                locator = requests.get(
                    headers=header,
                    url=f"{experiments_url}/{locator_id}",
                    verify=ssl_verification
                ).json()
                tracker = Tracker(locator)
                return tracker
    raise Exception(f"No experiment \"Sample Locator\" found in eLabFTW's database.")

def move_sample(API_KEY, sample_id, new_position_name):
    '''
    Patches a sample's position with the specified new one.
    The sample's resource-ID and the new position name is given;
    the field patched is "metadata/extra_fields/Position".

    The sample's STD-ID is returned - taken from the first 9 characters
    of the sample's title.
    '''
    header = Header(API_KEY).dump()
    sample = requests.get(
        headers=header,
        url=f"{items_url}/{sample_id}",
        verify=ssl_verification
    )
    if sample.status_code == 404:
        raise ValueError(f"No sample exists with resource ID of {sample_id}.")
    sample = sample.json()
    metadata = json.loads(sample.get("metadata"))
    metadata["extra_fields"]["Position"]["value"] = new_position_name
    patch = json.dumps(metadata)
    response = requests.patch(
        headers=header,
        url=f"{items_url}/{sample_id}",
        json={ "metadata": patch },
        verify=ssl_verification
    )
    std_id = response.json().get("title")[:9]
    return std_id

def add_to_position(API_KEY, sample_id, position_name, userid=""): # POST to empty position
    '''
    Patches the "Sample Locator" Experiment with the position of a newly created sample.

    Obsolescent, supersided by "move_to_position" and likely to be removed later.
    '''
    header = Header(API_KEY).dump()
    tracker = sample_locator(API_KEY)
    metadata = tracker.meta
    metadata["extra_fields"]["User"]["value"] = userid
    metadata["extra_fields"][position_name]["value"] = sample_id
    patch = {
        "metadata": json.dumps(metadata)
    }

    tracker_url = f"{experiments_url}/{tracker.id}"
    patching_meta = requests.patch(
        headers=header,
        url=tracker_url,
        json=patch,
        verify=ssl_verification
    )
    link_url = f"{tracker_url}/items_links/{sample_id}"
    linking_item = requests.post(
        headers=header,
        url=link_url,
        verify=ssl_verification
    )
    return 0

def patch_tracker(API_KEY, sample_id, old_position_name, new_position_name, userid=""):
    '''
    Patches the "Sample Locator" Experiment moving a sample from an old position to a new one.
    It handles the following exceptions:
        - Old position name is null (new sample is added): only the new position is changed,
          a POST request is sent to the /items_links endpoint to LINK sample and locator;
        - New position name is null (a sample is removed from the chambers): the old position
          is cleared, then a DELETE request is sent to the /items_links endpoint to severe the
          link between sample and locator;
        - Both old and new position names are null (neutral condition): Exception is raised.
    
    If a new sample is added a POST request is made to link the "Sample Locator" with the
    sample's eLabFTW entry.
    If a sample is removed a DELETE request is made to delete the link between the "Sample
    Locator" and the sample's eLabFTW entry.
    '''
    if (old_position_name == new_position_name
        or (not old_position_name and not new_position_name)): # neutral condition, just to be safe (both null or both equal)
        raise Exception("New and old positions correspond.")
    header = Header(API_KEY).dump()
    tracker = sample_locator(API_KEY)
    tracker_url = f"{experiments_url}/{tracker.id}"
    metadata = tracker.meta
    metadata["extra_fields"]["User"]["value"] = userid
    if (old_position_name == "") or (old_position_name is None):
        metadata["extra_fields"][new_position_name]["value"] = sample_id
        method = "post" # if old position doesn't exist, item is not linked yet so do it
    elif (new_position_name == "") or (new_position_name is None):
        metadata["extra_fields"][old_position_name]["value"] = None
        method = "delete" # if new position doesn't exist, unlink item
    else:
        metadata["extra_fields"][old_position_name]["value"] = None
        metadata["extra_fields"][new_position_name]["value"] = sample_id
    patch = {
        "metadata": json.dumps(metadata)
    }
    patching_meta = requests.patch(
        headers=header,
        url=tracker_url,
        json=patch,
        verify=ssl_verification
    )
    try:
        method # if method variable is assigned it means we need to create or delete the link between the sample and the Locator
        link_url = f"{tracker_url}/items_links/{sample_id}"
        linking_item = requests.request(
            method=method,
            headers=header,
            url=link_url,
            verify=ssl_verification
        )
    except:
        pass
    return

def move_to_position(API_KEY, sample_id, old_position_name, new_position_name, userid=""):
    '''
    Moves a sample from an old to a new position by:
        1. Patching the sample Item's metadata adding the new position's name;
        2. Patching the "Sample Locator" Experiment by emptying the old position and adding the
           resource ID of the sample to the new position;
        3. Deleting or creating the link between the sample and the locator - if the sample is
           being removed or added for the first time.

    It handles the following exceptions (see help(patch_tracker) for more info):
        - Old position name is null (new sample is added);
        - New position name is null (a sample is removed from the chambers);
        - Both old and new position names are null (neutral condition, raises error).
    '''
    std_id = move_sample(API_KEY, sample_id, new_position_name) # try to fetch the sample first
    patch_tracker(API_KEY, sample_id, old_position_name, new_position_name, userid) # patch the sample locator experiment
    return std_id


'''
=========================================================================================================================================
== RESOURCES SECTION ====================================================================================================================
=========================================================================================================================================
'''

def get_new_sample(API_KEY):
    '''
    Returns the sample with the highest resource-ID.
    '''
    every_id = []
    header = Header(API_KEY).dump()
    search_query = f'{items_url}?limit=9999'
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
    '''
    Patches the [newly created] sample adding important metadata
    which cannot be added on eLabFTW Items directly on creation
    in eLabFTW 5.1.15 and before.
    '''
    # like before, different url
    itemurl = f"{items_url}/{new_elabid}/"
    header = Header(API_KEY).dump()
    metadata = { "extra_fields": {
            "Owner": { "type": "users", "required": True },
            "Position": { "type": "items" },
            "Proposal": { "type": "items" },
            "Substrate Batch": { "type": "items" },
            "Substrate Holder": { "type": "text" },
            "STD-ID": { "type": "number" }
            } }
    metadata["extra_fields"]["Owner"]["value"] = new_userid
    metadata["extra_fields"]["Position"]["value"] = position
    metadata["extra_fields"]["Proposal"]["value"] = proposal
    metadata["extra_fields"]["Substrate Batch"]["value"] = batch
    metadata["extra_fields"]["Substrate Holder"]["value"] = subholder
    metadata["extra_fields"]["STD-ID"]["value"] = std_id
    payload = {
        "custom_id": None,
        "body": body,
        "metadata": json.dumps(metadata)
    }
    response = requests.patch(
        url=itemurl,
        headers=header,
        json=payload,
        verify=ssl_verification
    )
    return 0


def upload_attachments(API_KEY, new_elabid, attachments):
    '''
    Uploads attachments to the resource-specific "uploads" API endpoint.
    '''
    uploads_url = f"{items_url}/{new_elabid}/uploads"
    for field_name, (filename, file) in attachments:
        header = Header(API_KEY, None).dump()
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
    '''
    Creates a new Item of the "Sample" category on eLabFTW, providing title, tags, body and
    all metadata required.

    Up until eLabFTW 5.1.15 Item creation didn't allow most of these informations to be pushed
    directly with a single POST request, which is why this function calls "get_new_sample" and
    "patch_sample" to recover the resource-ID of the new sample and patch it with the extra data.
    '''
    header = Header(API_KEY).dump()
    payload = {
        "template": cat.get("sample"), # 10 defines this item as 'sample' in our database
        "title": title,
        "tags": tags
    }
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
    add_to_position(API_KEY=API_KEY, sample_id=new_elabid, position_name=position, userid=new_userid)
    # upload attachments
    if attachments:
        upload_attachments(API_KEY=API_KEY, new_elabid=new_elabid, attachments=attachments)
    # get std-id [yyxxx] and std-name [Aa-yy-xxx] of newly created sample:
    # new_stdname = new_sample['title'][:9]
    return 0 # for confirmation message to user

def batch_pieces_reducer(API_KEY, batch):
    '''
    Reduces the "Available pieces" field value of the substrates batch chosen during
    sample creation by one.
    Returns remaining pieces to warn the user if the number is too low or zero (depletion
    of the batch).
    '''
    batch_url = f"{items_url}/{batch}/"
    header = Header(API_KEY).dump()

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
== DATA FOR FORM BUILDING SECTION =======================================================================================================
=========================================================================================================================================
'''

def get_available_slots(API_KEY, tracker):
    '''
    Returns a list of the available slot in a Tracker-class object sorted by name.
    '''
    available_slots = tracker.getavailable()
    sorted_slots = sorted(available_slots, key=lambda item: (item["name"]))
    return sorted_slots

def get_substrate_batches(API_KEY):
    '''
    Looks up every Item of the "Substrates Batch" Category and returns a list of those
    with at least one available piece.
    '''
    header = Header(API_KEY).dump()
    search_query = f"{items_url}?q=&cat={cat.get("substrates batch")}&limit=9999" # "SUBSTRATES BATCH" should be id = 9
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
    '''Returns a list of proposals - which are a category of Items on eLabFTW.'''
    header = Header(API_KEY).dump()
    search_query = f"{items_url}?q=&cat={cat.get("proposal")}&limit=9999" # "PROPOSAL" should be id = 15
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