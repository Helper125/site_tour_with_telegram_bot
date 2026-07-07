from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    tg_id = State()
    username = State()
    email = State()
    password = State()
    password2 = State()


class Login(StatesGroup):
    tg_id = State()
    email = State()
    password = State()


class AddLand(StatesGroup):
    name = State()


class AddCity(StatesGroup):
    name = State()
    land_id = State()

class AddLandmark(StatesGroup):
    name = State()
    address = State()
    description = State()
    city_id = State()