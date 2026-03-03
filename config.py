import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

print("🔧 Загрузка конфигурации...")

if not BOT_TOKEN:
    raise ValueError("❌ Токен не найден! Добавь BOT_TOKEN в переменные окружения Railway")

if not ADMIN_ID:
    raise ValueError("❌ ADMIN_ID не найден! Добавь ADMIN_ID в переменные окружения Railway")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    raise ValueError("❌ ADMIN_ID должен быть числом")

print("✅ Конфигурация загружена")
print(f"Токен бота: {BOT_TOKEN[:10]}...")
print(f"Admin ID: {ADMIN_ID}")