import asyncio
import logging
import os
import sys
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import ADMIN_ID
from bot_instance import bot, set_admin_id
from database import init_db
from keep_alive import keep_alive

# Включаем подробное логирование
logging.basicConfig(level=logging.INFO)

print("🚀 Starting bot...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    keep_alive()
    print("✅ keep_alive started")
except Exception as e:
    print(f"❌ Error starting keep_alive: {e}")

try:
    set_admin_id(ADMIN_ID)
    print("✅ Admin ID set")
except Exception as e:
    print(f"❌ Error setting admin ID: {e}")

try:
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"❌ Error initializing DB: {e}")

dp = Dispatcher(storage=MemoryStorage())
print("✅ Dispatcher created")

from handlers import start, booking, admin
dp.include_router(start.router)
dp.include_router(booking.router)
dp.include_router(admin.router)
print("✅ Routers included")

async def main():
    print("🚀 Bot is starting polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Error in polling: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)