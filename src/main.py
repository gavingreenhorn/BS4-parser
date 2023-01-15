# main.py
import re
import logging
from urllib.parse import urljoin
from typing import NamedTuple, List, Iterator
from collections import Counter

from requests_cache import CachedSession
from bs4 import BeautifulSoup as Soup, SoupStrainer
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, PEPS_URL
from constants import EXPECTED_STATUS, UNEXPECTED_STATUS, MISSING_DATA
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response

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

    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    def scrape(session, url_prefix):
        link = urljoin(whats_new_url, url_prefix)
        response = get_response(session, link)
        response.encoding = 'utf-8'
        soup = Soup(response.text, features='lxml')
        return (link, *About.from_tags(soup.section))

    soup = Soup(
        get_response(session, whats_new_url).text,
        features='lxml')
    main_div = soup.find('section', id='what-s-new-in-python')
    div_with_ul = main_div.find('div', class_='toctree-wrapper')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for li in tqdm(div_with_ul('li', class_='toctree-l1')):
        results.append(scrape(session, li.a['href']))

    return results


def latest_versions(session) -> List[tuple]:
    response = get_response(session, MAIN_DOC_URL)
    response.encoding = 'utf-8'
    soup = Soup(response.text, 'lxml')
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
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    response = get_response(session, downloads_url)
    response.encoding = 'utf-8'
    soup = Soup(response.text, features='lxml')
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    for a in soup.body.find(
        'table', class_='docutils')(
        'a', href=re.compile(r'.*\.zip$')
    ):
        link = urljoin(downloads_url, a['href'])
        f_name = DOWNLOADS_DIR / link.split('/')[-1]
        with open(f_name, 'wb') as file:
            file.write(session.get(link).content)
    logging.info(f'Архив был загружен и сохранён: {f_name}')


def pep(session) -> List[tuple]:
    def scrape_table() -> Iterator[str]:
        soup = Soup(
            get_response(session, PEPS_URL).text,
            features='lxml',
            parse_only=PEP_TABLE_STRAINER
        )
        for num, table in enumerate(soup('table'), 1):
            for row in tqdm(table('tr'), desc=f'Processing table {num}'):
                status_tag, link_tag = row.abbr, row.a
                if not link_tag:
                    continue
                if not status_tag:
                    logging.info(MISSING_DATA.format(
                        PEP=link_tag.text,
                        datapoint='статус'
                    ))
                    continue
                expected_status = EXPECTED_STATUS[status_tag.text[1:]]
                actual_status = scrape_article_for_status(link_tag['href'])
                if actual_status not in expected_status:
                    logging.info(UNEXPECTED_STATUS.format(
                        PEP=link_tag['href'],
                        expected=expected_status,
                        actual=actual_status))
                yield actual_status

    def scrape_article_for_status(url) -> str:
        soup = Soup(
            get_response(session, urljoin(PEPS_URL, url)).text,
            features='lxml',
            parse_only=PEP_ARTICLE_STRAINER
        )
        for tag in soup.dl('dt'):
            if tag.text == "Status:":
                return tag.find_next_sibling().text
        else:
            logging.info('Не нашёл актуального статуса в статье')

    return [('Статус', 'Количество')] + list(Counter(scrape_table()).items())


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
    logging.info(f'Аргументы командной строки: {args}')
    parser_mode = args.mode
    with CachedSession() as session:
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
