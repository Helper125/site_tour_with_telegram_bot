from .services import home
from .repository import LandsRepository, CitiesRepository, LandmarksRepository, FavoriteLandsRepository, FavoriteCityRepository, FavoriteLandmarksRepository
from fastapi import APIRouter, Depends, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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


@tours_router.get("/lands", tags=["Land"], summary="all lands", response_class=HTMLResponse)
async def all_Land(request: Request, page: int = 1, limit: int = 3, search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    repo = LandsRepository(db)
    alls = await repo.get_all(page, limit, search_query)
    return templates.TemplateResponse(name="index.html", request=request, context={"alls":alls["item"], "total": alls["total"], "page": alls["page"], "limit": alls["limit"], "pages": alls["pages"], "user":user})

@tours_router.get("/land/{land_name}", tags=["City"], response_class=HTMLResponse)
async def get_cities_by_land(request: Request, land_name: str, page: int = 1, limit = 10, search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    repo = CitiesRepository(db)
    alls = await repo.get_cities_by_land(land_name, page, limit, search_query)
    return templates.TemplateResponse(name="city.html", request=request, context={"alls":alls, "total": alls["total"], "page": alls["page"], "limit": alls["limit"], "pages": alls["pages"]})

@tours_router.get("/city/{city_name}", tags=["landmark"], response_class=HTMLResponse)
async def get_landmark_by_cities(request: Request, city_name: str, page: int = 1, limit = 10, search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    repo = LandmarksRepository(db)
    alls = await repo.get_landmarks_by_city(city_name, page, limit, search_query)
    return templates.TemplateResponse(name="landmarks.html", request=request, context={"alls":alls, "total":alls["total"], "page":alls["page"], "limit":alls["limit"], "pages":alls["pages"], "land": alls["land"]})

@tours_router.get("/landmark/{landmark_name}")
async def get_landmark(request: Request, landmark_name: str, db: AsyncSession = Depends(get_db)):
    repository = LandmarksRepository(db)
    repo = await repository.get_one_landmark(landmark_name)
    return templates.TemplateResponse(name="landmark_more.html", request=request, context={"repo":repo})

@tours_router.get("/save", response_class=HTMLResponse)
async def all_lands_in_save(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    
    if user:

        land = FavoriteLandsRepository(db)
        stmt_land = land.get_all(user.id)

        city = FavoriteCityRepository(db)
        stmt_city = city.get_all(user.id)

        landmark = FavoriteLandmarksRepository(db)
        stmt_landmark = landmark.get_all(user.id)
    else:
        return RedirectResponse(url="/LandmarksInLands/login")

    return templates.TemplateResponse(name="save/all_save.html", request=request, context={"land":stmt_land, "city":stmt_city, "landmark":stmt_landmark})