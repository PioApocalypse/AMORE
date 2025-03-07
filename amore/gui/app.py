from flask import Flask, request, render_template, redirect, flash
import secrets
import amore.api.client as amore
from amore.api.utils import id_generator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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

    try:
        # recall batches variable BEFORE patching batch
        batches = amore.get_substrate_batches()
        # decrease number of available pieces in selected batch
        remaining = amore.batch_pieces_decreaser(batch)
        # this is where the magic happens:
        amore.create_sample(
            title=f"{full_id} - {title}",
            tags=tags,
            std_id=std_id,
            body=description,
            position=position,
            batch=batch,
            subholder=subholder,
            proposal=proposal,)
        flash(f'Item successfully created with Standard ID "{full_id}".', "success")
        batch_name = next((item['name'] for item in batches if item['id'] == batch), "you've just selected")
        if remaining <= 0:
            flash(f"Beware: The batch {batch_name} is now out of stock!", "batch_oos") # oos = out of stock
        elif remaining < 5:
            flash(f"Urgent: The batch {batch_name} is low on stock with {remaining} pieces left!", "batch_los") # los = low on stock
    except Exception as e:
        flash(f'Error processing your request: {str(e)}.', 'error')
    # redirect back to the home page
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)