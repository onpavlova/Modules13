
import unittest
import tempfile
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.contact import Contact
from model.phonebook import PhoneBook
from model.file_handler import FileHandler
from exceptions import ContactNotFoundError, FileOperationError


class TestContact(unittest.TestCase):
    """Тесты для класса Contact"""

    def test_contact_creation(self):
        """Тест создания контакта"""
        contact = Contact("Иван Иванов", "+79123456789", "Коллега")
        self.assertEqual(contact.name, "Иван Иванов")
        self.assertEqual(contact.phone, "+79123456789")
        self.assertEqual(contact.comment, "Коллега")
        self.assertIsNone(contact.id)

    def test_contact_creation_with_id(self):
        """Тест создания контакта с ID"""
        contact = Contact("Иван Иванов", "+79123456789", "Коллега", id=5)
        self.assertEqual(contact.id, 5)

    def test_contact_to_list(self):
        """Тест преобразования контакта в список"""
        contact = Contact("Иван Иванов", "+79123456789", "Коллега")
        result = contact.to_list()
        self.assertEqual(result, ["Иван Иванов", "+79123456789", "Коллега"])
        self.assertEqual(len(result), 3)

    def test_contact_to_string(self):
        """Тест преобразования контакта в строку"""
        contact = Contact("Иван Иванов", "+79123456789", "Коллега")
        result = contact.to_string()
        self.assertEqual(result, "Иван Иванов;+79123456789;Коллега")

    def test_contact_from_list(self):
        """Тест создания контакта из списка"""
        contact = Contact.from_list(["Иван Иванов", "+79123456789", "Коллега"])
        self.assertEqual(contact.name, "Иван Иванов")
        self.assertEqual(contact.phone, "+79123456789")
        self.assertEqual(contact.comment, "Коллега")

    def test_contact_from_list_with_id(self):
        """Тест создания контакта из списка с ID"""
        contact = Contact.from_list(["Иван Иванов", "+79123456789", "Коллега"], contact_id=5)
        self.assertEqual(contact.name, "Иван Иванов")
        self.assertEqual(contact.id, 5)

    def test_contact_from_list_invalid_data(self):
        """Тест создания контакта из неверного списка"""
        with self.assertRaises(ValueError):
            Contact.from_list(["Только имя"])  # Недостаточно элементов

    def test_contact_str_representation(self):
        """Тест строкового представления контакта"""
        contact = Contact("Иван Иванов", "+79123456789", "Коллега")
        self.assertEqual(str(contact), "Иван Иванов: +79123456789 (Коллега)")


