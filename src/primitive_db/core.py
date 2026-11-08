"""Основная логика работы с таблицами."""

from primitive_db.constants import COLUMN_SEPARATOR, ID_COLUMN, ID_TYPE, VALID_TYPES


def print_invalid_value(value):
    """Печатает сообщение о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def parse_column(column):
    """Разбирает строку вида 'имя:тип' в пару (имя, тип) или возвращает None."""
    parts = column.split(COLUMN_SEPARATOR)
    if len(parts) != 2:
        return None
    name, column_type = parts
    if not name or name == ID_COLUMN or column_type not in VALID_TYPES:
        return None
    return name, column_type


def create_table(metadata, table_name, columns):
    """Создаёт таблицу с автоматическим столбцом ID и возвращает метаданные."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        parsed = parse_column(column)
        if parsed is None or parsed[0] in schema:
            print_invalid_value(column)
            return metadata
        name, column_type = parsed
        schema[name] = column_type

    metadata[table_name] = schema
    columns_text = ", ".join(f"{name}:{kind}" for name, kind in schema.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает обновлённые метаданные."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Печатает список всех таблиц."""
    for table_name in metadata:
        print(f"- {table_name}")
