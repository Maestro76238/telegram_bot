import os
import sys

# Токен бота (из переменных окружения Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не задан!")
    sys.exit(1)

# Твой Telegram ID (админ)
try:
    ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", 0))
    if ADMIN_CHAT_ID == 0:
        raise ValueError
except:
    print("❌ ОШИБКА: ADMIN_CHAT_ID не задан или должен быть числом!")
    sys.exit(1)

# Путь к файлу с планом
PDF_FILE_PATH = "metod_mr_x.pdf"

# Цена
PRICE = 50  # рублей

# Версия
VERSION = "3.0"