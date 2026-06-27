from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .states import Register, Login
from src.auth.hashing import hash_password, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..auth.models import User_tg
from src.auth.models import User
from email_validator import validate_email, EmailNotValidError

router = Router()


@router.message(Command("start"))
async def start_bot(message: Message):
    user = message.from_user
    await message.answer(f'''Hello {user.first_name}! Do you want login or register account that synchronize data from the LandmarkInLands? \n\nIf you want to login your accout, you need to write the command /login. If you don`n accout and you want to create accout, that you want to write /register.''')


@router.message(Command("all_users"))
async def all_users(message: Message):
    async with async_session() as session:
        all_user = await session.scalars(select(User))
        answer_user = all_user.all()
        

        await message.answer("\n".join(f"ID: {user.id}, username: {user.username}, email: {user.email}, is_admin: {user.is_admin}" for user in answer_user))


@router.message(Command("all_tg_users"))
async def all_users(message: Message):
    async with async_session() as session:
        all_tg_user = await session.scalars(select(User_tg).options(selectinload(User_tg.user)))
        answer_tg_user = all_tg_user.all()
        if answer_tg_user != []:
            await message.answer(
                "\n".join(f"ID: {user_tg.id}, ID_tg: {user_tg.tg_id}, username: {user_tg.user.username}, login: {user_tg.login}, created_at: {user_tg.created_at}, is_admin: {user_tg.user.is_admin}" for user_tg in answer_tg_user)
            )
        else:
            await message.answer("Users are not register in telegram")


@router.message(Command("register"))
async def register(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return
    async with async_session() as session:
        check = await session.scalar(select(User_tg).where(User_tg.tg_id == message.from_user.id, User_tg.login == True))
        if check:
            await message.answer("You are in the account")
            return
        
        await state.set_state(Register.username)

        await message.answer("Please enter your username")


@router.message(Register.username)
async def get_username_register(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return
    await state.update_data(username=message.text)

    await state.set_state(Register.email)

    await message.answer("Please enter your email")


@router.message(Register.email)
async def get_email_register(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return
    email = message.text

    await message.delete()

    try:
        valid = validate_email(email)
        email = valid.email

        await state.update_data(email=email)

        await state.set_state(Register.password)

        await message.answer("Please enter your password")
    except EmailNotValidError as e:
        await message.answer(f"Invalid email: {e}")



@router.message(Register.password)
async def get_password_register(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return
    password = message.text

    await message.delete()

    await state.update_data(password=password)

    await state.set_state(Register.password2)

    await message.answer("Please your password again")


@router.message(Register.password2)
async def get_password2_register(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return
    password2 = message.text

    await message.delete()

    data = await state.get_data()
    if password2 != data["password"]:
        await state.set_state(Register.password2)
        await message.answer("Your password doesn`t match")
        return


    await state.update_data(password2=password2, tg_id=message.from_user.id)

    data = await state.get_data()

    async with async_session() as session:
        user = User(username=data["username"], email=data["email"], password=hash_password(data["password"]))
        session.add(user)
        await session.commit()
        user_tg = User_tg(user_id=user.id, tg_id=message.from_user.id, login=True)
        session.add(user_tg)
        await session.commit()

        await message.answer("Your account has been successfully created")
        await state.clear()


@router.message(Command("login"))
async def login(message: Message, state: FSMContext):
    async with async_session() as session:
        check = await session.scalar(select(User_tg).where(User_tg.tg_id == message.from_user.id, User_tg.login == True))
        if check:
            await message.answer("You are in the account")
            return 

    await state.set_state(Login.email)

    await message.answer("please enter your email")


@router.message(Login.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)

    await state.set_state(Login.password)

    await message.answer("Please enter your password")


@router.message(Login.password)
async def get_password(message: Message, state: FSMContext):
    password = message.text
    await message.delete()
    await state.update_data(password=password, tg_id=message.from_user.id)

    data = await state.get_data()

    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == data["tg_id"], User.email == data["email"]))
        if user:
            if not verify_password(data["password"], user.user.password):
                await state.clear()
                await message.answer("Incorrect email or password")
            if not user.login:
                user.login = True
                await session.commit()
                await message.answer("good")
        else:
            user_site = await session.scalar(select(User).where(User.email == data["email"]))
            if user_site:
                stmt = User_tg(user_id=user_site.id, tg_id=data["tg_id"], login=True)
                session.add(stmt)
                await session.commit()
                await message.answer("good")
            else:
                await message.answer("You don`t have account. Please register new account through the command /register")

    await state.clear()


@router.message(Command("logout"))
async def logout(message: Message):
    user_id = message.from_user.id
    async with async_session() as session:    
        user = await session.scalar(select(User_tg).where(User_tg.tg_id == user_id, User_tg.login == True))

        if user:
            user.login = False
            await session.commit()
            await message.answer("You are logout")
        else:
            await message.answer("You don`t register")
            return
        

@router.message(Command("profil"))
async def profil(message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == user_id, User_tg.login == True))
        if len(user.user.email) >= 18:
            user_email = user.user.email[3:14]
        else:
            user_email = user.user.email[1:5]
        if user:
            if user.user.is_admin:
                 await message.answer(f"Your profil admin:\nUsername: {user.user.username}\nEmail: ***{user_email}***\nCreated_at: {user.created_at}\nAdmin: {user.user.is_admin}")
            else: 
                await message.answer(f"Your profil:\nUsername: {user.user.username}\nEmail: ***{user_email}***\nCreated_at: {user.created_at}")