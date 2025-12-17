
from typing import Optional
from model.phonebook import PhoneBook
from model.contact import Contact
from view.console_view import ConsoleView
import text
from exceptions import PhoneBookError, FileOperationError, ContactNotFoundError


class PhoneBookController:
    """Контроллер для управления телефонной книгой"""

    def __init__(self):
        self.phone_book = PhoneBook()
        self.view = ConsoleView()
        self._current_file_path: Optional[str] = None  # Храним путь к текущему файлу

    def run(self) -> None:
        """Запуск основного цикла приложения"""
        try:
            while True:
                self.view.show_menu()
                choice = self.view.get_user_choice()
                self._handle_choice(choice)
        except KeyboardInterrupt:
            self.view.show_message("\nПрограмма завершена")
        except SystemExit:
            raise
        except Exception as e:
            self.view.show_message(f"Критическая ошибка: {str(e)}")

    def _handle_choice(self, choice: int) -> None:
        """Обработка выбора пользователя"""
        handlers = {
            1: self._open_file,
            2: self._save_file,
            3: self._show_all_contacts,
            4: self._add_contact,
            5: self._find_contacts,
            6: self._edit_contact,
            7: self._delete_contact,
            8: self._exit_program
        }

        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            self.view.show_message("Неверный выбор")

    def _open_file(self) -> None:
        """Открытие файла телефонной книги"""
        try:
            file_path = self.view.get_file_path()
            if self.phone_book.open(file_path):
                self._current_file_path = file_path  # Сохраняем путь
                self.view.show_message(text.phone_book_load_successful)
            else:
                self.view.show_message(text.phone_book_file_open_error)
        except FileOperationError as e:
            self.view.show_message(f"Ошибка при открытии файла: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Неизвестная ошибка: {str(e)}")

    def _save_file(self) -> None:
        """Сохранение телефонной книги"""
        try:
            # Если файл не был открыт, запрашиваем путь
            if not self.phone_book.is_open and not self._current_file_path:
                file_path = self.view.get_input("Введите путь для сохранения файла: ")
                self._current_file_path = file_path
                print(file_path+'if')

            # Сохраняем файл
            print(self._current_file_path)
            self.phone_book.save(self._current_file_path)
            self.view.show_message(text.phone_book_save_successful)

        except ValueError as e:
            self.view.show_message(f"Ошибка: {str(e)}")
        except FileOperationError as e:
            self.view.show_message(f"Ошибка при сохранении файла: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Ошибка при сохранении: {str(e)}")

    def _show_all_contacts(self) -> None:
        """Показ всех контактов"""
        if not self.phone_book.is_open and len(self.phone_book) == 0:
            self.view.show_message(text.phone_book_file_try_open)
            return

        contacts = self.phone_book.get_all_contacts()
        self.view.show_contacts(contacts, text.phone_book_empty_error)

    def _add_contact(self) -> None:
        """Добавление нового контакта"""
        try:
            contact_data = self.view.get_multiple_input(text.input_new_contact)
            contact = Contact.from_list(contact_data)
            contact_id = self.phone_book.add_contact(contact)
            self.view.show_message(text.new_contact_saved_successful.format(name=contact.name))
        except ValueError as e:
            self.view.show_message(f"Ошибка в данных контакта: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Ошибка при добавлении контакта: {str(e)}")

    def _find_contacts(self) -> None:
        """Поиск контактов"""
        if not self.phone_book.is_open and len(self.phone_book) == 0:
            self.view.show_message(text.phone_book_file_try_open)
            return

        try:
            search_term = self.view.get_input(text.input_word_to_find)
            found_contacts = self.phone_book.find_contacts(search_term)

            if found_contacts:
                self.view.show_contacts(found_contacts)
                self.view.show_message(f"Найдено контактов: {len(found_contacts)}")
            else:
                self.view.show_message(text.no_result_to_find.format(word=search_term))
        except Exception as e:
            self.view.show_message(f"Ошибка при поиске: {str(e)}")

    def _edit_contact(self) -> None:
        """Редактирование контакта"""
        if not self.phone_book.is_open and len(self.phone_book) == 0:
            self.view.show_message(text.phone_book_file_try_open)
            return

        try:
            contact_id_str = self.view.get_input(text.input_id_to_edit)
            if not contact_id_str.isdigit():
                self.view.show_message("ID должен быть числом")
                return

            contact_id = int(contact_id_str)

            # Получаем текущий контакт
            try:
                current_contact = self.phone_book.get_contact(contact_id)
            except ContactNotFoundError:
                self.view.show_message(f"Контакт с ID {contact_id} не найден")
                return

            self.view.show_message(f"Редактирование контакта: {current_contact.name}")
            self.view.show_message("Оставьте поле пустым, чтобы не изменять его")

            # Запрашиваем новые данные
            new_name = self.view.get_input(f"Новое имя [{current_contact.name}]: ")
            new_phone = self.view.get_input(f"Новый телефон [{current_contact.phone}]: ")
            new_comment = self.view.get_input(f"Новый комментарий [{current_contact.comment}]: ")

            # Обновляем контакт
            updated_contact = self.phone_book.update_contact(
                contact_id,
                name=new_name if new_name else None,
                phone=new_phone if new_phone else None,
                comment=new_comment if new_comment else None
            )

            self.view.show_message(text.contact_edited_successful.format(name=updated_contact.name))

        except ValueError as e:
            self.view.show_message(f"Ошибка в данных: {str(e)}")
        except ContactNotFoundError as e:
            self.view.show_message(str(e))
        except Exception as e:
            self.view.show_message(f"Ошибка при редактировании: {str(e)}")

    def _delete_contact(self) -> None:
        """Удаление контакта"""
        if not self.phone_book.is_open and len(self.phone_book) == 0:
            self.view.show_message(text.phone_book_file_try_open)
            return

        try:
            contact_id_str = self.view.get_input(text.input_contact_id_to_delete)
            if not contact_id_str.isdigit():
                self.view.show_message("ID должен быть числом")
                return

            contact_id = int(contact_id_str)

            # Получаем контакт для подтверждения
            try:
                contact = self.phone_book.get_contact(contact_id)
            except ContactNotFoundError:
                self.view.show_message(f"Контакт с ID {contact_id} не найден")
                return

            # Подтверждение удаления
            if self.view.confirm_action(f"Вы уверены, что хотите удалить контакт '{contact.name}'?"):
                deleted_contact = self.phone_book.delete_contact(contact_id)
                self.view.show_message(text.contact_deleted_successful.format(name=deleted_contact.name))
            else:
                self.view.show_message("Удаление отменено")

        except ContactNotFoundError as e:
            self.view.show_message(str(e))
        except Exception as e:
            self.view.show_message(f"Ошибка при удалении: {str(e)}")

    def _exit_program(self) -> None:
        """Выход из программы"""
        if len(self.phone_book) > 0:
            if self.view.confirm_action(text.phone_book_save_message):
                try:
                    # Если путь не указан, запрашиваем его
                    if not self._current_file_path:
                        self._current_file_path = self.view.get_input("Введите путь для сохранения: ")

                    self.phone_book.save(self._current_file_path)
                    self.view.show_message(text.phone_book_save_successful)
                except Exception as e:
                    self.view.show_message(f"Ошибка при сохранении: {str(e)}")

        self.view.show_message(text.end_of_program)
        raise SystemExit