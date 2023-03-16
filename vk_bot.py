from vk_worker import *
from db_worker import *
from user_states import *
from datetime import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TIMEOUT = 180


class SearchParameters:
    sex = None
    age_from = None
    age_to = None
    city = None
    relation = None


class VkBot:
    vk_bot_interface: VkBotInterface = None
    vk_bot_data: DataStorage = None
    new_time: datetime = None
    user_found_profiles = {}    # хранит список полученных анкет для каждого пользователя {vk_id: список_анкет}
    user_last_profile = {}      # хранит последнюю показанную анкету для каждого пользователя {vk_id: номер_анкеты}

    def __init__(self, vk_bot_interface, vk_bot_data) -> None:
        self.relation_dict = ['не указано', 'не женат/не замужем', 'есть друг/есть подруга',
                              'помолвлен/помолвлена', 'женат/замужем', 'всё сложно',
                              'в активном поиске', 'влюблён/влюблена,в гражданском браке']
        self.search_parameters = SearchParameters()
        self.user = None
        self.vk_bot_interface = vk_bot_interface
        self.vk_bot_data = vk_bot_data

    def main_bot_menu(self):
        menu_keyboard = VkKeyboard(one_time=True)
        menu_keyboard.add_button(label='Новый поиск', color=VkKeyboardColor.PRIMARY)
        all_users = self.vk_bot_data.get_favorites(self.user.vk_id)
        if len(all_users) > 0:
            menu_keyboard.add_button(label='Избранное', color=VkKeyboardColor.PRIMARY)
        all_users = self.vk_bot_data.get_blacklisted(self.user.vk_id)
        if len(all_users) > 0:
            menu_keyboard.add_button(label='Черный список', color=VkKeyboardColor.PRIMARY)
        self.vk_bot_interface.send_message(self.user.vk_id, "Вас приветствует бот - Vkinder\nВыберите действие",
                                           keyboard=menu_keyboard.get_keyboard())
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.MAIN_MENU, self.new_time)

    def next_add_menu(self):
        menu_keyboard = VkKeyboard(one_time=True)
        menu_keyboard.add_button(label='Следующая анкета', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_button(label='Добавить в избранное', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_line()
        menu_keyboard.add_button(label='Главное меню', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_button(label='Добавить в черный список', color=VkKeyboardColor.PRIMARY)
        self.vk_bot_interface.send_message(self.user.vk_id, "Выберите действие",
                                           keyboard=menu_keyboard.get_keyboard())
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.NEXT_ADD_MENU, self.new_time)

    def next_favorites_blacklisted_menu(self, user_state):
        menu_keyboard = VkKeyboard(one_time=True)
        menu_keyboard.add_button(label='Следующая анкета', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_button(label='Удалить из списка', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_button(label='Главное меню', color=VkKeyboardColor.PRIMARY)
        self.vk_bot_interface.send_message(self.user.vk_id, "Выберите действие",
                                           keyboard=menu_keyboard.get_keyboard())
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, user_state, self.new_time)

    def get_blacklisted(self):
        self.user_found_profiles.update({self.user.vk_id: self.vk_bot_data.get_blacklisted(self.user.vk_id)})
        self.user_last_profile = {self.user.vk_id: -1}
        self.show_next_favorite_or_blacklisted_profile(UserStates.BLACKLISTED)
    #    self.next_favorites_blacklisted_menu()
    def get_favorites(self):
        self.user_found_profiles.update({self.user.vk_id: self.vk_bot_data.get_favorites(self.user.vk_id)})
        self.user_last_profile = {self.user.vk_id: -1}
        self.show_next_favorite_or_blacklisted_profile(UserStates.FAVORITES)
        #self.next_favorites_blacklisted_menu()

    def get_next_message(self):
        for event in self.vk_bot_interface.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event

    def run(self):
        while True:

            event = self.get_next_message()
            #    msg_text, user_id = self.vk_interface.long_poll.listen()
            if event.text:
                self.new_time = datetime.now()
                print('Получено сообщение', event.text, 'от пользователя', event.user_id)
                if self.vk_bot_data.register_new_user(event.user_id, UserStates.NOT_ACTIVE, str(datetime.now())):
                    # Регистрируем пользователя в БД если его там нет
                    print('Зарегистрирован новый пользователь', event.user_id)
                self.user = self.vk_bot_data.get_db_user(event.user_id)
                current_user_state = self.take_user_state()
                start_message = event.text.lower().replace('/', '') in ['start', 'bot', 'старт', 'бот', '1']
                if start_message:
                    current_user_state = UserStates.NOT_ACTIVE
                match current_user_state:
                    case UserStates.NOT_ACTIVE:
                        if start_message:
                            self.main_bot_menu()
                        else:
                            self.bot_not_active()

                    case UserStates.MAIN_MENU:
                        match event.text:
                            case 'Новый поиск':
                                self.ask_sex()
                            case 'Избранное':
                                self.get_favorites()
                            case 'Черный список':
                                self.get_blacklisted()
                            case _:
                                self.main_bot_menu()

                    case UserStates.GET_SEX:
                        sex_dict = ['Все', 'Девушки', 'Парни']
                        if event.text in sex_dict:
                            self.search_parameters.sex = sex_dict.index(event.text)
                            self.ask_age()
                            self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.GET_AGE, self.new_time)
                        else:
                            self.ask_sex()

                    case UserStates.GET_AGE:
                        try:
                            self.search_parameters.age_from = int(event.text[0:2])
                        except ValueError:
                            self.search_parameters.age_from = 18
                        try:
                            self.search_parameters.age_to = int(event.text[-2:])
                        except ValueError:
                            self.search_parameters.age_to = 99
                        self.vk_bot_interface.send_message(self.user.vk_id,
                                                           f'Выбран возраст {self.search_parameters.age_from}'
                                                           f' - {self.search_parameters.age_to}')
                        self.ask_city()

                    case UserStates.GET_CITY:
                        self.search_parameters.city = event.text
                        self.ask_relation()

                    case UserStates.GET_RELATION:
                        if event.text in self.relation_dict:
                            self.search_parameters.relation = self.relation_dict.index(event.text)
                        else:
                            self.search_parameters.relation = 0
                        self.user_found_profiles.update({self.user.vk_id: self.new_search()})
                        if len(self.user_found_profiles[self.user.vk_id]) > 0:
                            self.user_last_profile = {self.user.vk_id: -1}
                            self.show_next_profile()
                            self.next_add_menu()
                        else:
                            self.vk_bot_interface.send_message(self.user.vk_id, 'Ваш запрос не дал результатов')
                            self.main_bot_menu()
                    case UserStates.NEXT_ADD_MENU:
                        profile_num = self.user_last_profile[self.user.vk_id]
                        shown_user = self.user_found_profiles[self.user.vk_id][profile_num]
                        match event.text:
                            case 'Добавить в избранное':
                                if self.vk_bot_data.add_to_favorites(shown_user, self.user):
                                    self.vk_bot_interface.send_message(self.user.vk_id,
                                              'Пользователь добавлен в избранное.')
                                else:
                                    self.vk_bot_interface.write_msg(self.user.vk_id,
                                                               'Пользователь уже в избранном.')
                            case 'Добавить в черный список':
                                if self.vk_bot_data.add_to_black_list(shown_user, self.user):
                                    self.vk_bot_interface.send_message(self.user.vk_id,
                                              'Пользователь добавлен в чёрный список.')
                                else:
                                    self.vk_bot_data.write_msg(self.user.vk_id,
                                                               'Пользователь уже в чёрном списке.')
                            case 'Следующая анкета':
                                pass
                            case 'Главное меню':
                                self.main_bot_menu()
                                continue
                            case _:
                                self.next_add_menu()
                                continue
                        self.show_next_profile()
                        self.next_add_menu()

                    case UserStates.BLACKLISTED:
                        match event.text:
                            case 'Следующая анкета':
                                self.show_next_favorite_or_blacklisted_profile(UserStates.BLACKLISTED)
                            case 'Удалить из списка':
                                self.vk_bot_data.delete_db_blacklist(self.user_found_profiles[self.user.vk_id]
                                                                     [self.user_last_profile[self.user.vk_id]].vk_id)
                                self.show_next_favorite_or_blacklisted_profile(UserStates.BLACKLISTED)
                            case 'Главное меню':
                                self.main_bot_menu()
                            case _:
                                self.next_favorites_blacklisted_menu(UserStates.BLACKLISTED)

                    case UserStates.FAVORITES:
                        match event.text:
                            case 'Следующая анкета':
                                self.show_next_favorite_or_blacklisted_profile(UserStates.FAVORITES)
                            case 'Удалить из списка':
                                self.vk_bot_data.delete_db_favorites(self.user_found_profiles[self.user.vk_id]
                                                                     [self.user_last_profile[self.user.vk_id]].vk_id)
                                self.show_next_favorite_or_blacklisted_profile(UserStates.FAVORITES)
                            case 'Главное меню':
                                self.main_bot_menu()
                            case  _:
                                self.next_favorites_blacklisted_menu(UserStates.FAVORITES)

    def show_next_favorite_or_blacklisted_profile(self, user_state):
        show_user = False
        next_profile_num = self.user_last_profile.get(self.user.vk_id)
        while not show_user:
            next_profile_num += 1
            if len(self.user_found_profiles[self.user.vk_id]) <= next_profile_num:
                msg = 'Анкеты закончились'
                self.vk_bot_interface.send_message(self.user.vk_id, msg)
                self.main_bot_menu()
                return
            next_profile = self.user_found_profiles[self.user.vk_id][next_profile_num]
            photos = self.vk_bot_interface.get_photo(next_profile.vk_id)
            msg = '@id' + str(next_profile.vk_id) + \
                  '(' + next_profile.first_name + " " + next_profile.last_name + ")"
            self.vk_bot_interface.send_message(self.user.vk_id, msg)
            self.vk_bot_interface.send_message(self.user.vk_id, f'фото:', attachment=','.join(photos))
            self.user_last_profile[self.user.vk_id] = next_profile_num
            show_user = True
        self.next_favorites_blacklisted_menu(user_state)

    def show_next_profile(self):
        show_user = False
        next_profile_num = self.user_last_profile.get(self.user.vk_id)
        while not show_user:
            next_profile_num += 1
            if len(self.user_found_profiles[self.user.vk_id]) <= next_profile_num:
                msg = 'Анкеты закончились'
                self.vk_bot_interface.send_message(self.user.vk_id, msg)
                self.main_bot_menu()
                return
            next_profile = self.user_found_profiles[self.user.vk_id][next_profile_num]
            favorites, black = self.vk_bot_data.check_db_user(next_profile['vk_id'])
            photos = self.vk_bot_interface.get_photo(next_profile['vk_id'])
            if favorites or black or not photos:
                continue
            msg = '@id' + str(next_profile['vk_id']) + \
                  '(' + next_profile['first_name'] + " " + next_profile['last_name'] + ")"
            self.vk_bot_interface.send_message(self.user.vk_id, msg)
            self.vk_bot_interface.send_message(self.user.vk_id, f'фото:', attachment=','.join(photos))
            self.user_last_profile[self.user.vk_id] = next_profile_num
            show_user = True

    def new_search(self):
        found_users = self.vk_bot_interface.search_users(self.search_parameters.sex,
                                                         self.search_parameters.age_from,
                                                         self.search_parameters.age_to,
                                                         self.search_parameters.city,
                                                         self.search_parameters.relation)
        return found_users

    def ask_relation(self):
        button_num = 0
        menu_keyboard = VkKeyboard(one_time=True)
        for value in self.relation_dict:
            if button_num % 3 == 0 and button_num != 0:
                menu_keyboard.add_line()
            menu_keyboard.add_button(label=value, color=VkKeyboardColor.PRIMARY)
            button_num += 1
        self.vk_bot_interface.send_message(self.user.vk_id, "Выберите статус",
                                           keyboard=menu_keyboard.get_keyboard())
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.GET_RELATION, self.new_time)


    def ask_city(self):
        self.vk_bot_interface.send_message(self.user.vk_id, "Введите город\n")
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.GET_CITY, self.new_time)

    def ask_age(self):
        self.vk_bot_interface.send_message(self.user.vk_id, "Введите возраст в формате от - до (18 - 99)\n")
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.GET_AGE, self.new_time)

    def ask_sex(self):
        menu_keyboard = VkKeyboard(one_time=True)
        menu_keyboard.add_button(label='Парни', color=VkKeyboardColor.PRIMARY)
        menu_keyboard.add_button(label='Девушки', color=VkKeyboardColor.NEGATIVE)
        menu_keyboard.add_button(label='Все', color=VkKeyboardColor.SECONDARY)
        self.vk_bot_interface.send_message(self.user.vk_id, "Выберите пол",
                                           keyboard=menu_keyboard.get_keyboard())
        self.vk_bot_data.update_last_time_and_state(self.user.vk_id, UserStates.GET_SEX, self.new_time)

    def bot_not_active(self):
        menu_keyboard = VkKeyboard(one_time=True)
        menu_keyboard.add_button(label='Start', color=VkKeyboardColor.PRIMARY)
        self.vk_bot_interface.send_message(self.user.vk_id, "Тут нет живых. Для активации бота наберите /start",
                                           keyboard=menu_keyboard.get_keyboard())

    def take_user_state(self):
        current_user_state = UserStates.NOT_ACTIVE
        if self.user:
            current_user_state = self.user.user_state
            print('пользователь уже зарегистрирован')
            diff_seconds = int((self.new_time - self.user.last_time).total_seconds())
            print(f'предыдущее сообщение было {diff_seconds} секунд назад')
            if diff_seconds > TIMEOUT or self.user.user_state == 0:
                current_user_state = UserStates.NOT_ACTIVE
                # с последнего сообщения прошло много секунд или пользователь сам завершил сеанс
        return current_user_state
