from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from dotenv import load_dotenv
import os

load_dotenv()

password = os.getenv("PG_PASSWORD")
hostname = os.getenv("PG_HOSTNAME")
username = os.getenv("PG_USERNAME")
dbname = os.getenv("PG_BDNAME")
port = os.getenv("PG_PORT")

DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{hostname}:{port}/{dbname}"
print("Connecting to:", DATABASE_URL)

engine = create_async_engine(DATABASE_URL, connect_args={"ssl": False})

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass



# all basedatas, for create db in postgresql
from src.auth.models import *
from src.tour.models import *