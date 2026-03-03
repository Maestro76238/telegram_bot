import asyncio
import logging
import os
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import ADMIN_ID
from bot_instance import bot, set_admin_id
from database import init_db, add_user, get_all_bookings
from keep_alive import keep_alive

# Запускаем веб-сервер для Railway
keep_alive()

set_admin_id(ADMIN_ID)

# Инициализация базы данных
print("🔄 Инициализация базы данных...")
init_db()

# Добавляем тестовые данные, если база пустая
from database import get_all_users, get_all_bookings
if len(get_all_users()) == 0:
    print("🔄 Добавляем тестового администратора...")
    add_user(ADMIN_ID, "admin", "Administrator")
    print("✅ Тестовый администратор добавлен")

if len(get_all_bookings()) == 0:
    print("🔄 Добавляем тестовую запись...")
    from database import save_booking
    save_booking(ADMIN_ID, "💇 Тестовая запись", "15.03.2026", "14:00")
    print("✅ Тестовая запись добавлена")

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=MemoryStorage())

from handlers import start, booking, admin

dp.include_router(start.router)
dp.include_router(booking.router)
dp.include_router(admin.router)

async def main():
    print("=" * 50)
    print("🚀 БОТ ЗАПУЩЕН НА RAILWAY")
    print("=" * 50)
    print(f"📊 ID администратора: {ADMIN_ID}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    
    # Проверяем наличие базы
    if os.path.exists('salon.db'):
        size = os.path.getsize('salon.db')
        print(f"✅ Файл базы данных найден, размер: {size} байт")
    else:
        print(f"❌ Файл базы данных НЕ найден!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())