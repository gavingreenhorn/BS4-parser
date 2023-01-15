# main.py
import logging
import re
from collections import Counter
from typing import NamedTuple, List, Iterator
from urllib.parse import urljoin

from bs4 import SoupStrainer
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import DOWNLOADS_DIR, MAIN_DOC_URL, PEPS_URL, WHATS_NEW_URL
from constants import EXPECTED_STATUS, UNEXPECTED_STATUS, MISSING_DATA
from constants import DOWNLOAD_SAVED_AT, ARGUMENTS_MESSAGE
from outputs import control_output
from utils import get_soup

PEP_TABLE_STRAINER = SoupStrainer('table')
PEP_ARTICLE_STRAINER = SoupStrainer('dl')


def whats_new(session) -> List[tuple]:

    class About(NamedTuple):
        title: str
        extra: str

        @classmethod
        def from_tags(cls, section) -> 'About':
            return cls(
                section.h1.text.rstrip('¶'),
                section.dl.text.replace('\n', ' '))

    def scrape(session, url_prefix):
        link = urljoin(WHATS_NEW_URL, url_prefix)
        soup = get_soup(session, link)
        return (link, *About.from_tags(soup.section))

    soup = get_soup(session, WHATS_NEW_URL)
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for li in tqdm(
        soup.select('#what-s-new-in-python div.toctree-wrapper li.toctree-l1')
    ):
        results.append(scrape(session, li.a['href']))

    return results


def latest_versions(session) -> List[tuple]:
    soup = get_soup(session, MAIN_DOC_URL)
    ul_tags = soup.find('div', class_='sphinxsidebarwrapper')('ul')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for ul in ul_tags:
        if 'All versions' in ul.text:
            for tag in tqdm(ul('a')):
                match = re.search(
                    r'Python (\d\.\d+) \((.*)\)', tag.text)
                if match:
                    version, status = match.groups()
                    results.append((tag['href'], version, status))
            break
    return results


def download(session) -> None:
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    for link in tqdm(soup.body.select('table.docutils a[href$=".zip"]')):
        url = urljoin(downloads_url, link['href'])
        f_name = DOWNLOADS_DIR / url.split('/')[-1]
        with open(f_name, 'wb') as file:
            file.write(session.get(url).content)
        logging.info(DOWNLOAD_SAVED_AT.format(path=f_name))


def pep(session) -> List[tuple]:
    def scrape_article_for_status(url) -> str:
        soup = get_soup(session, urljoin(PEPS_URL, url), PEP_ARTICLE_STRAINER)
        for tag in soup.dl('dt'):
            if tag.text == "Status:":
                return tag.find_next_sibling().text
        else:
            logging.info('Не нашёл актуального статуса в статье')

    def scrape_table() -> Iterator[str]:
        soup = get_soup(session, PEPS_URL, PEP_TABLE_STRAINER)
        log_messages = []
        for num, table in enumerate(soup('table'), 1):
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
                actual_status = scrape_article_for_status(link_tag['href'])
                if actual_status not in expected_status:
                    log_messages.append(UNEXPECTED_STATUS.format(
                        PEP=link_tag['href'],
                        expected=expected_status,
                        actual=actual_status))
                yield actual_status
        for message in log_messages:
            logging.info(message)

    counter = Counter(scrape_table())
    return [('Статус', 'Количество')] + list(counter.items()) \
        + [('Все PEP', sum(counter.values()))]


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
    with CachedSession() as session:
        if args.clear_cache:
            session.cache.clear()
        try:
            results = MODE_TO_FUNCTION[parser_mode](session)
        except Exception as error:
            logging.error(error)
        if results is not None:
            control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
