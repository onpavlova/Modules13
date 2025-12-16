class PhoneBookError(Exception):
    """Базовое исключение для телефонного справочника"""
    pass


class FileOperationError(PhoneBookError):
    """Ошибка при работе с файлом"""
    def __init__(self, message="Ошибка при работе с файлом", filename=None):
        self.filename = filename
        super().__init__(f"{message}: {filename}" if filename else message)


class ContactNotFoundError(PhoneBookError):
    """Контакт не найден"""
    def __init__(self, contact_id=None, name=None):
        self.contact_id = contact_id
        self.name = name
        message = "Контакт не найден"
        if contact_id:
            message += f" с ID: {contact_id}"
        if name:
            message += f" с именем: {name}"
        super().__init__(message)


class InvalidInputError(PhoneBookError):
    """Неверный ввод данных"""
    pass


class PhoneBookNotOpenError(PhoneBookError):
    """Телефонная книга не открыта"""
    def __init__(self):
        super().__init__("Телефонная книга не открыта. Сначала откройте файл.")