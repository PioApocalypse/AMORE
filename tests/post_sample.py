from amore.api.client import create_sample
from datetime import datetime

def test_create_sample():
    mytitle = "Test sample"
    title = f"NA-{datetime.now().strftime("%y")}-001 - {mytitle}"
    status = 2
    tags = ["test", "primo campione"]
    body = "Bla bla bla"
    substrate_batch = "Batch 1"
    position = "A1"

    create_sample(title, body, status, tags, substrate_batch, position)
    #populate_sample(title, date, status, tags, body, substrate_batch, position)
    #assert "id" in response
    #assert response["title"] == title
    #assert response["category_id"] == 10

test_create_sample()