import time
import os
from os.path import join, dirname
from urllib.error import HTTPError
from chalice import Chalice
from dotenv import load_dotenv

app = Chalice(app_name='bookie')
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

AWS_ASSOCIATE_TAG = os.environ.get("AWS_ASSOCIATE_TAG")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


@app.route('/')
def index():

    return {'message': AWS_ASSOCIATE_TAG}
    # return {'message': 'Hi, This is bookie API server!'}


@app.route('/isbn/{isbn}')
def get_isbn(isbn):
    return {'isbn': isbn}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
