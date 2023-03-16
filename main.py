from vk_worker import *
from credentials import *
from vk_bot import VkBot
from db_worker import DataStorage
import sys

assert sys.version_info >= (3, 10), 'I need python version >= 3.10'


def main():
    secrets = Secrets()
    ############################################################################
    #                                    УДАЛИТЬ ПОТОМ
    print('API:', secrets.vk_api_ver)
    print('App ID:', secrets.app_id)
    print('Group token:', secrets.group_token)
    print('User token:', secrets.user_token)
    print('DB name:', secrets.db_name)
    print('DB user name:', secrets.db_user)
    print('DB user password:', secrets.db_pass)
    ##############################################################################
    user_choice = start_menu()
    if user_choice == '2':
        secrets.set_new_credentials()
        sys.exit()
    elif user_choice == '3':
        print('Очищаю секретные данные')
        secrets.delete_credentials()
        sys.exit()
    try:
        vk_bot_data = DataStorage(secrets)
    except Exception as db_error:
        print("Ошибка подключения к БД", db_error)
        sys.exit(-1)
    vk_bot_data.create_tables()
    if user_choice == '4':
        try:
            vk_bot_data.drop_tables()
            print('Таблицы удалены')
            sys.exit()
        except Exception as db_error:
            print("Ошибка удаления таблиц", db_error)
            sys.exit(-1)
    elif user_choice == '5':
        try:
            vk_bot_data.create_tables()
            print('Таблицы созданы')
            sys.exit()
        except Exception as db_error:
            print("Ошибка создания таблиц", db_error)
            sys.exit(-1)
    elif user_choice != '1':
        print('Вы выбрали не ту пилюлю')
        sys.exit()

    try:
        vk_bot_interface = VkBotInterface(secrets)
    except Exception as vk_bot_interface_error:
        print(vk_bot_interface_error)
        sys.exit(-1)

    vk_bot = VkBot(vk_bot_interface, vk_bot_data)
    print("Бот запущен")
    vk_bot.run()


def start_menu():
    print("""
            1 - Запуск бота
            2 - Ввод учетных данных
            3 - Удаление учетных данных
            4 - Дропнуть таблицы
            5 - Создать таблицы""")
    return input()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(error)
