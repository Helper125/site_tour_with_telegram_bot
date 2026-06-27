import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from telegram_bot.router.all_routers import routers

from src.db.database import engine, Base

load_dotenv()

TOKEN_TELEGRAM = getenv("TELEGRAM_BOT_TOKEN")
print(TOKEN_TELEGRAM)
dp = Dispatcher()

dp.include_router(routers)

async def db_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main() -> None:
    await db_create()
    
    bot = Bot(token=TOKEN_TELEGRAM)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())