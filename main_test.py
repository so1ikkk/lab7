from main import *
import unittest
import io


class TestGetCurrencies(unittest.TestCase):
    """Тесты для функции get_currencies."""
    def test_real_currencies(self):
        """Проверка возврата корректных курсов валют."""
        result = get_currencies(["USD", "EUR"])
        self.assertIn("USD", result)
        self.assertIn("EUR", result)
        self.assertIsInstance(result["USD"], (int, float))

    def test_missing_currency(self):
        """Проверка ошибки при несуществующей валюте."""
        with self.assertRaises(KeyError):
            get_currencies(["XXX"])

    def test_connection_error(self):
        """Проверка ошибки ConnectionError при недоступном API."""
        with self.assertRaises(ConnectionError):
            get_currencies(["USD"], url="https://invalid")

    def test_invalid_json(self):
        """Проверка ValueError при некорректном JSON."""
        with self.assertRaises(ValueError):
            get_currencies(["USD"], url="https://httpbin.org/html")

class TestLoggerDecorator(unittest.TestCase):
    """Тесты для логирующего декоратора logger."""
    def setUp(self):
        """Создание потока для перехвата логов."""
        self.stream = io.StringIO()

    def test_success_logging(self):
        """Проверка логов при успешном выполнении функции."""
        @logger(handle=self.stream)
        def test_func(x):
            """Функция для тестирования."""
            return x * 2

        result = test_func(4)
        logs = self.stream.getvalue()

        self.assertEqual(result, 8)
        self.assertIn("START test_func", logs)
        self.assertIn("END test_func result=8", logs)

    def test_error_logging(self):
        """Проверка логов и проброса исключения при ошибке."""
        @logger(handle=self.stream)
        def test_func(x):
            """Функция, вызывающая исключение."""
            raise ValueError("boom")

        with self.assertRaises(ValueError):
            test_func(1)

        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)

class TestStreamWrite(unittest.TestCase):
    """Пример теста с использованием контекста и StringIO."""
    def setUp(self):
        self.stream = io.StringIO()

        @logger(handle=self.stream)
        def wrapped():
            """Функция, вызывающая ConnectionError."""
            return get_currencies(['USD'], url="https://invalid")

        self.wrapped = wrapped

    def test_logging_error(self):
        """Проверка логирования ошибки при недоступном API."""
        with self.assertRaises(ConnectionError):
            self.wrapped()

        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)

if __name__ == "__main__":
    unittest.main()