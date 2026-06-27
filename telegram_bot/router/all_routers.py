from aiogram import Router
from telegram_bot.tours.routers import router
from telegram_bot.tours.site_date_in_telegram import router as site_router


routers = Router()

routers.include_router(router)
routers.include_router(site_router)