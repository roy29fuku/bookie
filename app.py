import time
import os
from urllib.error import HTTPError
from chalice import Chalice
import bottlenose
from bs4 import BeautifulSoup

app = Chalice(app_name='bookie')
app.debug = True

BOOKIE_AWS_ASSOCIATE_TAG = os.environ.get("BOOKIE_AWS_ASSOCIATE_TAG")
BOOKIE_AWS_ACCESS_KEY_ID = os.environ.get("BOOKIE_AWS_ACCESS_KEY_ID")
BOOKIE_AWS_SECRET_ACCESS_KEY = os.environ.get("BOOKIE_AWS_SECRET_ACCESS_KEY")
# TODO: chalice localだとconfig.jsonを環境変数から読み取らないので適宜設定する必要があるので修正


def error_handler(err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        time.sleep(1)
        return True


def get_profile(soup):
    profile = {}
    try:
        profile['title'] = soup.find('title').text
    except:
        profile['title'] = ''
    try:
        profile['author'] = soup.find('author').text
    except:
        profile['author'] = ''
    try:
        profile['label'] = soup.find('label').text
    except:
        profile['label'] = ''
    try:
        profile['categories'] = get_categories(soup)
    except:
        profile['categories'] = []
    try:
        profile['review'] = get_review(soup)
    except:
        profile['review'] = ''
    try:
        profile['large_image_url'] = soup.find('largeimage').text
    except:
        profile['large_image_url'] = ''
    return profile


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
    """
    書籍のISBNをパラメータにして叩くと、Amazon.co.jpから書籍情報を取得
    これをJSON形式でreturn
    :param isbn: ISBN-10（10桁の数字）
    :return:
    """
    try:
        amazon = bottlenose.Amazon(
            AWSAccessKeyId=BOOKIE_AWS_ACCESS_KEY_ID,
            AWSSecretAccessKey=BOOKIE_AWS_SECRET_ACCESS_KEY,
            AssociateTag=BOOKIE_AWS_ASSOCIATE_TAG,
            Region='JP',
            ErrorHandler=error_handler
        )
    except Exception as e:
        print(e)

    try:
        response = amazon.ItemLookup(
            ItemId=isbn,
            ResponseGroup="Images,ItemAttributes,BrowseNodes,EditorialReview",
            SearchIndex="Books",
            IdType="ISBN")
    except Exception as e:
        print(e)

    soup = BeautifulSoup(response, 'lxml')
    profile = get_profile(soup)
    return {
        'isbn': isbn,
        'title': profile['title'],
        'author': profile['author'],
        'label': profile['label'],
        'categories': profile['categories'],
        'review': profile['review'],
        'large_image_url': profile['large_image_url']
    }


if __name__ == '__main__':
    isbn = '4040800206'
    get_isbn(isbn)
