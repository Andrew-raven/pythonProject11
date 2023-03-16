import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase
from user_states import *

class Base(DeclarativeBase): pass


# Пользователь бота ВК
class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    user_state = sq.Column(sq.Enum(UserStates))
    last_time = sq.Column(sq.DateTime)


# Анкеты добавленные в избранное
class DatingUser(Base):
    __tablename__ = 'dating_user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
 #   link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))


# Фото избранных анкет
#class Photos(Base):
#    __tablename__ = 'photos'
#    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
#    link_photo = sq.Column(sq.String)
#    count_likes = sq.Column(sq.Integer)
#    id_dating_user = sq.Column(sq.Integer, sq.ForeignKey('dating_user.id', ondelete='CASCADE'))


# Анкеты в черном списке
class BlackList(Base):
    __tablename__ = 'black_list'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))

