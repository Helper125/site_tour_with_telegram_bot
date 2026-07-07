from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .states import AddLand, AddCity, AddLandmark
from src.auth.hashing import hash_password, verify_password
from src.db.database import async_session
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..auth.models import User_tg
from src.auth.models import User
from src.tour.models import Lands, City, Landmarks, FavoriteLands, FavoriteCity, FavoriteLandmarks

from ..keyboards.InlineKeyboards import lands, cities, landmarks, back_landmark_to_landmarks, save_topic, saves_lands, saves_cities, saves_landmarks, saves_landmark_back, lands_for_AddCity, cities_for_AddLandmark

router = Router()

@router.message(Command("lands"))
async def all_lands(message: Message, new_page: int | None = None):
    async with async_session() as session:
        if new_page:
            page = new_page
        else:
            page = 1
        per_page = 5
        total = await session.scalar(select(func.count()).select_from(Lands))
        max_pages = (total + per_page - 1) // per_page
        land = await session.scalars(select(Lands).offset((page - 1) * per_page).limit(per_page))
        list_land = land.all()
        await message.answer(f"Lands page: {page}, max page: {max_pages}", reply_markup=lands(list_land, page, max_pages))


@router.callback_query(F.data.startswith("page_"))
async def lands_page(callback: CallbackQuery):
    page = int(callback.data.split("_"[1]))
    return await all_lands(callback, page)


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
        await callback.message.answer(f"Name: {landmark.name}\nAddress: {landmark.address}\nDescription: {landmark.description}", reply_markup=back_landmark_to_landmarks())


@router.callback_query(F.data.startswith("back_landmark"))
async def back_landmark():
    return all_lands()


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



@router.message(Command("add_land"))
async def add_land(message: Message, state: FSMContext):
    id_user = message.from_user.id
    async with async_session() as session:
        check = await session.scalar(select(User_tg).join(User_tg.user).options(selectinload(User_tg.user)).where(User_tg.tg_id == id_user, User_tg.login == True, User.is_admin == True))
        if not check:
            return None
        
        await state.set_state(AddLand.name)

        await message.answer("Enter the name of the new land")

@router.message(AddLand.name)
async def add_name_land(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("All stoped")
        return None
    
    await state.update_data(name=message.text)

    data = await state.get_data()

    async with async_session() as session:
        land = Lands(name=data["name"])
        session.add(land)
        await session.commit()

    await message.delete()
    await message.answer(f"Land {data["name"]} added successfully")
    await state.clear()


@router.message(Command("add_city"))
async def add_city(message: Message, state: FSMContext):
    state.clear()
    id_user = message.from_user.id
    async with async_session() as session:
        user = await session.scalar(select(User_tg).join(User_tg.user).options(selectinload(User_tg.user)).where(User_tg.tg_id == id_user, User_tg.login == True, User.is_admin == True))
        if not user:
            return None
        
        await state.set_state(AddCity.name)

        await message.answer("Enter the name of the new city")


@router.message(AddCity.name)
async def add_name_city(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("All stoped")
        return None
    
    await state.update_data(name=message.text)

    page = 1
    per_page = 5
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(Lands))
        max_page = (total + per_page - 1) // per_page
        land = await session.scalars(select(Lands).offset((page - 1) * per_page).limit(per_page))
        all_land = land.all()
        await message.answer(f"Lands page: {page}, max page: {max_page}", reply_markup=lands_for_AddCity(all_land, page, max_page))
        
        await state.get_state(AddCity.land_id)


@router.callback_query(F.data.startswith("AddCity_"))
async def add_land_id_city(callback: CallbackQuery, state: FSMContext):
    land_id = int(callback.data.split("_")[1])

    await state.update_data(land_id=land_id)

    data = await state.get_data()

    async with async_session() as session:
        city = City(name=data["name"], land_id=data["land_id"])
        session.add(city)
        await session.commit()
        
        await callback.message.answer(f"All correct. New city: {data["name"]}")
        
    await state.clear()


@router.message(Command("add_landmark"))
async def add_landmark(message: Message, state: FSMContext):
    await state.clear()
    id_user = message.from_user.id

    async with async_session() as session:
        user = await session.scalar(select(User_tg).join(User_tg.user).options(selectinload(User_tg.user)).where(User_tg.tg_id == id_user, User_tg.login == True, User.is_admin == True))
        if not user:
            return None
        
        await state.set_state(AddLandmark.name)

        await message.answer("Enter the name of the landmark")

@router.message(AddLandmark.name)
async def add_name_landmark(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return None

    await state.update_data(name=message.text)
    await state.set_state(AddLandmark.address)

    await message.answer("Enter the address of the landmark")


@router.message(AddLandmark.address)
async def add_address_landmark(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return None
    
    await state.update_data(address=message.text)
    await state.set_state(AddLandmark.description)

    await message.answer("Enter the description of the landmark")


@router.message(AddLandmark.description)
async def add_description_landmark(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.delete()
        await message.answer("all stoped")
        return None

    await state.update_data(description=message.text)
    await state.set_state(AddLandmark.city_id)

    page = 1
    per_page = 5
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(City))
        max_page = (total - per_page - 1) // per_page
        city = await session.scalars(select(City).offset((page - 1) * per_page).limit(per_page))
        cities = city.all()

        await message.answer("Choise city", reply_markup=cities_for_AddLandmark(cities, page, max_page))


@router.callback_query(F.data.startswith("AddLandmark_"))
async def add_city_id_landmark(callback: CallbackQuery, state: FSMContext):
    city_id = int(callback.data.split("_")[1])

    await state.update_data(city_id=city_id)
    data = await state.get_data()
    async with async_session() as session:
        landmark = Landmarks(name=data["name"], address=data["address"], description=data["description"], city_id=data["city_id"])
        session.add(landmark)
        await session.commit()

        await callback.message.answer(f"All correct. New landmark: {data["name"]}")

    await state.clear()




# TODO