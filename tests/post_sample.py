from amore.api.client import create_sample
from datetime import datetime
from random import randrange as rr

'''
WARNING! Unique ID is randomly generated.
This playground is meant to be nuked as soon
as this project is put in production.
'''

def test_create_sample():
    mytitle = "Test sample"
    title = f"NA-{datetime.now().strftime("%y")}-001 - {mytitle}"
    status = 2
    tags = ["test", "primo campione"]
    body = "Bla bla bla"
    unique = f"{rr(1,999,1)}" # unique is randomly generated
    std_id = 25101
    substrate_batch = "Batch 1"
    position = "A1"

    create_sample(title, body, status, tags, std_id, substrate_batch, position)
    #populate_sample(title, date, status, tags, body, substrate_batch, position)
    #assert "id" in response
    #assert response["title"] == title
    #assert response["category_id"] == 10

if __name__ == "__main__":
    test_create_sample()