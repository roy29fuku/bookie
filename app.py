import time
import os
from urllib.error import HTTPError
from chalice import Chalice
import bottlenose
from bs4 import BeautifulSoup

app = Chalice(app_name='bookie')

BOOKIE_AWS_ASSOCIATE_TAG = os.environ.get("BOOKIE_AWS_ASSOCIATE_TAG")
BOOKIE_AWS_ACCESS_KEY_ID = os.environ.get("BOOKIE_AWS_ACCESS_KEY_ID")
BOOKIE_AWS_SECRET_ACCESS_KEY = os.environ.get("BOOKIE_AWS_SECRET_ACCESS_KEY")


def error_handler(err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        time.sleep(1)
        return True


def get_review(soup):
    # TODO: 全角スペーストリム
    # TODO: editorialreview以外にもっと良い説明文が取得できないか検討
    nodes = soup.find('editorialreviews').find_all('editorialreview')
    result = ''
    for node in nodes:
        review = node.find_all('content')
        review = ''.join([r.text for r in review])
        result += review
    return result


def get_categories(soup):
    nodes = soup.find('browsenodes').find_all('browsenode', recursive=False)
    result = []
    for node in nodes:
        names = node.find_all('name', recursive=False)
        names = [n.text for n in names]
        result.extend(names)
    return result


@app.route('/')
def index():
    return {'message': 'Hi, This is bookie API server!'}


@app.route('/isbn/{isbn}', methods=['GET'])
def get_isbn(isbn):
    amazon = bottlenose.Amazon(
        BOOKIE_AWS_ACCESS_KEY_ID,
        BOOKIE_AWS_SECRET_ACCESS_KEY,
        BOOKIE_AWS_ASSOCIATE_TAG,
        Region='JP',
        ErrorHandler=error_handler
    )
    response = amazon.ItemLookup(
        ItemId=isbn,
        ResponseGroup="Images,ItemAttributes,BrowseNodes,EditorialReview",
        SearchIndex="Books",
        IdType="ISBN")
    soup = BeautifulSoup(response, 'lxml')
    title = soup.find('title').text
    author = soup.find('author').text
    label = soup.find('label').text
    categories = get_categories(soup)
    review = get_review(soup)
    large_image_url = soup.find('largeimage').text
    return {
        'isbn': isbn,
        'title': title,
        'author': author,
        'label': label,
        'categories': categories,
        'review': review,
        'large_image_url': large_image_url
    }


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
