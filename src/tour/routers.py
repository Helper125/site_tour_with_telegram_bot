from .services import home
from .repository import LandsRepository, CitiesRepository, LandmarksRepository
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import LandCreate, LandUpdate, CityCreate, CityUpdate, LandmarkCreate, LandmarkUpdate
from ..db.dependency import get_db
from src.templates import templates
from src.auth.hashing import get_current_user


tours_router = APIRouter()

@tours_router.get("/", response_class=HTMLResponse)
async def get_home(request:Request, db: AsyncSession = Depends(get_db)):
    homes = await home(db)
    # return templates.TemplateResponse(name="index.html", request=request, context={"homes":homes})


@tours_router.get("/all_land", tags=["Land"], summary="all lands", response_class=HTMLResponse)
async def all_Land(request: Request, page: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    repo = LandsRepository(db)
    alls = await repo.get_all(page, limit)
    return templates.TemplateResponse(name="index.html", request=request, context={"alls":alls["items"], "user":user})

@tours_router.post("/add_land", response_model=LandUpdate, tags=["Land"], summary="add land")
async def add_Land(data: LandCreate, db: AsyncSession = Depends(get_db)):
    repo = LandsRepository(db)
    return await repo.create(data)

@tours_router.patch("/update_land", response_model=LandUpdate, tags=["Land"], summary="update land")
async def update_Land(id: int, data: LandUpdate, db: AsyncSession = Depends(get_db)):
    repo = LandsRepository(db)
    return await repo.update(id, data)


@tours_router.delete("/delete_land/{id}", tags=["Land"], summary="delete land")
async def delete_Land(id: int, db: AsyncSession = Depends(get_db)):
    repo = LandsRepository(db)
    return await repo.delete(id)

@tours_router.get("/all_city", tags=["City"], summary="all city")
async def all_city(page: int, limit: int, db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    return await repo.get_all(page, limit)

@tours_router.post("/add_city", response_model=CityUpdate, tags=["City"], summary="add city")
async def add_city(data: CityCreate, db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    return await repo.create(data)

@tours_router.patch("/update_city", response_model=CityUpdate, tags=["City"], summary="update city")
async def update_city(id: int, data: CityUpdate, db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    return await repo.update(id, data)

@tours_router.delete("/delete_city", tags=["City"], summary="delete city")
async def delete_city(id: int, db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    return await repo.delete(id)

@tours_router.get("/all_landmark", tags=["landmark"], summary="all landmark")
async def all_landmark(page: int, limit: int, db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    return await repo.get_all(page, limit)

@tours_router.post("/add_landmark", response_model=LandmarkCreate, tags=["landmark"], summary="add landmark")
async def add_landmark(data: LandmarkCreate, db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    return await repo.create(data)

@tours_router.patch("/update_landmark", response_model=LandmarkUpdate, tags=["landmark"], summary="update landmark")
async def update_landmark(id: int, data: LandmarkUpdate, db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    return await repo.update(id, data)

@tours_router.delete("/delete_landmark", tags=["landmark"], summary="delete landmark")
async def delete_landmark(id: int, db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    return await repo.delete(id)


@tours_router.get("/land/{land_name}", tags=["City"])
async def get_cities_by_land(request: Request, land_name: str, db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    alls = await repo.get_cities_by_land(land_name)
    return templates.TemplateResponse(name="city.html", request=request, context={"alls":alls})

@tours_router.get("/city/{city_name}", tags=["landmark"])
async def get_landmark_by_cities(request: Request, city_name: str, db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    alls = await repo.get_landmarks_by_city(city_name)
    return templates.TemplateResponse(name="landmarks.html", request=request, context={"alls":alls})

@tours_router.get("/get_land/{land_name}", tags=["Land"])
async def get_one_land(land_name: str, db: AsyncSession = Depends(get_db)):
    repo = LandsRepository(db)
    return await repo.get_one(land_name)