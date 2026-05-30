from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import Depends, Request, Form
from ..db.dependency import get_db
from src.auth.hashing import get_current_user
from src.auth.models import User
from src.tour.models import Lands, City
from .schemas import UserSchemas


async def admin_panel(request: Request, session: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, session)
    return user


async def admin_users(request: Request, session: AsyncSession = Depends(get_db)):
    users = select(User).order_by(User.id)
    stmt = await session.scalars(users)
    result = stmt.all()
    return result


async def user_more(username: str, request: Request, session: AsyncSession = Depends(get_db)):
    user = await session.scalar(select(User).where(User.username == username))
    result = user
    
    return result


async def edit_user_more(username: str, new_username: str = Form(None), email: str = Form(None), is_admin: str = Form(None), session: AsyncSession = Depends(get_db)):
    user = await session.scalar(select(User).where(User.username == username))

    if username:
        user.username = new_username
    
    if email:
        user.email = email
    
    user.is_admin = is_admin == "true"

    await session.flush()

    return user


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


async def land_more(name: str, session: AsyncSession = Depends(get_db)):
    land = await session.scalar(select(Lands).where(Lands.name == name))
    return land


async def edition_land_more(name: str, new_name: str = Form(None), session: AsyncSession = Depends(get_db)):
    land = await session.scalar(select(Lands).where(Lands.name == name))

    if new_name:
        land.name = new_name
    
    await session.flush()
    return land



async def cities(sort_by: str, search_query: str, session: AsyncSession):
    stmt =  select(City).options(selectinload(City.land))

    if search_query:
        stmt = stmt.where(City.name.ilike(f"%{search_query}%"))
        
    if sort_by == "id":
        stmt = stmt.order_by(City.id)
    else:
        stmt = stmt.order_by(City.name)

    result = await session.scalars(stmt)
    return result.all()
    
async def city_more(name: str, session: AsyncSession):
    city = await session.scalar(select(City).options(selectinload(City.land)).where(City.name == name))
    return city
    
async def city_update_more(name: str, new_name: str, land: str, session: AsyncSession):

    city = await session.scalar(select(City).options(selectinload(City.land)).where(City.name == name))

    if not city:
        return None

    if new_name:
        city.name = new_name

    if land:
        land_obj = await session.scalar(
            select(Lands).where(Lands.name == land)
        )

        if land_obj:
            city.land = land_obj

    await session.commit()
    await session.refresh(city)

    return city