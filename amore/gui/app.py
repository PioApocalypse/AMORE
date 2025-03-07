from flask import Flask, request, render_template, redirect, flash
import amore.api.client as amore
from amore.api.utils import id_generator

app = Flask(__name__)

@app.route("/")
def home():
    positions = amore.get_positions() # which is a list of dicts
    batches = amore.get_substrate_batches() # which is a list of dicts
    proposals = amore.get_proposals() # you get the gist
    return render_template("index.html", positions=positions, batches=batches, proposals=proposals)

@app.route("/create_sample", methods=["POST"])
def handle_create_sample():
    title = request.form.get("title")
    position = request.form.get("position") # ID of item
    batch = request.form.get("batch") # ID of item
    subholder = request.form.get("subholder")

    id_generated = id_generator(request.form.get("location")) # list
    proposal = request.form.get("proposal") # ID of item
    tags = request.form.get("tags").split(",")  # Convert tags to a list
    description = request.form.get("description")

    std_id = id_generated[0] # index 0 of id_generator returns numeric id in yyxxx format
    full_id = id_generated[1] # index 1 of id_generator returns full code in Na-{%y}-xxx format

    # This is where the fun begins:
    amore.create_sample(
        title=f"{full_id} - {title}",
        tags=tags,
        std_id=std_id,
        body=description,
        position=position,
        batch=batch,
        subholder=subholder,
        proposal=proposal,
    )

    # Redirect back to the home page
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)