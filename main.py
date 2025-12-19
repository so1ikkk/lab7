import sys
import functools
import logging
import requests
import math
from typing import List, Dict, Optional, Tuple

# 1. Декоратор logger
""" Универсальный логирующий декоратор.

    Логирует старт, завершение и ошибки функции.
    Поддерживает логирование в sys.stdout или logging.Logger.

    Args:
        func (callable): Функция для оборачивания.
        handle (sys.stdout или logging.Logger): Куда писать логи.
    """
def logger(func=None, *, handle=sys.stdout):
    if func is None:
        return lambda f: logger(f, handle=handle)

    is_logger = isinstance(handle, logging.Logger)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        msg_start = f"START {func.__name__} args={args}, kwargs={kwargs}"
        if is_logger:
            handle.info(msg_start)
        else:
            handle.write(msg_start + "\n")

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            msg_err = f"ERROR in {func.__name__}: {type(e).__name__}: {e}"
            if is_logger:
                handle.error(msg_err)
            else:
                handle.write(msg_err + "\n")
            raise

        msg_end = f"END {func.__name__} result={result}"
        if is_logger:
            handle.info(msg_end)
        else:
            handle.write(msg_end + "\n")

        return result

    return wrapper


# 2. Функция get_currencies
def get_currencies(currency_codes: list,url: str = "https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    """Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (List[str]): Список символьных кодов валют (например, ['USD', 'EUR']).
        url (str, optional): URL API. По умолчанию 'https://www.cbr-xml-daily.ru/daily_json.js'.

    Returns:
        Dict[str, float]: Словарь с курсами валют.

    Raises:
        ConnectionError: Если API недоступен.
        ValueError: Если JSON некорректный.
        KeyError: Если отсутствуют ожидаемые ключи в данных.
        TypeError: Если курс валюты имеет неверный тип.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError("API недоступен") from e

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError("Некорректный JSON") from e

    if "Valute" not in data:
        raise KeyError("Нет ключа 'Valute'")

    result = {}

    for code in currency_codes:
        if code not in data["Valute"]:
            raise KeyError(f"Валюта {code} отсутствует в данных")

        value = data["Valute"][code].get("Value")

        if not isinstance(value, (int, float)):
            raise TypeError(f"Курс валюты {code} имеет неверный тип")

        result[code] = value

    return result

# 3. Использование с логированием
@logger(handle=sys.stdout)
def get_currencies_logged(currency_codes, url='https://www.cbr-xml-daily.ru/daily_json.js'):
    return get_currencies(currency_codes, url=url)


if __name__ == "__main__":
    currencies = ["USD", "EUR", "GBP", "AUD"]

    try:
        data = get_currencies_logged(currencies)
        print("Результат:", data)
    except Exception as e:
        print("Ошибка:", e)


# 4. Логирование в файл
file_logger = logging.getLogger("currency_file")
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("currency.log", encoding="utf-8")
file_logger.addHandler(file_handler)

@logger(handle=file_logger)
def get_currencies_file(currency_codes, url='https://www.cbr-xml-daily.ru/daily_json.js'):
    return get_currencies(currency_codes, url=url)

try:
    get_currencies_file(currencies)
except Exception:
    pass

# Функция solve_quadratic
logging.basicConfig(
    filename="quadratic.log",
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s"
)

quad_logger = logging.getLogger("quadratic")

@logger(handle=quad_logger)
def solve_quadratic(a: float, b: float, c: float) -> Optional[Tuple[float, ...]]:
    """Решает квадратное уравнение ax^2 + bx + c = 0 с логированием.

    Args:
        a (float): Коэффициент при x^2.
        b (float): Коэффициент при x.
        c (float): Свободный член.

    Returns:
        Optional[Tuple[float, ...]]: Кортеж с корнями (1 или 2) или None, если корней нет.

    Raises:
        TypeError: Если коэффициенты некорректного типа.
        ValueError: Если уравнение невозможно (a=b=0).
    """
    # ERROR — некорректные данные
    for name, value in zip(("a", "b", "c"), (a, b, c)):
        if not isinstance(value, (int, float)):
            quad_logger.error(f"Invalid type for '{name}': {value}")
            raise TypeError(f"Coefficient '{name}' must be numeric")

    # CRITICAL — полностью невозможная ситуация
    if a == 0 and b == 0:
        quad_logger.critical("Impossible equation: a = 0 and b = 0")
        raise ValueError("Invalid quadratic equation")

    d = b * b - 4 * a * c
    quad_logger.debug(f"Discriminant = {d}")

    # WARNING — нет действительных корней
    if d < 0:
        quad_logger.warning("Discriminant < 0: no real roots")
        return None

    # Один корень
    if d == 0:
        x = -b / (2 * a)
        quad_logger.info("One real root")
        return (x,)

    # INFO — два корня
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)
    quad_logger.info("Two real roots computed")
    return x1, x2


# -----------------------
# 4. Демонстрация
# -----------------------
if __name__ == "__main__":
    # INFO — два корня
    solve_quadratic(1, -3, 2)

    # WARNING — дискриминант < 0
    solve_quadratic(1, 1, 10)

    # ERROR — некорректные данные
    try:
        solve_quadratic("abc", 2, 3)
    except Exception:
        pass

    # CRITICAL — невозможная ситуация
    try:
        solve_quadratic(0, 0, 5)
    except Exception:
        pass
