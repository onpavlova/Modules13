import os
from typing import Dict, List
from exceptions import FileOperationError


class FileHandler:
    """Класс для обработки операций с файлами"""

    def __init__(self, separator: str = ';'):
        self.separator = separator

    def load(self, file_path: str) -> Dict[int, List[str]]:
        """Загрузка данных из файла"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")

            with open(file_path, 'r', encoding='UTF-8') as file:
                contacts = {}
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if line:
                        contacts[line_num] = line.split(self.separator)
                return contacts

        except FileNotFoundError as e:
            raise FileOperationError(f"Файл не найден", file_path) from e
        except PermissionError as e:
            raise FileOperationError(f"Нет доступа к файлу", file_path) from e
        except Exception as e:
            raise FileOperationError(f"Ошибка при чтении файла", file_path) from e

    def save(self, file_path: str, contacts: Dict[int, List[str]]) -> None:
        """Сохранение данных в файл"""
        try:
            with open(file_path, 'w', encoding='UTF-8') as file:
                lines = []
                for contact_id in sorted(contacts.keys()):
                    contact_data = contacts[contact_id]
                    line = self.separator.join(contact_data)
                    lines.append(line)
                file.write('\n'.join(lines))

        except PermissionError as e:
            raise FileOperationError(f"Нет доступа для записи в файл", file_path) from e
        except Exception as e:
            raise FileOperationError(f"Ошибка при сохранении файла", file_path) from e