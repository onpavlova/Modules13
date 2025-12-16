
from typing import Dict, List, Optional, Iterator
from .contact import Contact
from .file_handler import FileHandler
from exceptions import ContactNotFoundError


class PhoneBook:
    """Класс для управления телефонной книгой"""

    def __init__(self):
        self._contacts: Dict[int, Contact] = {}
        self._file_handler = FileHandler()
        self._is_open = False
        self._file_path: Optional[str] = None

    @property
    def is_open(self) -> bool:
        """Проверка, открыта ли телефонная книга"""
        return self._is_open

    @property
    def file_path(self) -> Optional[str]:
        """Получение пути к файлу"""
        return self._file_path

    def open(self, file_path: str) -> bool:
        """Открытие телефонной книги из файла"""
        try:
            contacts_dict = self._file_handler.load(file_path)
            self._contacts = {}
            for contact_id, contact_data in contacts_dict.items():
                self._contacts[contact_id] = Contact.from_list(contact_data, contact_id)
            self._is_open = True
            self._file_path = file_path
            return True
        except Exception as e:
            self._is_open = False
            raise e

    def save(self, file_path: Optional[str] = None) -> None:
        """Сохранение телефонной книги в файл"""
        if not self._is_open:
            raise ValueError("Телефонная книга не открыта")

        save_path = file_path or self._file_path
        if not save_path:
            raise ValueError("Не указан путь для сохранения")

        contacts_dict = {cid: contact.to_list() for cid, contact in self._contacts.items()}
        self._file_handler.save(save_path, contacts_dict)

    def add_contact(self, contact: Contact) -> int:
        """Добавление нового контакта"""
        new_id = self._get_next_id()
        contact.id = new_id
        self._contacts[new_id] = contact
        return new_id

    def get_contact(self, contact_id: int) -> Contact:
        """Получение контакта по ID"""
        if contact_id not in self._contacts:
            raise ContactNotFoundError(contact_id=contact_id)
        return self._contacts[contact_id]

    def get_all_contacts(self) -> Dict[int, Contact]:
        """Получение всех контактов"""
        return self._contacts.copy()

    def find_contacts(self, search_term: str) -> Dict[int, Contact]:
        """Поиск контактов по всем полям"""
        result = {}
        search_term_lower = search_term.lower()

        for contact_id, contact in self._contacts.items():
            if (search_term_lower in contact.name.lower() or
                    search_term_lower in contact.phone.lower() or
                    search_term_lower in contact.comment.lower()):
                result[contact_id] = contact

        return result

    def update_contact(self, contact_id: int, **kwargs) -> Contact:
        """Обновление контакта"""
        if contact_id not in self._contacts:
            raise ContactNotFoundError(contact_id=contact_id)

        contact = self._contacts[contact_id]
        for key, value in kwargs.items():
            if hasattr(contact, key) and value:
                setattr(contact, key, value)

        return contact

    def delete_contact(self, contact_id: int) -> Contact:
        """Удаление контакта"""
        if contact_id not in self._contacts:
            raise ContactNotFoundError(contact_id=contact_id)

        return self._contacts.pop(contact_id)

    def __len__(self) -> int:
        return len(self._contacts)

    def __iter__(self) -> Iterator[Contact]:
        return iter(self._contacts.values())

    def _get_next_id(self) -> int:
        """Получение следующего ID для нового контакта"""
        if self._contacts:
            return max(self._contacts.keys()) + 1
        return 1