from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependency import get_db
from src.auth.hashing import get_current_user
from src.templates import templates
from .services import (admin_panel, admin_users, user_more, edit_user_more, admin_lands, all_lands, land_more, edition_land_more, city_more, city_update_more,
                       landmarks_more, landmarks_more_update, all_cities, all_city, all_landmarks, one_land_delete, land_delete, one_city_delete, city_delete, one_landmark_delete, 
                       landmarks_delete, one_user_delete, user_delete, user_add, land_add, city_add, landmarks_add)


admin_router = APIRouter(prefix="/admin")

async def check(request, session):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse("/LandmarksInLands/login")
    if not user.is_admin:
        return RedirectResponse("/LandmarksInLands/lands")
    
    return user



@admin_router.get("", response_class=HTMLResponse)
async def admin_get(request: Request, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await admin_panel(request, db)
    return templates.TemplateResponse(name="admin/admin.html", request=request, context={"repo":repo, "user":check_user})


@admin_router.get("/add_user", response_class=HTMLResponse)
async def page_add_user(request: Request):
    return templates.TemplateResponse(name="admin/users/add_user.html", request=request)


@admin_router.post("/add_user")
async def admin_add(request: Request, username: str = Form(None), email: str = Form(None), is_admin: bool = Form(False), password: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    
    repo = await user_add(username, email, is_admin, password, db)
    return RedirectResponse(url="/LandmarksInLands/admin/add_user", status_code=303)



@admin_router.get("/users", response_class=HTMLResponse)
async def admin_user_get(request: Request, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await admin_users(request, sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/users/admin_users.html", request=request, context={"repo":repo})


@admin_router.get("/user/{username}", response_class=HTMLResponse)
async def user_more_get(username: str, request: Request, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await user_more(username, request, db)
    return templates.TemplateResponse(name="admin/users/more_user.html", request=request, context={"repo": repo})


@admin_router.get("/one_user/delete/{user_id}")
async def delete_one_user(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)
    
    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await one_user_delete(user_id, db)
    return RedirectResponse("/LandmarksInLands/admin/users", status_code=303)


@admin_router.post("/user/delete")
async def delete_user_post(request: Request, user_id: List[int] = Form(...), action: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    users = await user_delete(user_id, action, db)
    return RedirectResponse("/LandmarksInLands/admin/users", status_code=303)


@admin_router.post("/user/update/{username}")
async def update_user_get(request: Request, username: str, new_username: str = Form(None), email: str = Form(None), is_admin: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await edit_user_more(username, new_username, email, is_admin, db)

    return RedirectResponse(url=f"/LandmarksInLands/admin/user/{new_username or username}", status_code=302)


@admin_router.get("/add_land", response_class=HTMLResponse)
async def page_add_land(request: Request):
    return templates.TemplateResponse(name="admin/lands/add_land.html", request=request)


@admin_router.post("/add_land")
async def admin_land_add(request: Request, name: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)
    if isinstance(check_user, RedirectResponse):
        return check_user
    
    repo = await land_add(name, db)
    return RedirectResponse("/LandmarksInLands/admin/lands", status_code=303)


@admin_router.get("/lands", response_class=HTMLResponse)
async def admin_lands_more_get(request: Request, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await admin_lands(sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/lands/admin_lands.html", request=request, context={"result":result})

@admin_router.get("/land_more/{name}", response_class=HTMLResponse)
async def land_more_get(name: str, request: Request, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await land_more(name, db)
    return templates.TemplateResponse(name="admin/lands/land_more.html", request=request, context={"result":result})


@admin_router.get("/one_land/delete/{land_id}")
async def delete_one_land(request: Request, land_id: int, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)
    
    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await one_land_delete(land_id, db)
    return RedirectResponse("/LandmarksInLands/admin/lands", status_code=303)


@admin_router.post("/land/delete")
async def lend_delete_past(request: Request, land_id: List[int] = Form(...), action: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    land = await land_delete(land_id, action, db)
    return RedirectResponse(url="/LandmarksInLands/admin/lands", status_code=303)


@admin_router.post("/land/update/{name}")
async def land_update_post(request: Request, name: str, new_name: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await edition_land_more(name, new_name, db)
    return RedirectResponse(url=f"/LandmarksInLands/admin/land_more/{new_name or name}", status_code=302)


@admin_router.get("/add_city")
async def page_city_add(request: Request, db: AsyncSession = Depends(get_db)):
    repo = await all_lands(db)
    return templates.TemplateResponse(name="admin/cities/add_cities.html", request=request, context={"repo":repo})


@admin_router.post("/add_city")
async def add_city(request: Request, land_id: int = Form(...), name: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await city_add(name, land_id, db)
    return RedirectResponse("/LandmarksInLands/admin/cities", status_code=303)
    

@admin_router.get("/cities", response_class=HTMLResponse)
async def all_cities_get(request: Request, page: int = 1, limit = 10, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await all_cities(page, limit, sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/cities/all_cities.html", request=request, context={"cities": result["item"], "stmt": result["stmt"], "page": result["page"], "limit": result["limit"], "pages": result["pages"]})


@admin_router.get("/city_more/{name}", response_class=HTMLResponse)
async def city_more_get(name: str, request: Request, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await city_more(name, db)
    return templates.TemplateResponse(name="admin/cities/city_more.html", request=request, context={"result":result["city"], "lands":result["lands"]})


@admin_router.get("/one_city/delete/{city_id}")
async def delete_one_city(request: Request, city_id: int, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)
    
    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await one_city_delete(city_id, db)
    return RedirectResponse("/LandmarksInLands/admin/cities", status_code=303)


@admin_router.post("/city/delete")
async def city_delete_post(request:Request, city_id: List[int] = Form(...), action: str = Form(None), db:AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await city_delete(city_id, action, db)
    return RedirectResponse("/LandmarksInLands/admin/cities", status_code=303)

@admin_router.post("/city/update/{name}")
async def city_more_update(request: Request, name: str, new_name: str = Form(None), land: int = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await city_update_more(name, new_name, land, db)
    return RedirectResponse(url=f"/LandmarksInLands/admin/city_more/{new_name or name}", status_code=302)


@admin_router.get("/add_landmarks")
async def page_landmark_add(request: Request, db: AsyncSession = Depends(get_db)):
    repo = await all_city(db)
    return templates.TemplateResponse(name="admin/landmarks/add_landmarks.html", request=request, context={"repo":repo})


@admin_router.post("/add_landmarks")
async def add_landmarks(request: Request, city_id: int = Form(...), name: str = Form(None), address: str = Form(None), description: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await landmarks_add(name, address, description, city_id, db)
    return RedirectResponse("/LandmarksInLands/admin/landmarks", status_code=303)


@admin_router.get("/landmarks", response_class=HTMLResponse)
async def all_landmarks_get(request: Request, page: int = 1, limit: int = 10, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await all_landmarks(page, limit, sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/landmarks/all_landmarks.html", request=request, context={"item": result["item"], "stmt":result["stmt"], "page":result["page"], "limit": result["limit"], "pages": result["pages"]})


@admin_router.get("/one_landmark/delete/{landmark_id}")
async def delete_one_landmarks(request: Request, landmark_id: int, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)
    
    if isinstance(check_user, RedirectResponse):
        return check_user
    repo = await one_landmark_delete(landmark_id, db)
    return RedirectResponse("/LandmarksInLands/admin/landmarks", status_code=303)


@admin_router.post("/landmark/delete")
async def landmark_delete_post(request: str, landmark_id: int = Form(...), action: str = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    land = await landmarks_delete(landmark_id, action, db)
    return RedirectResponse("/LandmarksInLands/admin/landmarks", status_code=303)


@admin_router.get("/landmark_more/{name}", response_class=HTMLResponse)
async def landmarks_more_get(request: Request, name: str, db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await landmarks_more(name, db)
    return templates.TemplateResponse(name="admin/landmarks/landmark_more.html", request=request, context={"result":result["stmt"], "cities": result["cities"]})

@admin_router.post("/landmark/update/{name}")
async def lanmarks_update_post(request: Request, name: str, new_name: str = Form(None), address: str = Form(None), description: str = Form(None), city: int = Form(None), db: AsyncSession = Depends(get_db)):
    check_user = await check(request, db)

    if isinstance(check_user, RedirectResponse):
        return check_user
    result = await landmarks_more_update(name, new_name, address, description, city, db)
    return RedirectResponse(url=f"/LandmarksInLands/admin/landmark_more/{new_name or name}", status_code=302)