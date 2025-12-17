import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.phonebook_controller import PhoneBookController
from exceptions import ContactNotFoundError, FileOperationError
import text


class TestPhoneBookController(unittest.TestCase):
    """Интеграционные тесты контроллера"""

    def setUp(self):
        self.controller = PhoneBookController()

    def test_initial_state(self):
        """Тест начального состояния контроллера"""
        self.assertIsNotNone(self.controller.phone_book)
        self.assertIsNotNone(self.controller.view)
        self.assertIsNone(self.controller._current_file_path)

    @patch('controller.phonebook_controller.ConsoleView.get_input')
    def test_open_file_success_integration(self, mock_get_input):
        """Интеграционный тест успешного открытия файла"""
        # Настраиваем моки
        mock_get_input.return_value = "test_file.txt"

        with patch.object(self.controller.phone_book, 'open') as mock_open:
            mock_open.return_value = True
            with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
                self.controller._open_file()

                # Проверяем вызовы
                mock_get_input.assert_called_once_with(text.input_path_message)
                mock_open.assert_called_once_with("test_file.txt")
                mock_show.assert_called_once_with(text.phone_book_load_successful)

    @patch('controller.phonebook_controller.ConsoleView.get_input')
    def test_save_file_integration(self, mock_get_input):
        """Интеграционный тест сохранения файла"""
        # Настраиваем, что книга открыта
        self.controller.phone_book._is_open = True
        self.controller._current_file_path = "test_file.txt"

        with patch.object(self.controller.phone_book, 'save') as mock_save:
            with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
                self.controller._save_file()

                # Проверяем вызовы
                mock_save.assert_called_once_with("test_file.txt")
                mock_show.assert_called_once_with(text.phone_book_save_successful)
                mock_get_input.assert_not_called()

    @patch('controller.phonebook_controller.ConsoleView.get_multiple_input')
    def test_add_contact_integration(self, mock_get_input):
        """Интеграционный тест добавления контакта"""
        # Настраиваем моки
        mock_get_input.return_value = ["Иван Иванов", "+79123456789", "Коллега"]

        # Устанавливаем, что файл открыт
        self.controller.phone_book._is_open = True

        with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
            with patch.object(self.controller.phone_book, 'add_contact') as mock_add:
                mock_add.return_value = 1

                self.controller._add_contact()

                # Проверяем вызовы
                mock_get_input.assert_called_once_with(text.input_new_contact)
                mock_add.assert_called_once()

                # Упрощенная проверка - просто проверяем, что было сообщение
                self.assertTrue(mock_show.called)

    @patch('controller.phonebook_controller.ConsoleView.get_input')
    def test_find_contacts_integration(self, mock_get_input):
        """Интеграционный тест поиска контактов"""
        # Настраиваем моки
        mock_get_input.return_value = "Иван"

        # Устанавливаем, что файл открыт
        self.controller.phone_book._is_open = True

        # Создаем mock результат поиска
        mock_contact = MagicMock()
        mock_contact.name = "Иван Иванов"
        mock_contact.phone = "+79123456789"
        mock_contact.comment = "Коллега"

        with patch('controller.phonebook_controller.ConsoleView.show_contacts') as mock_show_contacts:
            with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show_message:
                with patch.object(self.controller.phone_book, 'find_contacts') as mock_find:
                    mock_find.return_value = {1: mock_contact}

                    self.controller._find_contacts()

                    # Проверяем вызовы
                    mock_get_input.assert_called_once_with(text.input_word_to_find)
                    mock_find.assert_called_once_with("Иван")
                    mock_show_contacts.assert_called_once()
                    mock_show_message.assert_called_once_with("Найдено контактов: 1")


class TestErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок"""

    def setUp(self):
        self.controller = PhoneBookController()

    @patch('controller.phonebook_controller.ConsoleView.get_input')
    def test_open_file_not_found(self, mock_get_input):
        """Тест открытия несуществующего файла"""
        mock_get_input.return_value = "nonexistent.txt"

        with patch.object(self.controller.phone_book, 'open') as mock_open:
            mock_open.side_effect = FileOperationError("Файл не найден: nonexistent.txt")

            with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
                self.controller._open_file()

                # Проверяем, что сообщение об ошибке было показано
                mock_show.assert_called()
                # Проверяем, что в сообщении есть информация об ошибке
                call_args = mock_show.call_args[0][0]
                self.assertIn("Ошибка при открытии файла", call_args)
                self.assertIn("nonexistent.txt", call_args)

    def test_save_file_without_path(self):
        """Тест сохранения без указанного пути"""
        # Не устанавливаем путь
        self.controller._current_file_path = None

        with patch('controller.phonebook_controller.ConsoleView.get_input') as mock_get_input:
            mock_get_input.return_value = "new_file.txt"

            with patch.object(self.controller.phone_book, 'save') as mock_save:
                with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
                    self.controller._save_file()

                    mock_get_input.assert_called_once_with("Введите путь для сохранения файла: ")
                    mock_save.assert_called_once_with("new_file.txt")
                    mock_show.assert_called_once_with(text.phone_book_save_successful)

    @patch('controller.phonebook_controller.ConsoleView.get_input')
    def test_edit_nonexistent_contact(self, mock_get_input):
        """Тест редактирования несуществующего контакта"""
        mock_get_input.side_effect = ["999", "", "", ""]  # Несуществующий ID

        # Устанавливаем, что файл открыт
        self.controller.phone_book._is_open = True

        with patch.object(self.controller.phone_book, 'get_contact') as mock_get:
            mock_get.side_effect = ContactNotFoundError(contact_id=999)

            with patch('controller.phonebook_controller.ConsoleView.show_message') as mock_show:
                self.controller._edit_contact()

                # Проверяем, что сообщение об ошибке было показано
                mock_show.assert_called()
                call_args = mock_show.call_args[0][0]
                self.assertIn("не найден", call_args)
                self.assertIn("999", call_args)


class TestConsoleView(unittest.TestCase):
    """Тесты консольного представления"""

    def test_show_menu(self):
        """Тест отображения меню"""
        from view.console_view import ConsoleView

        with patch('builtins.print') as mock_print:
            ConsoleView.show_menu()

            # Проверяем, что print был вызван несколько раз
            self.assertGreater(mock_print.call_count, 0)

    @patch('builtins.input')
    def test_get_user_choice_valid(self, mock_input):
        """Тест получения корректного выбора пользователя"""
        from view.console_view import ConsoleView

        mock_input.return_value = "1"

        choice = ConsoleView.get_user_choice()

        self.assertEqual(choice, 1)
        mock_input.assert_called_once_with(text.user_menu_choice)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_choice_invalid_then_valid(self, mock_print, mock_input):
        """Тест получения неверного, затем корректного выбора"""
        from view.console_view import ConsoleView

        # Сначала неверный ввод, затем верный
        mock_input.side_effect = ["invalid", "10", "5"]

        choice = ConsoleView.get_user_choice()

        self.assertEqual(choice, 5)
        self.assertEqual(mock_input.call_count, 3)
        self.assertEqual(mock_print.call_count, 2)  # Два сообщения об ошибке

    def test_show_contacts_empty(self):
        """Тест отображения пустого списка контактов"""
        from view.console_view import ConsoleView

        with patch('builtins.print') as mock_print:
            ConsoleView.show_contacts({}, "Телефонная книга пуста")

            mock_print.assert_called_with("Телефонная книга пуста")


if __name__ == '__main__':
    unittest.main()