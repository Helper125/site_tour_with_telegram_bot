from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from .models import *
from .schemas import LandCreate, LandUpdate, CityCreate, CityUpdate, LandmarkCreate, LandmarkUpdate
from fastapi import HTTPException


class LandsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page: int, limit: int, search_query: str):
        offset = (page - 1) * limit

        query = select(Lands)
        count_stmt = select(func.count()).select_from(Lands)
        if search_query:
            condition = Lands.name.ilike(f"%{search_query}%")

            query = query.where(condition)
            count_stmt = count_stmt.where(condition)

        total = await self.db.scalar(count_stmt)

        lands = await self.db.scalars(query.offset(offset).limit(limit))

        return {
            "item": lands.all(),
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + page - 1) // limit
        }

    
    async def get_one(self, data: str):
        correct_text = data.lower().title()
        stmt = select(Lands).where(Lands.name == correct_text)
        result = await self.db.scalars(stmt)
        return result.all()


class CitiesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self, page: int, limit: int, search_query: str):
        offset = (page - 1) * limit

        query = select(City)
        count_stmt = select(func.count()).select_from(City)

        if search_query:
            condition = City.name.ilike(f"%{search_query}%")

            query = query.where(condition)
            count_stmt = count_stmt.where(condition)

        total = await self.db.scalar(count_stmt)

        city = await self.db.scalars(query.offset(offset).limit(limit))

        return {
            "item": city.all(),
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + page - 1) // limit
        }

    async def get_cities_by_land(self, land_name: str, page: int, limit: int, search_query: str):
        offset = (page - 1) * limit

        query = select(City).join(City.land).where(Lands.name == land_name)
        count_stmt = select(func.count()).select_from(City).join(City.land).where(Lands.name == land_name)

        if search_query:
            condition = City.name.ilike(f"%{search_query}%")

            query = query.where(condition)
            count_stmt = count_stmt.where(condition)

        total = await self.db.scalar(count_stmt)

        city = await self.db.scalars(query.offset(offset).limit(limit))

        return {
            "cities": city.all(),
            "land": land_name,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    

class LandmarksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self, page: int = 1, limit = 100):
        if page < 1:
            page = 1
        skip = (page - 1) * limit

        total = await self.db.scalar(select(func.count()).select_from(Landmarks))

        stmt = select(Landmarks).offset(skip).limit(limit)
        result = await self.db.scalars(stmt)
        items = result.all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": -(-total // limit)
        }
    
    async def get_landmarks_by_city(self, city_name: str, page:int, limit: int, search_query: str):
        offset = (page - 1) * limit

        query = select(Landmarks).options(selectinload(Landmarks.city).selectinload(City.land)).join(Landmarks.city).where(City.name == city_name)
        count_stmt = select(func.count()).select_from(Landmarks).join(Landmarks.city).where(City.name == city_name)

        if search_query:
            condition = Landmarks.name.ilike(f"%{search_query}%")

            query = query.where(condition)
            count_stmt = count_stmt.where(condition)

        total = await self.db.scalar(count_stmt)

        landmarks = await self.db.scalars(query.offset(offset).limit(limit))
        result = landmarks.all()


        
        return {
            "landmarks": result,
            "city": city_name,
            "land": result[0].city.land.name,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1 ) // limit
            }
    
    async def get_one_landmark(self, landmark_name: str):
        stmt = await self.db.scalar(select(Landmarks).options(selectinload(Landmarks.city)).where(Landmarks.name == landmark_name))
        return stmt
    

class FavoriteLandsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id):
        stmt = await self.db.scalars(select(FavoriteLands).options(selectinload(FavoriteLands.land)).where(FavoriteLands.user_id == user_id))
        return {"stmt": stmt.all()}
    
    async def add_land(self, user_id, land_id):
        land = FavoriteLands(land_id=land_id, user_id=user_id)
        
        self.db.add(land)
        await self.db.commit()

        return land

    async def del_land(self, user_id, land_id):
        land = await self.db.scalar(select(FavoriteLands).where(FavoriteLands.user_id == user_id, FavoriteLands.land_id == land_id))

        if land:
            await self.db.delete(land)
            await self.db.commit()

        return land


class FavoriteCityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id):
        stmt = await self.db.scalars(select(FavoriteCity).options(selectinload(FavoriteCity.city)).where(FavoriteCity.user_id == user_id))
        return {"stmt": stmt.all()}
    
    async def add_city(self, user_id, city_id):
        city = FavoriteCity(city_id=city_id, user_id=user_id)

        if city:
            self.db.add(city)
            await self.db.commit()

        return city
    
    async def del_city(self, user_id, city_id):
        city = await self.db.scalars(select(FavoriteCity).where(FavoriteCity.user_id == user_id, FavoriteCity.city_id == city_id))

        if city:
            await self.db.delete(city)
            await self.db.commit()

        return city
    

class FavoriteLandmarksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id):
        stmt = await self.db.scalars(select(FavoriteLandmarks).options(FavoriteLandmarks.landmark).where(FavoriteLandmarks.user_id == user_id))

        return {"stmt": stmt.all()}
    
    async def add_landmark(self, user_id, landmark_id):
        landmark = FavoriteLandmarks(user_id=user_id, landmark_id=landmark_id)

        if landmark:
            self.db.add(landmark)
            await self.db.commit()
        
        return landmark

    async def del_landmark(self, user_id, landmark_id):
        landmark = FavoriteLandmarks(user_id=user_id, landmark_id=landmark_id)

        if landmark:
            await self.db.delete(landmark)
            await self.db.commit()

        return landmark