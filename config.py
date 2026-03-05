import os
import sys

# Токен бота (из переменных окружения Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не задан!")
    print("💡 Зайди в Railway -> Variables -> добавь BOT_TOKEN")
    sys.exit(1)

# Твой Telegram ID (админ) - с запасным вариантом
try:
    # Сначала пробуем получить из переменных окружения
    admin_id_str = os.environ.get("ADMIN_CHAT_ID")
    
    if admin_id_str:
        ADMIN_CHAT_ID = int(admin_id_str)
        print(f"✅ ADMIN_CHAT_ID загружен из Railway: {ADMIN_CHAT_ID}")
    else:
        # ВАЖНО: ВСТАВЬ СЮДА СВОЙ ID РУЧКАМИ, ЕСЛИ Railway НЕ РАБОТАЕТ
        # Узнай свой ID у @userinfobot и вставь вместо 0
        ADMIN_CHAT_ID = 0  # <--- ИЗМЕНИ ЭТО ЧИСЛО НА СВОЙ ID!
        
        if ADMIN_CHAT_ID == 0:
            print("❌ ОШИБКА: ADMIN_CHAT_ID не задан!")
            print("💡 Вариант 1: Добавь ADMIN_CHAT_ID в Railway Variables")
            print("💡 Вариант 2: Вставь свой ID руками в файл config.py (строка 18)")
            sys.exit(1)
        else:
            print(f"✅ ADMIN_CHAT_ID установлен вручную: {ADMIN_CHAT_ID}")
            
except ValueError:
    print("❌ ОШИБКА: ADMIN_CHAT_ID должен быть числом!")
    print(f"   Сейчас он: {os.environ.get('ADMIN_CHAT_ID')}")
    sys.exit(1)

# Путь к файлу с планом
PDF_FILE_PATH = "metod_mr_x.pdf"

# Цена
PRICE = 50  # рублей

# Версия
VERSION = "3.0"

print("✅ Конфигурация загружена")
print(f"📊 Токен: {BOT_TOKEN[:10]}...")
print(f"👤 Админ ID: {ADMIN_CHAT_ID}")