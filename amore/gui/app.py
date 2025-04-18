'''
External modules. In particular, from flask:
- Flask object implements the WSGI. Usage: app = Flask(__name__) - operations on variable 'app' setup the environment configuration.
- request is used to get variables values from the HTML form upon submission.
- render_template and redirect are quite obvious, look them up.
- flash allows for "flash" (pop-up) messages to warn user if something goes wrong (or right).
- get_flashed_messages to show messages created before redirect (Use: get_flashed_messages() on first line of destination route function).
- session allows to store information into cookies.
'''
from flask import Flask, request, render_template, redirect, flash, get_flashed_messages, session
import secrets # for session cookies
from datetime import timedelta # for session timeout
import os # use method os.environ.get() to bypass the need for a .env file/dotenv module
import amore.api.client as amore # client module, see: amore/api/client.py
import amore.api.utils as utils # utilities module, see: amore/api/utils.py
import amore.api.auth as auth # authentication module, see: amore/api/auth.py

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # default Flask limit is 16 MB


'''
The following function is not associated to a route. It checks if current
session contains an "api_key" non-null value then calls check_apikey
function to verify if that value is a valid API key. If both this
conditions are not met, it clears the entire session altogether and
redirects to login. Otherwise it returns 0.
'''
def check_session():
    if session.get('api_key') == None:
        session.clear()
        return redirect("/login")
    else:
        try:
            auth.check_apikey(session['api_key'])
            return 0
        except Exception as e:
            session.clear()
            flash(str(e), 'error')
            return redirect("/login")
'''
Usage: if check_session() != 0 return output of check_session, which
is just redirect to login page, otherwise, execute the rest.

    check = check_session()
    if check != 0:
        return check
    # <rest of the function>
'''

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/login", methods=["GET","POST"])
def login():
    # Inherit flashed messages from functions redirecting to this (i.e. the logout pop-up message).
    get_flashed_messages()
    # First of all check if session already exists and user doesn't need to login.
    check = check_session()
    if check == 0:
        return redirect("/") # no need to login = let's get down to business
    # If user is submitting their API key then method is POST, therefore validate:
    if request.method == "POST":
        API_KEY = request.form.get("api_key")
        try:
            session['user'] = auth.check_apikey(KEY=API_KEY)
            session['api_key'] = API_KEY
            flash(f"Welcome, {session['user']}!", 'success')
            # flash(f"Here's you key: {session['api_key']}", 'success') # debug only
            return redirect("/create")
        except Exception as e:
            flash(str(e), 'error')
            # return redirect("/login")

    # If user is just loading the page then method is GET, therefore render login page.
    return render_template("login.html")

@app.route("/logout")
def logout():
    check = check_session()
    if check != 0:
        flash(f"You're already unauthenticated. Login to logout.", 'error')
        return redirect("/login")
    else:
        session.clear()
        flash("Successfully logged out.", 'success')
        return redirect("/login")

@app.route("/")
def root():
    check = check_session()
    if check != 0:
        return check
    user = session.get('user') or "unspecified user"
    return render_template("index.html", user=user)

'''
Pages that require a valid r/w API key (login) to work.
'''

@app.route("/create")
def home():
    check = check_session()
    if check != 0:
        return check
    API_KEY = session.get('api_key')
    user = session.get('user') or "unspecified user"
    tracker = amore.sample_locator(API_KEY)
    positions = amore.get_available_slots(API_KEY, tracker) # which is a list of dicts
    batches = amore.get_substrate_batches(API_KEY) # which is a list of dicts
    proposals = amore.get_proposals(API_KEY) # you get the gist
    return render_template("create_sample.html", user=user, positions=positions, batches=batches, proposals=proposals)

@app.route("/create_sample", methods=["POST"])
def handle_create_sample():
    check = check_session()
    if check != 0:
        return check
    API_KEY = session.get('api_key')
    title = request.form.get("title")
    position = request.form.get("position") # name of position
    batch = request.form.get("batch") # ID of item
    subholder = request.form.get("subholder")

    id_generated = utils.id_generator(request.form.get("location")) # list
    proposal = request.form.get("proposal") # ID of item
    tags = request.form.get("tags").split(",")  # Convert tags to a list
    description = request.form.get("description")
    
    uploads = request.files.getlist("attachments")
    try:
        attachments = utils.attachment_handler(uploads=uploads)
    except Exception as e:
        flash(str(e), 'error')
        # return redirect("/")

    std_id = id_generated[0] # index 0 of id_generator returns numeric id in yyxxx format
    full_id = id_generated[1] # index 1 of id_generator returns full code in Na-{%y}-xxx format

    try: # check for successful decrement of available pieces
        # recall batches variable BEFORE patching batch
        batches = amore.get_substrate_batches(API_KEY)
        # decrease number of available pieces in selected batch
        remaining = amore.batch_pieces_decreaser(API_KEY, batch)
    except Exception as e:
        flash(f"Error handling batch availability: {str(e)}. Sample might have still been created.", 'batch_oos')
    
    try: # this is where the magic happens:
        amore.create_sample(
            API_KEY=API_KEY,
            title=f"{full_id} - {title}",
            tags=tags,
            std_id=std_id,
            body=description,
            position=position,
            batch=batch,
            subholder=subholder,
            proposal=proposal,
            attachments=attachments)
        flash(f'Item successfully created with Standard ID "{full_id}".', "success")
        batch_name = next((item['name'] for item in batches if item['id'] == batch), "you've just selected")
        if remaining <= 0:
            flash(f"Beware: The batch {batch_name} is now out of stock!", "batch_oos") # oos = out of stock
        elif remaining < 5:
            flash(f"Urgent: The batch {batch_name} is low on stock with {remaining} pieces left!", "batch_los") # los = low on stock
    except Exception as e:
        flash(f'Error processing your submission: {str(e)}.', 'error')
    if attachments != None:
        utils.tmp_remover(attachments) # removes tmp files in upload
    # redirect back to the home page
    return redirect("/create")

@app.route("/positions")
def handle_positions():
    check = check_session()
    if check != 0:
        return check
    API_KEY = session.get('api_key')
    tracker = amore.sample_locator(API_KEY) # which is an object of class Tracker
    slots = tracker.getslots() # see help(Tracker.getslots)
    return #render_template("positions.html", slots=slots)


if __name__ == '__main__':
    app.run(debug=True)
