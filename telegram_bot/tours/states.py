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