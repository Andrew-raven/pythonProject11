import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import models
from credentials import Secrets


class DataStorage():
    def __init__(self, secrets: Secrets):
        connection_string = f'postgresql://{secrets.db_user}:{secrets.db_pass}@localhost:5432/{secrets.db_name}'
        self.engine = sq.create_engine(connection_string, client_encoding='utf8')
        session = sessionmaker(bind=self.engine)
        self.db_session = session()
        self.connection = self.engine.connect()

    def create_tables(self):
        models.Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        models.Base.metadata.drop_all(bind=self.engine)

    def delete_db_blacklist(self, ids):
        current_user = self.db_session.query(models.BlackList).filter_by(vk_id=ids).first()
        self.db_session.delete(current_user)
        self.db_session.commit()

    def delete_db_favorites(self, ids):
        current_user = self.db_session.query(models.DatingUser).filter_by(vk_id=ids).first()
        self.db_session.delete(current_user)
        self.db_session.commit()

    def get_db_user(self, ids):
        """
        Get Vk user from DB
        :param ids: user VK id
        :return: user from DB or None
        """
        return self.db_session.query(models.User).filter_by(vk_id=ids).first()

    # обновляет время последнего сообщения и состояние пользователя
    def update_last_time_and_state(self, vk_id, new_user_state, new_time):
        user = self.db_session.query(models.User).filter_by(vk_id=vk_id).first()
        current_user = self.db_session.query(models.User).get(user.id)
        current_user.last_time = new_time
        current_user.user_state = new_user_state
        self.db_session.commit()

    def check_db_user(self, ids):
        """
        Проверяет, есть ли пользователь в БД
        """
        dating_user = self.db_session.query(models.DatingUser).filter_by(
            vk_id=ids).first()
        blocked_user = self.db_session.query(models.BlackList).filter_by(
            vk_id=ids).first()
        return dating_user, blocked_user

    def get_blacklisted(self, ids):
        """
        Проверяет, есть ли у пользователя кто-то в черном списке
        """
        current_user = self.db_session.query(models.User).filter_by(vk_id=ids).first()
        # Находим все анкеты из чс которые добавил данный юзер
        all_users = self.db_session.query(models.BlackList).filter_by(id_user=current_user.id).all()
        return all_users

    def get_favorites(self, ids):
        """
        Проверяет, есть ли у пользователя кто-то в избранном
        """
        current_user = self.db_session.query(models.User).filter_by(vk_id=ids).first()
        # Находим все анкеты из избранного которые добавил данный юзер
        all_users = self.db_session.query(models.DatingUser).filter_by(id_user=current_user.id).all()
        return all_users

    # Регистрация пользователя
    def register_new_user(self, vk_id, user_state, last_time):
        if not self.get_db_user(vk_id):
            try:
                new_user = models.User(
                    vk_id=vk_id,
                    user_state=user_state,
                    last_time=last_time
                )
                self.db_session.add(new_user)
                self.db_session.commit()
                return True
            except (IntegrityError, InvalidRequestError) as error:
                print(error)
        return False

    def add_to_favorites(self, added_user, user):
        try:
            new_user = models.DatingUser(
                vk_id=added_user['vk_id'],
                first_name=added_user['first_name'],
                last_name=added_user['last_name'],
 #               link=added_user[2],
                id_user=user.id
            )
            self.db_session.add(new_user)
            self.db_session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    def add_to_black_list(self, added_user, user):
        try:
            new_user = models.BlackList(
                vk_id=added_user['vk_id'],
                first_name=added_user['first_name'],
                last_name=added_user['last_name'],
#                link=added_user[2],
                id_user=user.id
            )
            self.db_session.add(new_user)
            self.db_session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    # Сохранение в БД фото добавленного пользователя
    def add_user_photos(self, event_id, link_photo, count_likes, id_dating_user):
        try:
            new_user = models.Photos(
                link_photo=link_photo,
                count_likes=count_likes,
                id_dating_user=id_dating_user
            )
            self.db_session.add(new_user)
            self.db_session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False


