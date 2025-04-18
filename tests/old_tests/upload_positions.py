import os
import json
import requests

with open('sample_positions.json', 'r') as f:
    ls = json.load(f)


def mktitle(dic):
    title = f"POS {dic.get('machine')}"
    if dic.get('sector'):
        title += f" - {dic.get('sector')}"
    if dic.get('slot'):
        title += f" - {dic.get('slot')}"
    return title

def create_on_elab(title): 
    base_url = os.getenv('ELAB_HOST')
    url = f"https://{base_url}/api/v2/items/"
    API_KEY = os.getenv('ELAB_KEY')
    header = {"Authorization": API_KEY,
        "Content-Type": "application/json"}
    payload = {"template": 17,
    "title": title,
    "tags": ["test", "newposition", "emanuele"]}
    
    response = requests.post(
        url=url,
        headers=header,
        json=payload,
        verify=True)
    return response # for confirmation message to user

for item in ls:
    title = mktitle(item)
    r = create_on_elab(title)
    print(r)