import time
import os
from os.path import join, dirname
from urllib.error import HTTPError
from dotenv import load_dotenv
import bottlenose
from bs4 import BeautifulSoup

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

AWS_ASSOCIATE_TAG = os.environ.get("AWS_ASSOCIATE_TAG")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


def error_handler(err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        time.sleep(1) # 1秒待つ
        return True


def get_categories(soup):
    nodes = soup.find('browsenodes').find_all('browsenode', recursive=False)
    categories = []
    for node in nodes:
        names = node.find_all('name', recursive=False)
        names = [n.text for n in names]
        categories.extend(names)
    return categories


if __name__ == '__main__':
    amazon = bottlenose.Amazon(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        AWS_ASSOCIATE_TAG,
        Region='JP',
        ErrorHandler=error_handler
    )
    isbn = '4040800206'
    response = amazon.ItemLookup(
        ItemId=isbn,
        ResponseGroup="Images,ItemAttributes,BrowseNodes",
        SearchIndex="Books",
        IdType="ISBN")

    soup = BeautifulSoup(response, 'lxml')

    title = soup.find('title').text
    author = soup.find('author').text
    label = soup.find('label').text
    categories = get_categories(soup)
    large_image_url = soup.find('largeimage').text

    print(isbn)
    print(title)
    print(author)
    print(label)
    print(categories)
    print(large_image_url)
