import requests
import json

def post_experiment():
    # reads from metadata.json
    with open('metadata.json', 'r') as md_file:
        metadata = json.load(md_file)

    url = API_URL
    api_key = API_KEY
    headers = {'Authorization': api_key}
    
    # request to POST header and metadata to url then  record server response as 'response'
    # note for self: this is not sufficient if API_URL is just 'https://elabftw.base.url/api/v2/' since 'experiments/' has to be appended to it
    # as this script is specific to experiments
    response = requests.post(url, headers=headers, json=metadata, verify=False)  # verify=false is essential since our elab is SSL self-signed

    if response.status_code == 201:
        print("Experiment created!")
    else:
        print(f"ERROR {response.status_code}: {response.text}")

if __name__ == "__main__":
    post_experiment()