"""Вспомогательные функции для работы с файлами."""

import json
import os

from primitive_db.constants import DATA_DIR, DATA_FILE_EXTENSION


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла; если файла нет, возвращает {}."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_path(table_name):
    """Возвращает путь к файлу с данными таблицы."""
    return os.path.join(DATA_DIR, table_name + DATA_FILE_EXTENSION)


def load_table_data(table_name):
    """Загружает записи таблицы; если файла нет, возвращает []."""
    try:
        with open(get_table_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы, создавая папку data при необходимости."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он существует."""
    path = get_table_path(table_name)
    if os.path.exists(path):
        os.remove(path)


def get_table_version(table_name):
    """Возвращает время последнего изменения файла таблицы (для кэша)."""
    path = get_table_path(table_name)
    if not os.path.exists(path):
        return None
    return os.path.getmtime(path)
