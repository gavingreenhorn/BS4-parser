from bs4 import BeautifulSoup as Soup
import requests

from constants import TAG_NOT_FOUND_MESSAGE, CONNECTION_ERROR_MESSAGE


class ParserFindTagException(Exception):
    pass


class ParserStatusMissingException(Exception):
    pass


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except requests.exceptions.RequestException:
        raise ConnectionError(
            CONNECTION_ERROR_MESSAGE.format(url=url))


def get_soup(session, url, strainer=None, features='lxml'):
    return Soup(
        get_response(session, url).text,
        parse_only=strainer,
        features=features)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if searched_tag is None:
        raise ParserFindTagException(
            TAG_NOT_FOUND_MESSAGE.format(tag=tag, attrs=attrs))
    return searched_tag
