import argparse

import logging
from logging.handlers import RotatingFileHandler

from constants import LOG_DIR, PARSER_LOG_NAME, PRETTY_OUTPUT, FILE_OUTPUT

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
OUTPUT_OPTIONS = (PRETTY_OUTPUT, FILE_OUTPUT)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=OUTPUT_OPTIONS,
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        PARSER_LOG_NAME, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
