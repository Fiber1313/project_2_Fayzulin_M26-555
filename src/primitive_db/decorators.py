"""Декораторы и замыкание для кэширования."""

import time

import prompt

from primitive_db.constants import CONFIRM_ANSWER, TIME_PRECISION


def copy_function_info(wrapper, func):
    """Переносит имя и docstring исходной функции на обёртку."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Перехватывает ошибки работы с базой и печатает понятное сообщение."""

    def wrapper(*args, **kwargs):
        """Вызывает функцию и перехватывает ошибки."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return copy_function_info(wrapper, func)


def confirm_action(action_name):
    """Фабрика декораторов: спрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        """Оборачивает функцию запросом подтверждения."""
        def wrapper(*args, **kwargs):
            """Спрашивает подтверждение и вызывает функцию при ответе y."""
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return copy_function_info(wrapper, func)

    return decorator


def log_time(func):
    """Замеряет и печатает время выполнения функции."""

    def wrapper(*args, **kwargs):
        """Вызывает функцию и печатает время её выполнения."""
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(
            f"Функция {func.__name__} выполнилась за "
            f"{elapsed:.{TIME_PRECISION}f} секунд."
        )
        return result

    return copy_function_info(wrapper, func)


def create_cacher():
    """Возвращает функцию cache_result, которая хранит кэш в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key in cache:
            return cache[key]
        result = value_func()
        if result is not None:
            cache[key] = result
        return result

    return cache_result
