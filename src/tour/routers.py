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
    repo_favorite = FavoriteLandsRepository(db)
    saved_ids = await repo_favorite.get_saved_ids(user.id)
    repo = LandsRepository(db)
    alls = await repo.get_all(page, limit, search_query)
    return templates.TemplateResponse(name="index.html", request=request, context={"alls":alls["item"], "total": alls["total"], "page": alls["page"], "limit": alls["limit"], "pages": alls["pages"], "user":user, "saved_ids": saved_ids})

@tours_router.get("/land/{land_name}", tags=["City"], response_class=HTMLResponse)
async def get_cities_by_land(request: Request, land_name: str, page: int = 1, limit = 10, search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    repo_favorite = FavoriteCityRepository(db)
    saved_ids = await repo_favorite.get_saved_ids(user.id)
    repo = CitiesRepository(db)
    alls = await repo.get_cities_by_land(land_name, page, limit, search_query)
    return templates.TemplateResponse(name="city.html", request=request, context={"alls":alls, "total": alls["total"], "page": alls["page"], "limit": alls["limit"], "pages": alls["pages"], "saved_ids":saved_ids})

@tours_router.get("/city/{city_name}", tags=["landmark"], response_class=HTMLResponse)
async def get_landmark_by_cities(request: Request, city_name: str, page: int = 1, limit = 10, search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    repo_favorite = FavoriteLandmarksRepository(db)
    saved_ids = await repo_favorite.get_saved_ids(user.id)
    repo = LandmarksRepository(db)
    alls = await repo.get_landmarks_by_city(city_name, page, limit, search_query)
    return templates.TemplateResponse(name="landmarks.html", request=request, context={"alls":alls, "total":alls["total"], "page":alls["page"], "limit":alls["limit"], "pages":alls["pages"], "land": alls["land"], "saved_ids":saved_ids})

@tours_router.get("/landmark/{landmark_name}")
async def get_landmark(request: Request, landmark_name: str, db: AsyncSession = Depends(get_db)):
    repository = LandmarksRepository(db)
    repo = await repository.get_one_landmark(landmark_name)
    return templates.TemplateResponse(name="landmark_more.html", request=request, context={"repo":repo})


@tours_router.get("/save", response_class=HTMLResponse)
async def all_lands_in_save(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    
    if not user:
        return RedirectResponse(url="/LandmarksInLands/login")
    
    land = FavoriteLandsRepository(db)
    stmt_land = await land.get_all(user.id)

    city = FavoriteCityRepository(db)
    stmt_city = await city.get_all(user.id)

    landmark = FavoriteLandmarksRepository(db)
    stmt_landmark = await landmark.get_all(user.id)

    return templates.TemplateResponse(name="save/all_save.html", request=request, context={"land":stmt_land, "city":stmt_city, "landmark":stmt_landmark})


@tours_router.post("/add-land-save")
async def add_land_save(request: Request, land_id: int = Form(None), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)

    if user:
        land = FavoriteLandsRepository(db)
        stmt_land = await land.add_land(user.id, land_id)
    else:
        return RedirectResponse(url="/LandmarksInLands/login")
    
    return RedirectResponse(url=f"{urls}", status_code=302)


@tours_router.post("/del-land-save")
async def del_land_save(request: Request, land_id: int = Form(None), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)

    if user:
        land = FavoriteLandsRepository(db)
        stmt_land = await land.del_land(user.id, land_id)
    else:
        return RedirectResponse(url="LandmarksInLands/login")
    
    return RedirectResponse(url=f"{urls}", status_code=302)


@tours_router.post("/add-city-save")
async def add_city_save(request: Request, city_id: int = Form(None), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)

    if not user:
        return RedirectResponse("/LandmarksInLands/login")
    
    city = FavoriteCityRepository(db)
    stmt_city = await city.add_city(user.id, city_id)

    return RedirectResponse(url=f"{urls}", status_code=302)

@tours_router.post("/del-city-save")
async def del_city_save(request: Request, city_id: int = Form(), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    
    if not user:
        return RedirectResponse("/LandmarksInLands/login")
    
    city = FavoriteCityRepository(db)
    stmt_city = await city.del_city(user.id, city_id)

    return RedirectResponse(url=f"{urls}", status_code=302)

@tours_router.post("/add-landmark-save")
async def add_landmark_save(request: Request, landmark_id: int = Form(None), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)

    if not user:
        return RedirectResponse("/LandmarksInLands/login")
    
    landmark = FavoriteLandmarksRepository(db)
    stmt_landmark = await landmark.add_landmark(user.id, landmark_id)

    return RedirectResponse(url=f"{urls}", status_code=302)

@tours_router.post("/del-landmark-save")
async def del_landmark_save(request: Request, landmark_id: int = Form(None), urls: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)

    if not user:
        return RedirectResponse("/LandmarksInlands/login")
    
    landmark = FavoriteLandmarksRepository(db)
    stmt_landmark = await landmark.del_landmark(user.id, landmark_id)

    return RedirectResponse(url=f"{urls}", status_code=302)