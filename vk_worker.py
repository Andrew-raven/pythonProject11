from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from vk_api import VkApi
from vk_api.utils import get_random_id


class VkBotInterface:
    vk_user_api_access = None
    vk_group_api_access = None
    long_poll = None
    secrets = None
    vk_session = None

    def __init__(self, secrets):
        self.secrets = secrets
        self.vk_user_api_access = self.user_auth()
        if self.vk_user_api_access is not None:
            self.authorized = True
        self.long_poll = self.long_pool_start()
        return

    def get_photo(self, user_owner_id):
        vk_ = VkApi(token=self.secrets.user_token)
        try:
            response = vk_.method('photos.get',
                                  {'owner_id': user_owner_id,
                                   'album_id': 'profile',
                                   'count': 20,
                                   'extended': 1,
                                   'photo_sizes': 1
                                   })
        except ApiError:
            return False
        users_photos = []
        photo_count = len(response['items'])
        for i in range(photo_count):
            users_photos.append(
                [response['items'][i]['likes']['count'],
                 response['items'][i]['comments']['count'],
                 'photo' + str(response['items'][i]['owner_id']) + '_' + str(response['items'][i]['id'])])
        users_photos.sort(reverse=True)
        users_photos = users_photos[0:3]
        result = []
        for photo in users_photos:
            result.append(photo[2])
        return result

    #    def get_user_by_id(self, vk_id):

    def search_users(self, sex, age_start, age_end, city, relation):
        all_persons = []
        link_profile = 'https://vk.com/id'
        vk_ = VkApi(token=self.secrets.user_token)
        response = vk_.method('users.search',
                              {'sort': 0,
                               'sex': sex,
                               'status': relation,
                               'age_from': age_start,
                               'age_to': age_end,
                               'has_photo': 1,
                               'count': 25,
                               'online': 1,
                               'hometown': city
                               })
        for element in response['items']:
            person = {'first_name': element['first_name'],
                      'last_name': element['last_name'],
#                      'link_profile': link_profile + str(element['id']),
                      'vk_id': element['id']
                      }
            all_persons.append(person)
        return all_persons

    def user_auth(self):
        try:
            self.vk_session = VkApi(token=self.secrets.user_token)
            return self.vk_session.get_api()
        except Exception as error:
            raise

    def long_pool_start(self):
        self.vk_group_api_access = VkApi(token=self.secrets.group_token)
        return VkLongPoll(self.vk_group_api_access)

    def send_message(self, receiver_user_id: str = '144912973', message_text: str = "тестовое сообщение",
                     attachment=None, keyboard=None):
        """
        Отправка сообщения от лица авторизованного пользователя
        :param receiver_user_id: уникальный идентификатор получателя сообщения
        :param message_text: текст отправляемого сообщения
        :param attachment: вложение в сообщении
        :param keyboard: клавиатура VK
        """
        if not self.authorized:
            print("Unauthorized. Check if ACCESS_TOKEN is valid")
            return
        try:
            self.vk_group_api_access.method('messages.send',
                                            {'user_id': receiver_user_id,
                                             'message': message_text,
                                             'random_id': get_random_id(),
                                             'attachment': attachment,
                                             'keyboard': keyboard})
            print(f"Сообщение отправлено для ID {receiver_user_id} с текстом: {message_text}")
        except Exception as error:
            print(error)


"""
    def run_long_poll(self):

        for event in self.long_poll.listen():

            # если пришло новое сообщение - происходит проверка текста сообщения
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                print('Получено сообщение')
                # если была получена одна из заданных фраз
                if event.text.lower() in ['/start', 'start', '/bot', 'bot']:

                    # ответ отправляется в личные сообщения пользователя (если сообщение из личного чата)
                    if event.from_user:
                        print('Личное')
                        self.send_message(receiver_user_id=event.user_id, message_text="Пошел нахуй)")

                    # ответ отправляется в беседу (если сообщение было получено в общем чате)
                    elif event.from_chat:
                        print('В беседе')
                        self.send_message(receiver_user_id=event.chat_id, message_text="Всем привет")
"""
