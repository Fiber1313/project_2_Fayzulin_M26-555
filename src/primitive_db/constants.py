"""Константы проекта primitive_db."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_EXTENSION = ".json"

ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")
COLUMN_SEPARATOR = ":"

TRUE_LITERAL = "true"
FALSE_LITERAL = "false"
QUOTES = ('"', "'")
VALUES_SEPARATOR = ","
ASSIGNMENT_SIGN = "="

INTO_KEYWORD = "into"
FROM_KEYWORD = "from"
VALUES_KEYWORD = " values "
WHERE_KEYWORD = " where "
SET_KEYWORD = " set "

INPUT_PROMPT = ">>>Введите команду: "
CONFIRM_ANSWER = "y"
TIME_PRECISION = 3

HELP_TEXT = """
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***
Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - \
создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> - \
прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where \
<столбец_условия> = <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - \
удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация
"""
