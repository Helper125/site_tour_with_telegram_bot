from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependency import get_db
from src.auth.hashing import get_current_user
from src.templates import templates
from .services import admin_panel, admin_users, user_more, edit_user_more, admin_lands, land_more, edition_land_more, cities, city_more, city_update_more


admin_router = APIRouter(prefix="/admin")


@admin_router.get("", response_class=HTMLResponse)
async def admin_get(request: Request, db: AsyncSession = Depends(get_db)):
    repo = await admin_panel(request, db)
    return templates.TemplateResponse(name="admin/admin.html", request=request, context={"repo":repo})

@admin_router.get("/users", response_class=HTMLResponse)
async def admin_user_get(request: Request, db: AsyncSession = Depends(get_db)):
    repo = await admin_users(request, db)
    return templates.TemplateResponse(name="admin/admin_users.html", request=request, context={"repo":repo})

@admin_router.get("/user/{username}", response_class=HTMLResponse)
async def user_more_get(username: str, request: Request, db: AsyncSession = Depends(get_db)):
    repo = await user_more(username, request, db)
    return templates.TemplateResponse(name="admin/more_user.html", request=request, context={"repo": repo})

@admin_router.post("/user/update/{username}")
async def update_user_get(username: str, new_username: str = Form(None), email: str = Form(None), is_admin: str = Form(None), db: AsyncSession = Depends(get_db)):
    repo = await edit_user_more(username, new_username, email, is_admin, db)

    return RedirectResponse(url=f"/LandmarksInLands/admin/user/{new_username or username}", status_code=302)

@admin_router.get("/lands", response_class=HTMLResponse)
async def admin_lands_more_get(request: Request, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    result = await admin_lands(sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/admin_lands.html", request=request, context={"result":result})

@admin_router.get("/land_more/{name}", response_class=HTMLResponse)
async def land_more_get(name: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await land_more(name, db)
    return templates.TemplateResponse(name="admin/land_more.html", request=request, context={"result":result})

@admin_router.post("/land/update/{name}")
async def land_update_post(name: str, new_name: str = Form(None), db: AsyncSession = Depends(get_db)):
    result = await edition_land_more(name, new_name, db)
    return RedirectResponse(url=f"/LandmarksInLands/admin/land_more/{new_name or name}", status_code=302)

@admin_router.get("/cities", response_class=HTMLResponse)
async def cities_get(reques: Request, sort_by: str = Query("id"), search_query: str = Query(None), db: AsyncSession = Depends(get_db)):
    result = await cities(sort_by, search_query, db)
    return templates.TemplateResponse(name="admin/cities.html", request=reques, context={"result":result})

@admin_router.get("/city_more/{name}", response_class=HTMLResponse)
async def city_more_get(name: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await city_more(name, db)
    return templates.TemplateResponse(name="admin/city_more.html", request=request, context={"result":result})

@admin_router.post("/city/update/{name}")
async def city_more_update(name: str, new_name: str = Form(None), land: str = Form(None), db: AsyncSession = Depends(get_db)):
    result = await city_update_more(name, new_name, land, db)
    return RedirectResponse(url=f"/LandmarksInLands/admin/city_more/{new_name or name}", status_code=302)

"""
    to finish land_more_get. make  new function "edit_land" and make more function with cities and landmarks
"""