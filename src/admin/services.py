from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import Depends, Request, Form
from ..db.dependency import get_db
from src.auth.hashing import get_current_user
from src.auth.models import User
from src.tour.models import Lands, City, Landmarks
from .schemas import UserCreate, LandCreate, CityCreate, LandmarkCreate
from typing import List
from src.auth.hashing import hash_password


async def admin_panel(request: Request, session: AsyncSession = Depends(get_db)):
    users_check = await get_current_user(request, session)
    return users_check


async def user_add(username: str, email: str, is_admin: bool, password: str, session: AsyncSession = Depends(get_db)):
    data = UserCreate(
        username=username,
        email=email,
        is_admin=is_admin,
        password=hash_password(password)
    )
    user = User(username=data.username, email=data.email, is_admin=data.is_admin, password=password)
    session.add(user)

    return user


async def admin_users(request: Request, sort_by: str, search_query: str, session: AsyncSession = Depends(get_db)):
    users = select(User)

    if search_query:
        users = users.where(User.username.ilike(f"%{search_query}%"))

    if sort_by == "username":
        users = users.order_by(User.username)
    else:
        users = users.order_by(User.id)

    stmt = await session.scalars(users)
    return stmt.all()


async def user_more(username: str, request: Request, session: AsyncSession = Depends(get_db)):
    user = await session.scalar(select(User).where(User.username == username))
    result = user
    
    return result


async def one_user_delete(user_id: int, session: AsyncSession):
    user = await session.scalar(select(User).where(User.id == user_id))
    await session.delete(user)
    await session.commit()
    return user


async def user_delete(user_id: List[int], action: str, session: AsyncSession):
    if action == "delete_objects":
        users = await session.scalars(select(User).where(User.id.in_(user_id)))

        for user in users:
            await session.delete(user)
        await session.commit()
        return user
    else:
        pass


async def edit_user_more(username: str, new_username: str = Form(None), email: str = Form(None), is_admin: str = Form(None), session: AsyncSession = Depends(get_db)):
    user = await session.scalar(select(User).where(User.username == username))
    
    if username:
        user.username = new_username
    
    if email:
        user.email = email
    
    user.is_admin = is_admin == "true"

    await session.flush()

    return user


async def land_add(name: str, session: AsyncSession):
    data = LandCreate(
        name=name
    )
    land = Lands(name=data.name)
    session.add(land)
    return land


async def admin_lands(sort_by: str, search_query: str, session: AsyncSession = Depends(get_db)):
    stmt = select(Lands)

    if search_query:
        stmt = stmt.where(Lands.name.ilike(f"%{search_query}%"))

    if sort_by == "id":
        stmt = stmt.order_by(Lands.id)
    else:
        stmt = stmt.order_by(Lands.name)

    result = await session.scalars(stmt)
    return result


async def all_lands(session: AsyncSession):
    repo = await session.scalars(select(Lands))
    lands = repo.all()

    return lands


async def land_more(name: str, session: AsyncSession):
    land = await session.scalar(select(Lands).where(Lands.name == name))
    return land


async def one_land_delete(land_id: int, session: AsyncSession):
    land = await session.scalar(select(Lands).where(Lands.id == land_id))
    await session.delete(land)
    await session.commit()
    return land


async def land_delete(land_id: List[int], action: str, session: AsyncSession):
    if action == "delete_objects":
        lands = await session.scalars(select(Lands).where(Lands.id.in_(land_id)))

        for land in lands:
            await session.delete(land)
        await session.commit()
        return land
    else:
        pass


async def edition_land_more(name: str, new_name: str = Form(None), session: AsyncSession = Depends(get_db)):
    land = await session.scalar(select(Lands).where(Lands.name == name))

    if new_name:
        land.name = new_name
    
    await session.commit()
    await session.refresh(land)
    return land


async def city_add(name: str, land_id: int, session: AsyncSession):
    data = CityCreate(
        name=name,
        land_id=land_id
    )

    city = City(name=data.name, land_id=data.land_id)

    session.add(city)
    return city


