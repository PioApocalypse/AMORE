from amore.api.utils import id_generator
from amore.api.client import create_sample
from datetime import datetime
from random import randrange as rr

'''
WARNING! Unique ID is randomly generated.
This playground is meant to be nuked as soon
as this project is put in production.
'''

def test_create_sample():
    mytitle = "Glutammato di stronzio"
    id = id_generator()
    std_id = id[0]
    title = f"{id[1]} {mytitle}"
    status = 1
    tags = ["test", "primo campione"]
    body = "Bla bla bla"
    substrate_batch = "Batch 1"
    position = "A1"

    create_sample(title, body, status, tags, std_id, substrate_batch, position)
    #populate_sample(title, date, status, tags, body, substrate_batch, position)
    #assert "id" in response
    #assert response["title"] == title
    #assert response["category_id"] == 10

if __name__ == "__main__":
    test_create_sample()