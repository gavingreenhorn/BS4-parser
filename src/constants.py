from pathlib import Path
from urllib.parse import urljoin

# literals
PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

# file system paths
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
PARSER_LOG_NAME = LOG_DIR / 'parser.log'

# urls
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOADS_URL = urljoin(MAIN_DOC_URL, 'download.html')

# formatting strings
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# dictionaries


EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

# info messages
ARGUMENTS_MESSAGE = 'Аргументы командной строки: {args}'
FILE_SAVED_AT = 'Файл с результатами был сохранён: {path}'
DOWNLOAD_SAVED_AT = 'Архив был загружен и сохранён: {path}'
UNEXPECTED_STATUS = ('Не совпадают статусы для статьи PEP{PEP}. '
                     'Ожидаемые: {expected}, '
                     'действительный {actual}')
MISSING_DATA = 'В таблице не найден {datapoint} для статьи {PEP}'
MISSING_STATUS = 'Не найден актуальный статус в статье {PEP}'

# exception messages
CONNECTION_ERROR_MESSAGE = 'Ошибка соединения при отправке запроса на {url}'
LOADING_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {url}'
TAG_NOT_FOUND_MESSAGE = 'Не найден тег {tag} {attrs}'
