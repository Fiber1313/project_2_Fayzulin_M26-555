"""Основная логика: управление таблицами и CRUD-операции."""

from primitive_db.constants import COLUMN_SEPARATOR, ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.utils import load_table_data

TYPE_BY_NAME = {"int": int, "str": str, "bool": bool}


def print_invalid_value(value):
    """Печатает сообщение о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def print_table_not_exists(table_name):
    """Печатает сообщение об отсутствующей таблице."""
    print(f'Ошибка: Таблица "{table_name}" не существует.')


def format_schema(schema):
    """Возвращает схему таблицы строкой вида 'ID:int, name:str'."""
    return ", ".join(f"{name}:{kind}" for name, kind in schema.items())


def parse_column(column):
    """Разбирает строку вида 'имя:тип' в пару (имя, тип) или возвращает None."""
    parts = column.split(COLUMN_SEPARATOR)
    if len(parts) != 2:
        return None
    name, column_type = parts
    if not name or name == ID_COLUMN or column_type not in VALID_TYPES:
        return None
    return name, column_type


def has_type(value, type_name):
    """Проверяет, что значение имеет тип столбца (bool не считается int)."""
    return type(value) is TYPE_BY_NAME[type_name]


def create_table(metadata, table_name, columns):
    """Создаёт таблицу с автоматическим столбцом ID; при ошибке возвращает None."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        parsed = parse_column(column)
        if parsed is None or parsed[0] in schema:
            print_invalid_value(column)
            return None
        name, column_type = parsed
        schema[name] = column_type

    metadata[table_name] = schema
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f"{format_schema(schema)}"
    )
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных; при ошибке возвращает None."""
    if table_name not in metadata:
        print_table_not_exists(table_name)
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Печатает список всех таблиц."""
    for table_name in metadata:
        print(f"- {table_name}")


def validate_clause(schema, clause):
    """Проверяет, что столбцы условия есть в таблице и значения нужного типа."""
    for column, value in clause.items():
        if column not in schema or not has_type(value, schema[column]):
            print_invalid_value(f"{column} = {value}")
            return False
    return True


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие where."""
    return all(record.get(column) == value for column, value in where_clause.items())


def insert(metadata, table_name, values):
    """Добавляет запись в таблицу; возвращает (данные, ID) или None при ошибке."""
    if table_name not in metadata:
        print_table_not_exists(table_name)
        return None

    schema = metadata[table_name]
    columns = [column for column in schema if column != ID_COLUMN]
    if len(values) != len(columns):
        print_invalid_value(f"ожидается значений: {len(columns)}")
        return None
    for column, value in zip(columns, values):
        if not has_type(value, schema[column]):
            print_invalid_value(value)
            return None

    table_data = load_table_data(table_name)
    new_id = max((record[ID_COLUMN] for record in table_data), default=0) + 1
    record = {ID_COLUMN: new_id}
    record.update(zip(columns, values))
    table_data.append(record)
    return table_data, new_id


def select(table_data, where_clause=None):
    """Возвращает все записи или только подходящие под условие where."""
    if not where_clause:
        return table_data
    return [record for record in table_data if matches(record, where_clause)]


def update(table_data, set_clause, where_clause):
    """Обновляет подходящие записи; возвращает (данные, список ID обновлённых)."""
    updated_ids = []
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
            updated_ids.append(record[ID_COLUMN])
    return table_data, updated_ids


def delete(table_data, where_clause):
    """Удаляет подходящие записи; возвращает (данные, список ID удалённых)."""
    deleted_ids = [r[ID_COLUMN] for r in table_data if matches(r, where_clause)]
    remaining = [r for r in table_data if not matches(r, where_clause)]
    return remaining, deleted_ids


def info(metadata, table_name, table_data):
    """Печатает схему таблицы и количество записей."""
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {format_schema(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")
