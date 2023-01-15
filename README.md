# Проект парсинга PEP
## Автор
[Случайный студент Практикума](https://github.com/gavingreenhorn)
## Стек
- Python 3.9
- [requests_cache](https://pypi.org/project/requests-cache/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [PrettyTable](https://pypi.org/project/prettytable/)
- [tqdm](https://github.com/tqdm/tqdm)
## Развертывание
>``git clone git@github.com:gavingreenhorn/bs4_parser_pep.git``

>``python -m venv venv``

>``$ source venv/bin/activate``

>``python -m pip install -r requirements.txt``
## Запуск
>``python main.py <mode (whats-new|latest-versions|pep|download)> [-h --help][-c --clear-cache][-o --option (pretty|file)]``
## Результат
В зависимости от выбранного режима работы:
- вывод в неотформатированных результатов в консоль (умолачение)
- вывод в консоль в виде таблицы
- сохранение csv-файла в ./results
- (для режима **download**): сохранение в ./downloads


