from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from .models import *
from .schemas import LandCreate, LandUpdate, CityCreate, CityUpdate, LandmarkCreate, LandmarkUpdate
from fastapi import HTTPException


class LandsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: LandCreate):
        existing = await self.db.scalar(select(Lands).where(Lands.name == data.name))
        if existing:
            raise HTTPException(status_code=400, detail="Already exists")
        land = Lands(**data.model_dump())
        self.db.add(land)
        await self.db.flush()
        return land

    async def get_all(self, page: int = 0, limit: int = 100):
        if page < 1:
            page = 1
        skip = (page - 1) * limit

        total = await self.db.scalar(select(func.count()).select_from(Lands))

        stmt = select(Lands).offset(skip).limit(limit)
        result = await self.db.scalars(stmt)
        items = result.all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": -(-total // limit)
        }
    
    
    async def get_one(self, data: str):
        correct_text = data.lower().title()
        stmt = select(Lands).where(Lands.name == correct_text)
        result = await self.db.scalars(stmt)
        return result.all()
    
    async def update(self, id: int, data: LandUpdate):
        lands = await self.db.get(Lands, id)
        if not lands:
            raise HTTPException(status_code=404, detail="Not found")
        lands.name = data.name
        return lands
    
    async def delete(self, id: int):
        lands = await self.db.get(Lands, id)
        if not lands:
            raise HTTPException(status_code=404, detail="Not found")
        await self.db.delete(lands)
        return True


class CitiesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CityCreate):
        existing = await self.db.scalar(select(City).where(City.name == data.name))
        if existing:
            raise HTTPException(status_code=400, detail="Already exists")
        city = City(**data.model_dump())
        self.db.add(city)
        await self.db.flush()
        return city
    
    async def get_all(self, page: int = 0, limit: int = 100):
        if page < 1:
            page = 1
        skip = (page - 1) * limit

        total = await self.db.scalar(select(func.count()).select_from(City))

        stmt = select(City).offset(skip).limit(limit)
        result = await self.db.scalars(stmt)
        items = result.all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": -(-total // limit)
        }
    
    
    async def update(self, id: int, data: CityUpdate):
        cities = await self.db.get(City, id)
        if not cities:
            raise HTTPException(status_code=404, detail="Not found")
        cities.name = data.name
        cities.land_id = data.land_id
        return cities
    
    async def delete(self, id: int | str):
        cities = await self.db.get(City, id)
        if not cities:
            raise HTTPException(status_code=404, detail="Not found")
        await self.db.delete(cities)
        return True

    async def get_cities_by_land(self, land_name: str):
        stmt = select(City).join(City.land).where(Lands.name.ilike(land_name))
        result = await self.db.scalars(stmt)
        cities = result.all()

        if not cities:
            raise HTTPException(status_code=404, detail="Not found")

        return {
            "cities": cities,
            "land": land_name
        }
    

class LandmarksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: LandmarkCreate):
        existing = await self.db.scalar(select(Landmarks).where(Landmarks.name == data.name))
        if existing:
            raise HTTPException(status_code=400, detail="Already exists")
        landmarks = Landmarks(**data.model_dump())
        self.db.add(landmarks)
        await self.db.flush()
        return landmarks
    
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
    
    async def update(self, id: int, data: LandmarkUpdate):
        landmarks = await self.db.get(Landmarks, id)
        if not landmarks:
            raise HTTPException(status_code=404, detail="Not found")
        landmarks.name = data.name
        landmarks.address = data.address
        landmarks.description = data.description
        landmarks.city_id = data.city_id
        return landmarks
    
    async def delete(self, id: int):
        landmarks = await self.db.get(Landmarks, id)
        if not landmarks:
            raise HTTPException(status_code=404, detail="Not found")
        
        await self.db.delete(landmarks)
        return True
    
    async def get_landmarks_by_city(self, city_name: str):
        stmt = select(Landmarks).join(Landmarks.city).where(City.name.ilike(city_name))
        result = await self.db.scalars(stmt)
        landmarks = result.all()

        if not landmarks:
            raise HTTPException(status_code=404, detail="Not found")
        
        return {
            "landmarks": landmarks,
            "city": city_name
            }
