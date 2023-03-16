from enum import Enum


# синтаксис класса
class UserStates(Enum):
    NOT_ACTIVE  = 0
    MAIN_MENU   = 1
    GET_SEX     = 2
    GET_AGE     = 3
    GET_CITY    = 4
    GET_RELATION= 5
    NEW_SEARCH  = 6
    BLACKLISTED = 7
    FAVORITES   = 8
    NEXT_ADD_MENU = 9