class TestPhoneBook(unittest.TestCase):
    """Тесты для класса PhoneBook"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.phonebook = PhoneBook()
        self.contact1 = Contact("Иван Иванов", "+79123456789", "Коллега")
        self.contact2 = Contact("Мария Петрова", "+79987654321", "Подруга")
        self.contact3 = Contact("Алексей Сидоров", "+79555555555", "Друг")

    def test_initial_state(self):
        """Тест начального состояния телефонной книги"""
        self.assertFalse(self.phonebook.is_open)
        self.assertIsNone(self.phonebook.file_path)
        self.assertEqual(len(self.phonebook), 0)

    def test_add_contact(self):
        """Тест добавления контакта"""
        contact_id = self.phonebook.add_contact(self.contact1)
        self.assertEqual(contact_id, 1)
        self.assertEqual(len(self.phonebook), 1)
        self.assertEqual(self.contact1.id, 1)

    def test_add_multiple_contacts(self):
        """Тест добавления нескольких контактов"""
        id1 = self.phonebook.add_contact(self.contact1)
        id2 = self.phonebook.add_contact(self.contact2)

        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)
        self.assertEqual(len(self.phonebook), 2)

    def test_get_contact(self):
        """Тест получения контакта по ID"""
        contact_id = self.phonebook.add_contact(self.contact1)
        retrieved_contact = self.phonebook.get_contact(contact_id)

        self.assertEqual(retrieved_contact.name, self.contact1.name)
        self.assertEqual(retrieved_contact.phone, self.contact1.phone)
        self.assertEqual(retrieved_contact.comment, self.contact1.comment)

    def test_get_nonexistent_contact(self):
        """Тест получения несуществующего контакта"""
        with self.assertRaises(ContactNotFoundError):
            self.phonebook.get_contact(999)

    def test_get_all_contacts(self):
        """Тест получения всех контактов"""
        self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)

        contacts = self.phonebook.get_all_contacts()
        self.assertEqual(len(contacts), 2)
        self.assertIn(1, contacts)
        self.assertIn(2, contacts)

    def test_find_contacts_by_name(self):
        """Тест поиска контактов по имени"""
        self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)
        self.phonebook.add_contact(self.contact3)

        # Поиск по полному имени
        results = self.phonebook.find_contacts("Иван")
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results.values())[0].name, "Иван Иванов")

        # Поиск по части имени (регистр не важен)
        results = self.phonebook.find_contacts("иван")
        self.assertEqual(len(results), 1)

    def test_find_contacts_by_phone(self):
        """Тест поиска контактов по телефону"""
        self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)

        results = self.phonebook.find_contacts("234567")
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results.values())[0].phone, "+79123456789")

    def test_find_contacts_by_comment(self):
        """Тест поиска контактов по комментарию"""
        self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)

        results = self.phonebook.find_contacts("Коллега")
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results.values())[0].comment, "Коллега")

    def test_find_nonexistent_contact(self):
        """Тест поиска несуществующего контакта"""
        self.phonebook.add_contact(self.contact1)
        results = self.phonebook.find_contacts("НетТакогоКонтакта")
        self.assertEqual(len(results), 0)

    def test_update_contact(self):
        """Тест обновления контакта"""
        contact_id = self.phonebook.add_contact(self.contact1)

        updated_contact = self.phonebook.update_contact(
            contact_id,
            name="Иван Петров",
            phone="+79999999999"
        )

        self.assertEqual(updated_contact.name, "Иван Петров")
        self.assertEqual(updated_contact.phone, "+79999999999")
        self.assertEqual(updated_contact.comment, "Коллега")  # Не изменялся

    def test_update_contact_partial(self):
        """Тест частичного обновления контакта"""
        contact_id = self.phonebook.add_contact(self.contact1)

        # Обновляем только имя
        updated_contact = self.phonebook.update_contact(
            contact_id,
            name="Новое Имя"
        )

        self.assertEqual(updated_contact.name, "Новое Имя")
        self.assertEqual(updated_contact.phone, "+79123456789")  # Не изменялся
        self.assertEqual(updated_contact.comment, "Коллега")  # Не изменялся

    def test_update_nonexistent_contact(self):
        """Тест обновления несуществующего контакта"""
        with self.assertRaises(ContactNotFoundError):
            self.phonebook.update_contact(999, name="Новое имя")

    def test_delete_contact(self):
        """Тест удаления контакта"""
        contact_id = self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)

        deleted_contact = self.phonebook.delete_contact(contact_id)

        self.assertEqual(deleted_contact.name, "Иван Иванов")
        self.assertEqual(len(self.phonebook), 1)  # Остался один контакт

    def test_delete_nonexistent_contact(self):
        """Тест удаления несуществующего контакта"""
        with self.assertRaises(ContactNotFoundError):
            self.phonebook.delete_contact(999)

    def test_iteration(self):
        """Тест итерации по телефонной книге"""
        self.phonebook.add_contact(self.contact1)
        self.phonebook.add_contact(self.contact2)

        contacts = list(self.phonebook)
        self.assertEqual(len(contacts), 2)

    @patch('model.phonebook.FileHandler')
    def test_open_file_success(self, mock_file_handler):
        """Тест успешного открытия файла"""
        # Настраиваем mock
        mock_instance = MagicMock()
        mock_instance.load.return_value = {
            1: ["Иван Иванов", "+79123456789", "Коллега"],
            2: ["Мария Петрова", "+79987654321", "Подруга"]
        }
        mock_file_handler.return_value = mock_instance

        # Создаем новый phonebook с mock
        with patch.object(self.phonebook, '_file_handler', mock_instance):
            result = self.phonebook.open("test_file.txt")

        self.assertTrue(result)
        self.assertTrue(self.phonebook.is_open)
        self.assertEqual(self.phonebook.file_path, "test_file.txt")
        self.assertEqual(len(self.phonebook), 2)

    @patch('model.phonebook.FileHandler')
    def test_open_file_failure(self, mock_file_handler):
        """Тест неудачного открытия файла"""
        # Настраиваем mock для выброса исключения
        mock_instance = MagicMock()
        mock_instance.load.side_effect = FileOperationError("Ошибка чтения", "test_file.txt")
        mock_file_handler.return_value = mock_instance

        with patch.object(self.phonebook, '_file_handler', mock_instance):
            with self.assertRaises(FileOperationError):
                self.phonebook.open("test_file.txt")

        self.assertFalse(self.phonebook.is_open)
        self.assertEqual(len(self.phonebook), 0)

    @patch('model.phonebook.FileHandler')
    def test_save_file(self, mock_file_handler):
        """Тест сохранения файла"""
        # Настраиваем mock
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        with patch.object(self.phonebook, '_file_handler', mock_instance):
            self.phonebook._contacts = {
                1: Contact("Иван Иванов", "+79123456789", "Коллега", id=1)
            }
            self.phonebook._is_open = True
            self.phonebook._file_path = "test_file.txt"

            self.phonebook.save()

            # Проверяем, что save был вызван с правильными аргументами
            mock_instance.save.assert_called_once_with(
                "test_file.txt",
                {1: ["Иван Иванов", "+79123456789", "Коллега"]}
            )

    def test_next_id_generation(self):
        """Тест генерации следующего ID"""
        self.assertEqual(self.phonebook._get_next_id(), 1)

        self.phonebook.add_contact(self.contact1)
        self.assertEqual(self.phonebook._get_next_id(), 2)

        self.phonebook.add_contact(self.contact2)
        self.assertEqual(self.phonebook._get_next_id(), 3)

        # Удаляем контакт и проверяем, что ID продолжает увеличиваться
        self.phonebook.delete_contact(1)
        self.assertEqual(self.phonebook._get_next_id(), 3)


class TestFileHandler(unittest.TestCase):
    """Тесты для класса FileHandler"""

    def setUp(self):
        self.file_handler = FileHandler()
        self.test_data = {
            1: ["Иван Иванов", "+79123456789", "Коллега"],
            2: ["Мария Петрова", "+79987654321", "Подруга"]
        }

    def test_load_valid_file(self):
        """Тест загрузки корректного файла"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Иван Иванов;+79123456789;Коллега\n")
            f.write("Мария Петрова;+79987654321;Подруга\n")
            temp_path = f.name

        try:
            result = self.file_handler.load(temp_path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[1], ["Иван Иванов", "+79123456789", "Коллега"])
            self.assertEqual(result[2], ["Мария Петрова", "+79987654321", "Подруга"])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_empty_file(self):
        """Тест загрузки пустого файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            result = self.file_handler.load(temp_path)
            self.assertEqual(len(result), 0)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Тест загрузки несуществующего файла"""
        with self.assertRaises(FileOperationError):
            self.file_handler.load("nonexistent_file.txt")

    def test_save_file(self):
        """Тест сохранения файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            self.file_handler.save(temp_path, self.test_data)

            # Проверяем, что файл был создан и содержит правильные данные
            self.assertTrue(os.path.exists(temp_path))

            with open(temp_path, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')

            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0], "Иван Иванов;+79123456789;Коллега")
            self.assertEqual(lines[1], "Мария Петрова;+79987654321;Подруга")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_empty_data(self):
        """Тест сохранения пустых данных"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            self.file_handler.save(temp_path, {})

            self.assertTrue(os.path.exists(temp_path))

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertEqual(content, "")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_file_exists(self):
        """Тест проверки существования файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            self.assertTrue(self.file_handler.file_exists(temp_path))
            self.assertFalse(self.file_handler.file_exists("nonexistent_file.txt"))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_is_writable(self):
        """Тест проверки возможности записи"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            self.assertTrue(self.file_handler.is_writable(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestParameterizedContacts(unittest.TestCase):
    """Параметризованные тесты для контактов"""

    def test_contact_parameterized_names(self):
        """Параметризованный тест имен контактов"""
        test_cases = [
            ("Иван Иванов", "+79123456789", "Друг"),
            ("Анна-Мария Петрова-Сидорова", "+79987654321", "Коллега"),
            ("John Doe", "+1234567890", "Friend"),
            ("O'Connor", "+44123456789", "Relative"),
            ("Имя с пробелами", "+71234567890", "Тестовый контакт"),
        ]

        for name, phone, comment in test_cases:
            with self.subTest(name=name, phone=phone, comment=comment):
                contact = Contact(name, phone, comment)
                self.assertEqual(contact.name, name)
                self.assertEqual(contact.phone, phone)
                self.assertEqual(contact.comment, comment)

    def test_contact_parameterized_phones(self):
        """Параметризованный тест телефонов контактов"""
        test_cases = [
            ("+79123456789", "Стандартный формат"),
            ("8-916-123-45-67", "С дефисами"),
            ("(495) 123-45-67", "Со скобками"),
            ("+7 916 123 45 67", "С пробелами"),
            ("1234567", "Короткий номер"),
            ("+1-800-123-4567", "Международный"),
        ]

        for phone, description in test_cases:
            with self.subTest(phone=phone, description=description):
                contact = Contact("Тест", phone, description)
                self.assertEqual(contact.phone, phone)

    def test_find_parameterized_search(self):
        """Параметризованный тест поиска"""
        phonebook = PhoneBook()
        phonebook.add_contact(Contact("Иван Иванов", "+79123456789", "Коллега"))
        phonebook.add_contact(Contact("Мария Петрова", "+79987654321", "Подруга"))
        phonebook.add_contact(Contact("Алексей Сидоров", "+79555555555", "Друг"))

        test_cases = [
            ("Иван", 1, "Поиск по имени"),
            ("петрова", 1, "Поиск по фамилии (регистр)"),
            ("+7912345", 1, "Поиск по части телефона"),
            ("коллега", 1, "Поиск по комментарию"),
            ("Алексей Сидоров", 1, "Поиск по полному имени"),
            ("нет", 0, "Поиск несуществующего"),
            ("", 3, "Пустой поисковой запрос"),
            (" ", 3, "Поиск по пробелу"),
        ]

        for search_term, expected_count, description in test_cases:
            with self.subTest(search_term=search_term, description=description):
                results = phonebook.find_contacts(search_term)
                self.assertEqual(len(results), expected_count, description)


