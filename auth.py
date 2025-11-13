import os

VALID_USERNAME = os.environ["VALID_USERNAME"]
VALID_PASSWORD = os.environ["VALID_PASSWORD"]

def check_credentials(username, password):
    print(username, password)
    return username == VALID_USERNAME and password == VALID_PASSWORD
