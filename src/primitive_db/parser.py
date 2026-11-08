"""Разбор сложных частей команд: values, where и set."""

import shlex

from primitive_db.constants import (
    ASSIGNMENT_SIGN,
    FALSE_LITERAL,
    QUOTES,
    TRUE_LITERAL,
    VALUES_SEPARATOR,
)


def split_outside_quotes(text, separator):
    """Делит строку по разделителю, не трогая разделители внутри кавычек."""
    parts = []
    current = []
    open_quote = None
    for char in text:
        if open_quote:
            if char == open_quote:
                open_quote = None
        elif char in QUOTES:
            open_quote = char
        elif char == separator:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    if open_quote:
        raise ValueError(text)
    parts.append("".join(current))
    return [part.strip() for part in parts]


def parse_literal(token):
    """Превращает токен в значение Python: "строка" -> str, 28 -> int, true -> bool."""
    token = token.strip()
    if len(token) >= 2 and token[0] in QUOTES and token[-1] == token[0]:
        return token[1:-1]
    if token.lower() == TRUE_LITERAL:
        return True
    if token.lower() == FALSE_LITERAL:
        return False
    try:
        return int(token)
    except ValueError:
        raise ValueError(token) from None


def parse_values(text):
    """Разбирает '("Император", 3000, true)' в список ['Император', 3000, True]."""
    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)
    inner = text[1:-1]
    if not inner.strip():
        raise ValueError(text)
    tokens = split_outside_quotes(inner, VALUES_SEPARATOR)
    return [parse_literal(token) for token in tokens]


def parse_assignments(text):
    """Разбирает 'age = 28, name = "Anna"' в словарь {'age': 28, 'name': 'Anna'}."""
    result = {}
    for pair in split_outside_quotes(text, VALUES_SEPARATOR):
        parts = split_outside_quotes(pair, ASSIGNMENT_SIGN)
        if len(parts) != 2 or not parts[0]:
            raise ValueError(pair)
        column, value = parts
        result[column] = parse_literal(value)
    return result


def parse_where(text):
    """Разбирает условие where в словарь {столбец: значение}."""
    return parse_assignments(text)


def parse_set(text):
    """Разбирает часть set в словарь {столбец: новое_значение}."""
    return parse_assignments(text)


def split_by_keyword(text, keyword):
    """Делит строку по ключевому слову: возвращает (до, после) или (text, None)."""
    before, found, after = text.partition(keyword)
    if not found:
        return text.strip(), None
    return before.strip(), after.strip()


def split_params(text):
    """Делит аргументы команды на слова с учётом кавычек (через shlex)."""
    try:
        return shlex.split(text)
    except ValueError:
        raise ValueError(text) from None
