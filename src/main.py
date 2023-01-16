# main.py
import logging
import re
from requests.exceptions import RequestException
from collections import Counter
from typing import List, Iterator
from urllib.parse import urljoin

from bs4 import SoupStrainer
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_URL, MAIN_DOC_URL, PEPS_URL,
                       EXPECTED_STATUS, UNEXPECTED_STATUS, MISSING_DATA,
                       DOWNLOAD_SAVED_AT, ARGUMENTS_MESSAGE, WHATS_NEW_URL,
                       MISSING_STATUS)
from outputs import control_output
from utils import get_soup, ParserStatusMissingException

PEP_TABLE_STRAINER = SoupStrainer('table')
PEP_ARTICLE_STRAINER = SoupStrainer('dl')


def whats_new(session) -> List[tuple]:
    def scrape(session, url_prefix):
        link = urljoin(WHATS_NEW_URL, url_prefix)
        section = get_soup(session, link).section
        return (link, section.h1.text.rstrip('¶'),
                section.dl.text.replace('\n', ' '))

    log_messages = []
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    try:
        for li in tqdm(
            get_soup(session, WHATS_NEW_URL).select(
                '#what-s-new-in-python div.toctree-wrapper li.toctree-l1')):
            results.append(scrape(session, li.a['href']))
    except RequestException as exception:
        log_messages.append(exception)
    for message in log_messages:
        logging.info(message)
    return results


def latest_versions(session) -> List[tuple]:
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    log_messages = []
    try:
        for ul in get_soup(session, MAIN_DOC_URL).find(
            'div', class_='sphinxsidebarwrapper'
        )('ul'):
            if 'All versions' in ul.text:
                for tag in tqdm(ul('a')):
                    match = re.search(
                        r'Python (\d\.\d+) \((.*)\)', tag.text)
                    if match:
                        version, status = match.groups()
                        results.append((tag['href'], version, status))
                break
    except RequestException as exception:
        log_messages.append(exception)
    for message in log_messages:
        logging.info(message)
    return results


def download(session) -> None:
    soup = get_soup(session, DOWNLOADS_URL)
    # константа определяется здесь, чтобы успокоился pytest
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    log_messages = []
    try:
        for link in tqdm(soup.body.select('table.docutils a[href$=".zip"]')):
            url = urljoin(DOWNLOADS_URL, link['href'])
            f_name = DOWNLOADS_DIR / url.split('/')[-1]
            with open(f_name, 'wb') as file:
                file.write(session.get(url).content)
            log_messages.append(DOWNLOAD_SAVED_AT.format(path=f_name))
    except RequestException as error:
        log_messages.append(error)
    for message in log_messages:
        logging.info(message)


def scrape_table(session, scrape_article) -> Iterator[str]:
    for num, table in enumerate(get_soup(
        session, PEPS_URL, PEP_TABLE_STRAINER)('table'), 1
    ):
        log_messages = []
        for row in tqdm(table('tr'), desc=f'Processing table {num}'):
            status_tag, link_tag = row.abbr, row.a
            if not link_tag:
                continue
            if not status_tag:
                log_messages.append(MISSING_DATA.format(
                    PEP=link_tag.text,
                    datapoint='статус'))
                continue
            expected_status = EXPECTED_STATUS[status_tag.text[1:]]
            try:
                actual_status = scrape_article(link_tag['href'])
            except ParserStatusMissingException:
                log_messages.append(
                    MISSING_STATUS.format(PEP=link_tag['href']))
            except RequestException as exception:
                log_messages.append(exception)
            if actual_status not in expected_status:
                log_messages.append(UNEXPECTED_STATUS.format(
                    PEP=link_tag['href'],
                    expected=expected_status,
                    actual=actual_status))
            yield actual_status
        for message in log_messages:
            logging.info(message)


def pep(session) -> List[tuple]:
    def scrape_article_for_status(url) -> str:
        soup = get_soup(session, urljoin(PEPS_URL, url), PEP_ARTICLE_STRAINER)
        for tag in soup.dl('dt'):
            if tag.text == "Status:":
                return tag.find_next_sibling().text
        else:
            raise ParserStatusMissingException

    counter = Counter(scrape_table(session, scrape_article_for_status))
    return [('Статус', 'Количество'),
            *list(counter.items()),
            ('Все PEP', sum(counter.values()))]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(ARGUMENTS_MESSAGE.format(args=args))
    parser_mode = args.mode
    try:
        with CachedSession() as session:
            if args.clear_cache:
                session.cache.clear()
            results = MODE_TO_FUNCTION[parser_mode](session)
            if results is not None:
                control_output(results, args)
    except Exception as error:
        logging.error(error)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
