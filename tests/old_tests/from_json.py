from amore.api.client import create_sample
import json
from random import randrange as rr

def test_create_sample():
    with open('tests/exsample.json', 'r') as file:
        data = json.load(file)
    body = data['body']
    tags = data['tags']
    #std_id = data['std_id']
    std_id = 25000 + rr(1,999,1)
    title = f"Na-{std_id // 1000}-{std_id % 1000} -- {data['title']}"

    create_sample(title=title, body=body, status="", tags=tags, std_id=std_id, substrate_batch="", position="")

if __name__ == "__main__":
    test_create_sample()