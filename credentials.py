import keyring
from config import *
from getpass import getpass

class Secrets():

    def __init__(self):
        self.vk_api_ver = vk_api_ver
        self.app_id = app_id
        self.group_token = keyring.get_password(system, group_token_name)
        self.user_token = keyring.get_password(system, user_token_name)
        self.db_name = keyring.get_password(system, db_name)
        self.db_user = keyring.get_password(system, db_user_name)
        self.db_pass = keyring.get_password(system, db_user_pass)

    def set_new_credentials(self):
        self.group_token = input('Введите токен вашей группы (enter - не менять): ')
        if len(self.group_token) > 0:
            try:
                keyring.set_password(system, group_token_name, self.group_token)
            except keyring.errors.PasswordSetError:
                print('Ошибка сохранения токена группы')

        self.user_token = input('Введите токен пользователя (enter - не менять): ')
        if len(self.user_token):
            try:
                keyring.set_password(system, user_token_name, self.user_token)
            except keyring.errors.PasswordSetError:
                print('Ошибка сохранения токена пользователя')

        self.db_name = input('Введите название DB (enter - не менять): ')
        if len(self.db_name):
            try:
                keyring.set_password(system, db_name, self.db_name)
            except keyring.errors.PasswordSetError:
                print('Ошибка сохранения названия DB')

        self.db_user = input('Введите имя пользователя DB (enter - не менять): ')
        if len(self.db_user):
            try:
                keyring.set_password(system, db_user_name, self.db_user)
            except keyring.errors.PasswordSetError:
                print('Ошибка сохранения названия DB')

        self.db_pass = getpass('Введите пароль пользователя BD (enter - не менять): ')
        if len(self.db_pass):
            try:
                keyring.set_password(system, db_user_pass, self.db_pass)
            except keyring.errors.PasswordSetError:
                print('Ошибка сохранения пароля пользователя DB')

    def delete_credentials(self):
        try:
            keyring.delete_password(system, group_token_name)
            keyring.delete_password(system, user_token_name)
            keyring.delete_password(system, db_name)
            keyring.delete_password(system, db_user_name)
            keyring.delete_password(system, db_user_pass)
        except keyring.errors.PasswordDeleteError:
            print('Ошибка удаления секретных дааных')
