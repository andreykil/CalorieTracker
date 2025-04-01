from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from bot_commands import (
    router_start,
    router_search_global,
    router_set_goal,
    router_search_favorite,
    router_create_favorite,
    router_favorite_from_image,
    router_daily_stats
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router_start)
dp.include_router(router_set_goal)
dp.include_router(router_search_global)
dp.include_router(router_search_favorite)
dp.include_router(router_create_favorite)
dp.include_router(router_favorite_from_image)
dp.include_router(router_daily_stats)

# Запуск бота
if __name__ == "__main__":
    dp.run_polling(bot)
