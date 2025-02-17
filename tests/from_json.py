from amore.api.client import create_sample
import json

def test_create_sample():
    with open('tests/exsample.json', 'r') as file:
        data = json.load(file)
    title = data['title']
    body = data['body']
    tags = data['tags']

    create_sample(title=title, body=body, status="", tags=tags, substrate_batch="", position="")

if __name__ == "__main__":
    test_create_sample()