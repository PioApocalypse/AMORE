import os
import requests
import json

'''
Use this file for AND ONLY FOR storing functions for authentication.
'''

"""
How do I check if an API key 1. is valid and 2. has read-write permissions?
eLabFTW has an endpoint for calling pre-existent API keys associated to one's account
The keys are always stored encrypted, no way to recover them if lost - thank god
Encryption method is bcrypt, SALT is unknown and on server so no way to check if hash corresponds
The only way is making a GET request to the apikey endpoint and look for the one that's been just used
/tests/api_get.py
"""

