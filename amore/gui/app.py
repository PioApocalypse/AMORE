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
    description = request.form.get("description")
    tags = request.form.get("tags").split(",")  # Convert tags to a list
    full_id=id_generator("Napoli")[1] # index 1 of id_generator returns full code in Na-{%y}-### format

    # This is where the fun begins:
    create_sample(
        title=f"{full_id} -- {title}",
        status=0,                       # Placeholder to be removed
        tags=tags,
        # substrate_batch="BATCH123",   # Placeholder to be removed
        # position="A1"                 # Placeholder to be removed
    )

    # Redirect back to the home page
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)