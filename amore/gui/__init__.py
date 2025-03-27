'''
External modules. In particular, from flask:
- Flask object implements the WSGI. Usage: app = Flask(__name__) - operations on variable 'app' setup the environment configuration.
- request is used to get variables values from the HTML form upon submission.
- render_template and redirect are quite obvious, look them up.
- flash allows for "flash" (pop-up) messages to warn user if something goes wrong (or right).
'''
from flask import Flask, request, render_template, redirect, flash
import secrets # for session cookies
import os # use method os.environ.get() to bypass the need for a .env file/dotenv module
'''From inside the project:'''
import amore.api.client as amore # client module, see: ./amore/api/client.py
import amore.api.utils as utils # utilities module, see: ./amore/api/utils.py
from . import create # form to create sample

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config.from_mapping(
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 # default Flask limit is 16 MB
)