async def all_cities(page: int, limit: int, sort_by: str, search_query: str, session: AsyncSession):
    offset = (page - 1) * limit

    query = select(City).options(selectinload(City.land))
    count_stmt = select(func.count()).select_from(City)

    if search_query :
        condition = City.name.ilike(f"%{search_query}%")

        query = query.where(condition)
        count_stmt = count_stmt.where(condition)
    
    if sort_by == "name":
        query = query.order_by(City.name)
    else:
        query = query.order_by(City.id)
    
    total = await session.scalar(count_stmt)
    
    cities = await session.scalars(query.offset(offset).limit(limit))

    return {
        "item": cities.all(),
        "stmt": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


async def all_city(session: AsyncSession):
    repo = await session.scalars(select(City))
    cities = repo.all()
    return cities


async def city_more(name: str, session: AsyncSession):
    city = await session.scalar(select(City).options(selectinload(City.land)).where(City.name == name))
    lands = await session.scalars(select(Lands))

    return {"city": city, "lands": lands}


async def one_city_delete(city_id: int, session: AsyncSession):
    city = await session.scalar(select(City).where(City.id == city_id))
    await session.delete(city)
    await session.commit()
    return city


async def city_delete(city_id: List[int], action: str, session: AsyncSession):

    if action == "delete_objects":
        cities = await session.scalars(select(City).where(City.id.in_(city_id)))

        for city in cities:
            await session.delete(city)

        await session.commit()
        return city
    else:
        pass
    

async def city_update_more(name: str, new_name: str, land: int, session: AsyncSession):

    city = await session.scalar(select(City).options(selectinload(City.land)).where(City.name == name))

    if not city:
        return None

    if new_name:
        city.name = new_name

    if land:
        city.land_id = land

    await session.commit()
    await session.refresh(city)

    return city


async def landmarks_add(name: str, address: str, description: str, city_id: int, session: AsyncSession):
    data = LandmarkCreate(
        name=name,
        address=address,
        description=description,
        city_id=city_id
    )

    landmarks = Landmarks(name=data.name, address=data.address, description=data.description, city_id=data.city_id)
    session.add(landmarks)
    return landmarks


async def all_landmarks(page: int, limit: int, sort_by: str, search_query: str, session: AsyncSession):
    offset = (page - 1) * limit

    query = select(Landmarks).options(selectinload(Landmarks.city))
    count_stmt = select(func.count()).select_from(Landmarks)
    if search_query:
        condition = Landmarks.name.ilike(f"%{search_query}%")

        query = query.where(condition)
        count_stmt = count_stmt.where(condition)

    if sort_by == "name":
        query = query.order_by(Landmarks.name)
    else:
        query = query.order_by(Landmarks.id)

    total = await session.scalar(count_stmt)

    landmarks = await session.scalars(query.offset(offset).limit(limit))

    return {
        "item": landmarks.all(),
        "stmt": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


async def landmarks_more(name: str, session: AsyncSession):
    stmt = await session.scalar(select(Landmarks).options(selectinload(Landmarks.city)).where(Landmarks.name == name))
    all_cities = await session.scalars(select(City))
    return {"stmt": stmt, "cities": all_cities}


async def one_landmark_delete(landmark_id: int, session: AsyncSession):
    landmark = await session.scalar(select(Landmarks).where(Landmarks.id == landmark_id))
    await session.delete(landmark)
    await session.commit()
    return landmark


async def landmarks_delete(landmark_id: int, action: str, session: AsyncSession):
    if action == "delete_objects":
        landmarks = await session.scalars(select(Landmarks).where(Landmarks.id.in_(landmark_id)))

        for landmark in landmarks:
            await session.delete(landmark)

        await session.commit()
        return landmark
    else:
        pass


async def landmarks_more_update(name: str, new_name: str, address: str, description: str, city: int, session: AsyncSession):
    stmt = await session.scalar(select(Landmarks).options(selectinload(Landmarks.city)).where(Landmarks.name == name))

    if new_name:
        stmt.name = new_name

    if address:
        stmt.address = address
    
    if description:
        stmt.description = description
    
    if city:
        stmt.city_id = int(city)

    await session.commit()
    await session.refresh(stmt)
    return stmt