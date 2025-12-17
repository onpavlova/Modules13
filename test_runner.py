
import unittest
import sys
import os


def run_all_tests():
    """Запуск всех тестов"""
    # Добавляем текущую директорию в путь
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # Загружаем тесты
    loader = unittest.TestLoader()

    # Находим все тестовые файлы
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Возвращаем код выхода
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 70)
    print("Запуск всех тестов телефонного справочника")
    print("=" * 70)

    exit_code = run_all_tests()

    print("=" * 70)
    print("Тестирование завершено")
    print("=" * 70)

    sys.exit(exit_code)