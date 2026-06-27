from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
from src.tour.models import Lands, City, Landmarks, FavoriteLands, FavoriteCity, FavoriteLandmarks

from ..keyboards.InlineKeyboards import lands, cities, landmarks, save_topic, saves_lands, saves_cities, saves_landmarks, saves_landmark_back

router = Router()

@router.message(Command("lands"))
async def all_lands(message: Message):
    async with async_session() as session:
        land = await session.scalars(select(Lands).offset(0).limit(10))
        list_land = land.all()
        await message.answer("Lands:", reply_markup=lands(list_land))

@router.callback_query(F.data.startswith("lands"))
async def all_lands_callback_query(callback: CallbackQuery):
    await callback.message.delete()
    await all_lands(callback.message)


@router.callback_query(F.data.startswith("land_"))
async def cities_in_land(callback: CallbackQuery):
    land_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        city = await session.scalars(select(City).options(selectinload(City.land)).join(City.land).where(Lands.id == land_id))
        list_city = city.all()
        if not list_city:
            await callback.answer("Sorry, but hier is no information", show_alert=True)
            return
        await callback.message.delete()
        await callback.message.answer(f"City in {list_city[0].land.name}", reply_markup=cities(list_city))


@router.callback_query(F.data.startswith("city_"))
async def landmarks_in_city(callback: CallbackQuery):
    city_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        landmark = await session.scalars(select(Landmarks).options(selectinload(Landmarks.city).selectinload(City.land)).join(Landmarks.city).where(City.id == city_id))
        list_landmark = landmark.all()
        if not list_landmark:
            await callback.answer("Sorry, but hier is no information", show_alert=True)
            return
        await callback.message.delete()
        await callback.message.answer(f"Landmarks in {list_landmark[0].city.name}", reply_markup=landmarks(list_landmark, list_landmark[0].city.land.id))

@router.callback_query(F.data.startswith("landmark_"))
async def landmarks_more(callback: CallbackQuery):
    landmark_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        landmark = await session.scalar(select(Landmarks).where(Landmarks.id == landmark_id))
        if not landmark:
            await callback.answer("Sorry, but hier is no information", show_alert=True)
            return
        await callback.message.delete()
        await callback.message.answer(f"Name: {landmark.name}\nAddress: {landmark.address}\nDescription: {landmark.description}")


@router.message(Command("save"))
async def save(message: Message, user_ids: str | None = None):
    if not user_ids:
        user_id = message.from_user.id
    else:
        user_id = user_ids
    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == user_id, User_tg.login == True))
        if not user:
            message.answer("you do must to /register or /login, if you do look your saves")
            return
        
        await message.answer("Please select category:", reply_markup=save_topic())

@router.callback_query(F.data.startswith("saved_lands"))
async def save_lands(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == user_id, User_tg.login == True))
        lands = await session.scalars(select(FavoriteLands).options(selectinload(FavoriteLands.land)).where(FavoriteLands.user_id == user.user.id))
        all_lands = lands.all()

        if not user:
            await callback.message.answer("You must to /register or /login, if you look your saves")
            return

        if not all_lands:
            await callback.answer("Sorry, but you don`t have saves lands", show_alert=True)
            return

        await callback.message.delete()
        await callback.message.answer("All your saved lands", reply_markup=saves_lands(all_lands))

@router.callback_query(F.data.startswith("saved_cities"))
async def save_cities(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == user_id, User_tg.login == True))
        cities = await session.scalars(select(FavoriteCity).options(selectinload(FavoriteCity.city)).where(FavoriteCity.user_id == user.user.id))
        all_cities = cities.all()

        if not user:
            await callback.message.answer("You must to /register or /login, if you look your saves")

        if not all_cities:
            await callback.answer("Sorry, but you don`t have saves cities", show_alert=True)
            return
        
        await callback.message.delete()
        await callback.message.answer("All your saved cities", reply_markup=saves_cities(all_cities))

@router.callback_query(F.data.startswith("saved_landmarks"))
async def save_landmarks(callback: CallbackQuery, user_ids: str | None = None):
    if not user_ids:
        user_id = callback.from_user.id
    else:
        user_id = user_ids
    async with async_session() as session:
        user = await session.scalar(select(User_tg).options(selectinload(User_tg.user)).where(User_tg.tg_id == user_id, User_tg.login == True))
        landmarks = await session.scalars(select(FavoriteLandmarks).options(selectinload(FavoriteLandmarks.landmark)).where(FavoriteLandmarks.user_id == user.user.id))
        all_landmarks = landmarks.all()

        if not user:
            await callback.message.answer("You must to /register or /login, if you look your saves")

        if not all_landmarks:
            await callback.answer("Sorry, but you don`t have saves landmarks", show_alert=True)
            return
        
        await callback.message.delete()
        await callback.message.answer("All your saved landmarks:", reply_markup=saves_landmarks(all_landmarks))


@router.callback_query(F.data.startswith("saves_landmark_"))
async def save_landmark_more(callback: CallbackQuery):
    landmark_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        landmark = await session.scalar(select(Landmarks).where(Landmarks.id == landmark_id))

        if not landmark:
            await callback.message.answer("Error")
            return
        
        await callback.message.delete()
        await callback.message.answer(f"Name: {landmark.name}\nAddress: {landmark.address}\nDescription: {landmark.description}", reply_markup=saves_landmark_back())


@router.callback_query(F.data.startswith("saves_back_to_topic") | F.data.startswith("saves_back_to_landmarks"))
async def saves_back_to_topic(callback: CallbackQuery):
    user_id = callback.from_user.id
    if callback.data.startswith("saves_back_to_topic"):
        await callback.message.delete()
        await save(callback.message, user_id)
    elif callback.data.startswith("saves_back_to_landmarks"): 
        await save_landmarks(callback, user_id)