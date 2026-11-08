"""Главный цикл программы и обработка команд."""

import shlex

import prompt

from primitive_db.constants import HELP_TEXT, INPUT_PROMPT, META_FILE
from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
    print_invalid_value,
)
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Печатает справку по командам."""
    print(HELP_TEXT)


def run():
    """Запускает основной цикл работы с базой данных."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(INPUT_PROMPT)

        try:
            args = shlex.split(user_input)
        except ValueError:
            print_invalid_value(user_input)
            continue
        if not args:
            continue

        command, params = args[0], args[1:]
        match command:
            case "create_table":
                if len(params) < 2:
                    print_invalid_value(user_input)
                    continue
                metadata = create_table(metadata, params[0], params[1:])
                save_metadata(META_FILE, metadata)
            case "drop_table":
                if len(params) != 1:
                    print_invalid_value(user_input)
                    continue
                metadata = drop_table(metadata, params[0])
                save_metadata(META_FILE, metadata)
            case "list_tables":
                list_tables(metadata)
            case "help":
                print_help()
            case "exit":
                return
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
