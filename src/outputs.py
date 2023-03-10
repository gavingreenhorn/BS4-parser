# outputs.py
import csv
import logging
from datetime import datetime

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT
from constants import FILE_SAVED_AT, PRETTY_OUTPUT, FILE_OUTPUT


FILE_NAME_TEMPLATE = '{mode}_{datetime}.csv'


def file_output(results, cli_args):
    # константа определяется здесь, чтобы успокоился pytest
    RESULTS_DIR = BASE_DIR / 'results'
    RESULTS_DIR.mkdir(exist_ok=True)
    file_name = FILE_NAME_TEMPLATE.format(
        mode=cli_args.mode,
        datetime=datetime.strftime(
            datetime.now(), DATETIME_FORMAT))
    file_path = RESULTS_DIR / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        csv.writer(
            file,
            dialect=csv.unix_dialect).writerows(results)
    logging.info(FILE_SAVED_AT.format(path=file_path))


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


OUTPUT_EXECUTORS = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUT_EXECUTORS[cli_args.output](results, cli_args)
