from flask import Flask, request, render_template, redirect, flash
from amore.api.client import create_sample
from amore.api.utils import id_generator

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create_sample", methods=["POST"])
def handle_create_sample():
    title = request.form.get("title")
    position = request.form.get("position")
    batch = request.form.get("batch")
    subholder = request.form.get("subholder")

    id_generated = id_generator(request.form.get("location"))
    proposal = request.form.get("proposal")
    tags = request.form.get("tags").split(",")  # Convert tags to a list
    next_step = request.form.get("next_step")
    print(next_step) # debug
    try:
        next_step
    except:
        next_step = "conquer the world" # placeholder
    description = request.form.get("description")

    std_id = id_generated[0] # index 0 of id_generator returns numeric id in yyxxx format
    full_id = id_generated[1] # index 1 of id_generator returns full code in Na-{%y}-xxx format

    # This is where the fun begins:
    create_sample(
        title=f"{full_id} - {title}",
        tags=tags,
        std_id=std_id,
        body=description,
        position=position,
        batch=batch,
        subholder=subholder,
        proposal=proposal,
        next_step=next_step
    )

    # Redirect back to the home page
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)