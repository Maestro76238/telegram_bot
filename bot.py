import asyncio
import logging
import os
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import ADMIN_ID
from bot_instance import bot, set_admin_id
from database import init_db
from keep_alive import keep_alive

keep_alive()

set_admin_id(ADMIN_ID)
init_db()

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=MemoryStorage())

from handlers import start, booking, admin

dp.include_router(start.router)
dp.include_router(booking.router)
dp.include_router(admin.router)

async def main():
    print("🚀 Бот запущен на Railway!")
    print(f"📊 ID администратора: {ADMIN_ID}")
    print(f"🌐 Порт: {os.environ.get('PORT', 'не указан')}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())