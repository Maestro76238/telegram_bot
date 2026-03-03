import asyncio
import logging
import os
import sys
from flask import Flask
from threading import Thread

# ================== НАСТРОЙКА ЛОГИРОВАНИЯ ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🚀 ЗАПУСК БОТА НА RAILWAY")
print("=" * 60)

# ================== FLASK ДЛЯ HEALTHCHECK ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! 🚀"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# Запускаем Flask в отдельном потоке
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
logger.info("✅ Flask сервер запущен")

# ================== ИМПОРТЫ AIOGRAM ==================
try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Message
    from aiogram.filters import Command
    from aiogram.fsm.storage.memory import MemoryStorage
    logger.info("✅ aiogram импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка импорта aiogram: {e}")
    sys.exit(1)

# ================== ПРОВЕРКА ПЕРЕМЕННЫХ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    logger.error("❌ ADMIN_ID не найден в переменных окружения!")
    sys.exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)
    logger.info(f"✅ ADMIN_ID: {ADMIN_ID}")
except ValueError:
    logger.error(f"❌ ADMIN_ID должен быть числом, получено: {ADMIN_ID}")
    sys.exit(1)

logger.info(f"✅ BOT_TOKEN: {BOT_TOKEN[:10]}...")

# ================== СОЗДАНИЕ БОТА ==================
try:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    logger.info("✅ Бот и диспетчер созданы")
except Exception as e:
    logger.error(f"❌ Ошибка создания бота: {e}")
    sys.exit(1)

# ================== ОБРАБОТЧИКИ ==================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Я бот для салона красоты.\n"
        f"🆔 Твой ID: {message.from_user.id}"
    )

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 Ты администратор!")
    else:
        await message.answer("⛔ У тебя нет прав администратора.")

@dp.message()
async def echo_all(message: Message):
    await message.answer(f"Ты написал: {message.text}")

# ================== ЗАПУСК ==================
async def main():
    logger.info("🚀 Запуск polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Вебхук удалён")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка в polling: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        # Держим процесс живым для Flask
        import time
        while True:
            time.sleep(10)