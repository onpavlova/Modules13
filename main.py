
from controller.phonebook_controller import PhoneBookController

def main():
    """Основная функция запуска приложения"""
    controller = PhoneBookController()
    controller.run()

if __name__ == "__main__":
    main()