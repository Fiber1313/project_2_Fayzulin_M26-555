"""Главный цикл программы и обработка команд."""

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    FROM_KEYWORD,
    HELP_TEXT,
    ID_COLUMN,
    INPUT_PROMPT,
    INTO_KEYWORD,
    META_FILE,
    SET_KEYWORD,
    VALUES_KEYWORD,
    WHERE_KEYWORD,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    print_invalid_value,
    print_table_not_exists,
    select,
    update,
    validate_clause,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import (
    parse_set,
    parse_values,
    parse_where,
    split_by_keyword,
    split_params,
)
from primitive_db.utils import (
    delete_table_data,
    get_table_version,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_select = create_cacher()


def print_help():
    """Печатает справку по командам."""
    print(HELP_TEXT)


def print_records(schema, records):
    """Выводит записи таблицы с помощью PrettyTable."""
    table = PrettyTable()
    table.field_names = list(schema)
    for record in records:
        table.add_row([record.get(column) for column in schema])
    print(table)


def strip_keyword(text, keyword):
    """Убирает ключевое слово в начале строки; возвращает остаток или None."""
    first_word, _, rest = text.partition(" ")
    if first_word != keyword:
        return None
    return rest.strip()


def get_existing_table(metadata, table_name):
    """Возвращает схему таблицы или None, если таблицы нет."""
    if table_name not in metadata:
        print_table_not_exists(table_name)
        return None
    return metadata[table_name]


def handle_create_table(metadata, user_input, params):
    """Обрабатывает команду create_table."""
    if len(params) < 2:
        print_invalid_value(user_input)
        return
    metadata = create_table(metadata, params[0], params[1:])
    if metadata is not None:
        save_metadata(META_FILE, metadata)


def handle_drop_table(metadata, user_input, params):
    """Обрабатывает команду drop_table."""
    if len(params) != 1:
        print_invalid_value(user_input)
        return
    if get_existing_table(metadata, params[0]) is None:
        return
    metadata = drop_table(metadata, params[0])
    if metadata is not None:
        save_metadata(META_FILE, metadata)
        delete_table_data(params[0])


def handle_insert(metadata, user_input, rest):
    """Обрабатывает команду insert into <таблица> values (...)."""
    tail = strip_keyword(rest, INTO_KEYWORD)
    if tail is None:
        print_invalid_value(user_input)
        return
    table_name, values_text = split_by_keyword(tail, VALUES_KEYWORD)
    if values_text is None:
        print_invalid_value(user_input)
        return
    values = parse_values(values_text)
    result = insert(metadata, table_name, values)
    if result is None:
        return
    table_data, new_id = result
    save_table_data(table_name, table_data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


def handle_select(metadata, user_input, rest):
    """Обрабатывает команду select from <таблица> [where ...]."""
    tail = strip_keyword(rest, FROM_KEYWORD)
    if tail is None:
        print_invalid_value(user_input)
        return
    table_name, where_text = split_by_keyword(tail, WHERE_KEYWORD)
    schema = get_existing_table(metadata, table_name)
    if schema is None:
        return
    where_clause = parse_where(where_text) if where_text else None
    if where_clause and not validate_clause(schema, where_clause):
        return
    cache_key = (table_name, where_text, get_table_version(table_name))

    def read_records():
        return select(load_table_data(table_name), where_clause)

    records = cache_select(cache_key, read_records)
    if records is not None:
        print_records(schema, records)


def handle_update(metadata, user_input, rest):
    """Обрабатывает команду update <таблица> set ... where ...."""
    table_name, after_set = split_by_keyword(rest, SET_KEYWORD)
    if after_set is None:
        print_invalid_value(user_input)
        return
    set_text, where_text = split_by_keyword(after_set, WHERE_KEYWORD)
    if where_text is None:
        print_invalid_value(user_input)
        return
    schema = get_existing_table(metadata, table_name)
    if schema is None:
        return
    set_clause = parse_set(set_text)
    where_clause = parse_where(where_text)
    if ID_COLUMN in set_clause:
        print_invalid_value(ID_COLUMN)
        return
    if not validate_clause(schema, set_clause):
        return
    if not validate_clause(schema, where_clause):
        return
    result = update(load_table_data(table_name), set_clause, where_clause)
    if result is None:
        return
    table_data, updated_ids = result
    if not updated_ids:
        print("Ошибка: Записи, подходящие под условие, не найдены.")
        return
    save_table_data(table_name, table_data)
    for record_id in updated_ids:
        print(
            f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
        )


def handle_delete(metadata, user_input, rest):
    """Обрабатывает команду delete from <таблица> where ...."""
    tail = strip_keyword(rest, FROM_KEYWORD)
    if tail is None:
        print_invalid_value(user_input)
        return
    table_name, where_text = split_by_keyword(tail, WHERE_KEYWORD)
    if where_text is None:
        print_invalid_value(user_input)
        return
    schema = get_existing_table(metadata, table_name)
    if schema is None:
        return
    where_clause = parse_where(where_text)
    if not validate_clause(schema, where_clause):
        return
    result = delete(load_table_data(table_name), where_clause)
    if result is None:
        return
    table_data, deleted_ids = result
    if not deleted_ids:
        print("Ошибка: Записи, подходящие под условие, не найдены.")
        return
    save_table_data(table_name, table_data)
    for record_id in deleted_ids:
        print(
            f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".'
        )


def handle_info(metadata, params):
    """Обрабатывает команду info <таблица>."""
    if len(params) != 1:
        print_invalid_value(" ".join(params))
        return
    table_name = params[0]
    if get_existing_table(metadata, table_name) is None:
        return
    info(metadata, table_name, load_table_data(table_name))


def run():
    """Запускает основной цикл работы с базой данных."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(INPUT_PROMPT).strip()
        command, _, rest = user_input.partition(" ")
        rest = rest.strip()

        try:
            match command:
                case "create_table":
                    handle_create_table(metadata, user_input, split_params(rest))
                case "drop_table":
                    handle_drop_table(metadata, user_input, split_params(rest))
                case "list_tables":
                    list_tables(metadata)
                case "insert":
                    handle_insert(metadata, user_input, rest)
                case "select":
                    handle_select(metadata, user_input, rest)
                case "update":
                    handle_update(metadata, user_input, rest)
                case "delete":
                    handle_delete(metadata, user_input, rest)
                case "info":
                    handle_info(metadata, split_params(rest))
                case "help":
                    print_help()
                case "exit":
                    return
                case _:
                    print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as error:
            print_invalid_value(error)
