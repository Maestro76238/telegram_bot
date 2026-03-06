import os
import sys

# Токен бота (из переменных окружения Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не задан!")
    print("💡 Зайди в Railway -> Variables -> добавь BOT_TOKEN")
    sys.exit(1)

# Твой Telegram ID (админ)
try:
    admin_id_str = os.environ.get("ADMIN_CHAT_ID")
    
    if admin_id_str:
        ADMIN_CHAT_ID = int(admin_id_str)
        print(f"✅ ADMIN_CHAT_ID загружен из Railway: {ADMIN_CHAT_ID}")
    else:
        # ВСТАВЬ СВОЙ ID СЮДА, ЕСЛИ НУЖНО
        ADMIN_CHAT_ID = 1167351174  # <--- ЗАМЕНИ НА СВОЙ ID ИЗ @userinfobot
        
        if ADMIN_CHAT_ID == 0:
            print("❌ ОШИБКА: ADMIN_CHAT_ID не задан!")
            print("💡 Добавь ADMIN_CHAT_ID в Railway Variables")
            sys.exit(1)
        else:
            print(f"✅ ADMIN_CHAT_ID установлен вручную: {ADMIN_CHAT_ID}")
            
except ValueError:
    print("❌ ОШИБКА: ADMIN_CHAT_ID должен быть числом!")
    print(f"   Сейчас он: {os.environ.get('ADMIN_CHAT_ID')}")
    sys.exit(1)

# Путь к файлу с планом
PDF_FILE_PATH = "metod_mr_x.pdf"  # <--- УБЕДИСЬ, ЧТО ФАЙЛ НАЗЫВАЕТСЯ ИМЕННО ТАК

# Цена
PRICE = 50  # рублей

# Версия
VERSION = "4.0"

print("✅ Конфигурация загружена")
print(f"📊 Токен: {BOT_TOKEN[:10]}...")
print(f"👤 Админ ID: {ADMIN_CHAT_ID}")
print(f"📄 PDF файл: {PDF_FILE_PATH}")