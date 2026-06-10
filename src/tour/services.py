from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends, Request
from .schemas import LandCreate, LandmarkUpdate
from ..db.dependency import get_db
from .models import FavoriteLands, FavoriteCity, FavotiteLandmarks
# from main import templates

async def home(session: AsyncSession):
    hello = "Hello FastAPI"
    return hello
    # return templates.TemplateResponse("index.html", {"request", request})
