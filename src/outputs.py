# outputs.py
import csv
import logging
from datetime import datetime

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT

FILE_NAME_TEMPLATE = '{mode}_{datetime}.csv'


def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    file_name = FILE_NAME_TEMPLATE.format(
                    mode=cli_args.mode,
                    datetime=datetime.strftime(
                        datetime.now(), DATETIME_FORMAT))
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)
