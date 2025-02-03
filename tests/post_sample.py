from amore.api.client import create_sample
from datetime import datetime

def test_create_sample():
    mytitle = "Test sample"
    title = f"NA-{datetime.now().strftime("%y")}-002 - {mytitle}"
    date = datetime.now().strftime("%Y-%m-%d")
    status = "In Progress"
    tags = ["test, sample"]
    body = "Bla bla bla"
    substrate_batch = "Batch 1"
    position = "A1"

    create_sample(title) # title, date, status, tags, body, substrate_batch, position)
    assert "id" in response
    #assert response["title"] == title
    #assert response["category_id"] == 10

test_create_sample()