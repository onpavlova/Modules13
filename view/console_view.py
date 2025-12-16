
from typing import Dict, List, Optional
from model.contact import Contact
import text


class ConsoleView:
    """Класс для взаимодействия с пользователем через консоль"""

    @staticmethod
    def show_menu() -> None:
        """Отображение главного меню"""
        for i, item in enumerate(text.main_menu_items):
            print(f'\t{i}. {item}' if i else item)

    @staticmethod
    def get_user_choice() -> int:
        """Получение выбора пользователя"""
        while True:
            try:
                number = input(text.user_menu_choice)
                if number.isdigit():
                    choice = int(number)
                    if 0 < choice < len(text.main_menu_items):
                        return choice
                print(text.user_menu_choice_error)
            except KeyboardInterrupt:
                print("\nПрограмма прервана пользователем")
                raise
            except Exception:
                print(text.user_menu_choice_error)

    @staticmethod
    def get_input(prompt: str) -> str:
        """Получение ввода от пользователя"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\nВвод прерван")
            raise

    @staticmethod
    def get_multiple_input(prompts: List[str]) -> List[str]:
        """Получение нескольких вводов от пользователя"""
        results = []
        for prompt in prompts:
            results.append(ConsoleView.get_input(prompt))
        return results

    @staticmethod
    def show_message(message: str) -> None:
        """Отображение сообщения"""
        print(f"{message}")

    @staticmethod
    def show_contacts(contacts: Dict[int, Contact], empty_message: str = "Телефонная книга пуста") -> None:
        """Отображение списка контактов"""
        if not contacts:
            ConsoleView.show_message(empty_message)
            return

        print("\n" + "=" * 80)
        print(f"{'ID':>3} {'Имя':<25} {'Телефон':<25} {'Комментарий':<25}")
        print("-" * 80)

        for contact_id, contact in sorted(contacts.items()):
            print(f"{contact_id:>3}. {contact.name:<25} {contact.phone:<25} {contact.comment:<25}")

        print("=" * 80 + "\n")

    @staticmethod
    def confirm_action(message: str) -> bool:
        """Подтверждение действия пользователем"""
        response = input(f"{message} (да/нет): ").strip().lower()
        return response in ['да', 'д', 'yes', 'y']

    @staticmethod
    def get_file_path() -> str:
        """Получение пути к файлу"""
        return ConsoleView.get_input(text.input_path_message)