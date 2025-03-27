import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
API_URL = os.getenv('ELABFTW_BASE_URL')
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    API_KEY = ""
endpoint = f"{API_URL}api/v2/apikeys"


def ismyapivalid(KEY):
    print(KEY)
    header = {
        "Authorization": KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(
        url=endpoint,
        headers=header,
        verify=True,
    )

    if response.status_code // 100 > 3:
        return 'Invalid API key'

    apikeys = [
        { 'date': item.get('last_used_at'), 'rw': item.get('can_write') }
        for item in response.json()
    ]

    last_used = max(apikeys, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'))
    return last_used['rw']
"""
tests show function returns 0 if key is read only, otherwise 1
tests show function returns 'Invalid API key' if API key is empty or invalid
"""


if __name__=="__main__":
    print(ismyapivalid(API_KEY))