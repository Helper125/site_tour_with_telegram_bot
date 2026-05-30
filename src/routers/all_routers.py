from fastapi import APIRouter
from src.tour.routers import tours_router
from src.auth.routerts import auth_router
from src.admin.routers import admin_router

routers = APIRouter()

routers.include_router(tours_router)
routers.include_router(auth_router)
routers.include_router(admin_router)