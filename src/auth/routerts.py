from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .schemas import Register, Login
from .repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependency import get_db
from .hashing import get_current_user
from src.templates import templates

auth_router = APIRouter()

@auth_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(name="auth/register.html", request=request)

@auth_router.post("/register", tags=["User"], summary="Register user")
async def register_user(data: Register, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    token = await repo.register(data)

    response = JSONResponse(content={"success": True})
    response.set_cookie(key="token", value=token, httponly=True, max_age=60 * 60 * 24, expires=60 * 60 * 24)
    return response

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(name="auth/login.html", request=request)

@auth_router.post("/login", tags=["User"], summary="Login user")
async def login_user(data: Login, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    token = await repo.login(data)

    response = JSONResponse(content={"success": True})
    response.set_cookie(key="token", value=token, httponly=True, max_age=60 * 60 * 24)
    return response

@auth_router.get("/logout")
async def logout_user():
    response = RedirectResponse(url="/LandmarksInLands/lands", status_code=302)
    response.delete_cookie(key="token")
    return response


@auth_router.get("/profile")
async def profile(user_id: int = Depends(get_current_user)):
    return {"user_id": user_id}