class TestBoundaryConditions(unittest.TestCase):
    """Тесты граничных условий"""

    def setUp(self):
        self.phonebook = PhoneBook()

    def test_add_empty_contact_fields(self):
        """Тест добавления контакта с пустыми полями"""
        # Пустое имя допустимо
        contact = Contact("", "+79123456789", "Без имени")
        contact_id = self.phonebook.add_contact(contact)
        self.assertEqual(contact_id, 1)

        # Пустой телефон допустим
        contact2 = Contact("Иван", "", "Без телефона")
        contact_id2 = self.phonebook.add_contact(contact2)
        self.assertEqual(contact_id2, 2)

        # Пустой комментарий допустим
        contact3 = Contact("Мария", "+79987654321", "")
        contact_id3 = self.phonebook.add_contact(contact3)
        self.assertEqual(contact_id3, 3)

        self.assertEqual(len(self.phonebook), 3)

    def test_add_contact_with_whitespace(self):
        """Тест добавления контакта с пробельными символами"""
        contact = Contact("  Иван  ", "  +79123456789  ", "  Коллега  ")
        contact_id = self.phonebook.add_contact(contact)

        retrieved = self.phonebook.get_contact(contact_id)
        self.assertEqual(retrieved.name, "  Иван  ")  # Пробелы сохраняются
        self.assertEqual(retrieved.phone, "  +79123456789  ")
        self.assertEqual(retrieved.comment, "  Коллега  ")

    def test_search_boundary_conditions(self):
        """Тест граничных условий поиска"""
        phonebook = PhoneBook()

        # Проверка поиска в пустой книге
        results = phonebook.find_contacts("любой запрос")
        self.assertEqual(len(results), 0)

        # Проверка поиска очень длинного запроса
        long_query = "a" * 1000
        results = phonebook.find_contacts(long_query)
        self.assertEqual(len(results), 0)

        # Добавляем контакт и проверяем специальные символы
        phonebook.add_contact(Contact("Test@Name", "+123", "Comment#123"))

        results = phonebook.find_contacts("@")
        self.assertEqual(len(results), 1)

        results = phonebook.find_contacts("#")
        self.assertEqual(len(results), 1)

    def test_unicode_and_special_characters(self):
        """Тест Unicode и специальных символов"""
        test_cases = [
            ("Имя с ёлка", "+79123456789", "Комментарий с Ё"),
            ("Emoji 😊", "+79987654321", "Смайлик в имени"),
            ("Name with\nnewline", "+79111111111", "Comment"),
            ("Табуляция\tтест", "+79222222222", "Tab"),
        ]

        for name, phone, comment in test_cases:
            with self.subTest(name=name):
                contact = Contact(name, phone, comment)
                contact_list = contact.to_list()
                contact_str = contact.to_string()

                # Проверяем, что преобразования работают
                self.assertEqual(len(contact_list), 3)
                self.assertIn(name, contact_str)
                self.assertIn(phone, contact_str)
                self.assertIn(comment, contact_str)


if __name__ == '__main__':
    unittest.main()