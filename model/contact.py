
from dataclasses import dataclass
from typing import Optional


@dataclass
class Contact:
    """Класс для представления контакта"""
    name: str
    phone: str
    comment: str
    id: Optional[int] = None

    def to_list(self) -> list[str]:
        """Преобразует контакт в список строк"""
        return [self.name, self.phone, self.comment]

    def to_string(self, separator: str = ';') -> str:
        """Преобразует контакт в строку"""
        return separator.join(self.to_list())

    @classmethod
    def from_list(cls, data: list[str], contact_id: Optional[int] = None) -> 'Contact':
        """Создает контакт из списка строк"""
        if len(data) != 3:
            raise ValueError("Список должен содержать 3 элемента: имя, телефон, комментарий")
        return cls(name=data[0], phone=data[1], comment=data[2], id=contact_id)

    def __str__(self) -> str:
        return f"{self.name}: {self.phone} ({self.comment})"