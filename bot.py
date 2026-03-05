#!/usr/bin/env python3
import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, VERSION, ADMIN_CHAT_ID
from database import db
from handlers import *

# Flask приложение
app = Flask(__name__)

@app.route('/')
def index():
    stats = db.get_stats()
    return {
        "status": "alive",
        "bot": "Mr. X",
        "version": VERSION,
        "stats": stats
    }

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_flask():
    """Запуск Flask в отдельном потоке"""
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Запускаем Flask на порту {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def run_bot_main():
    """Запуск бота в главном потоке"""
    print("🤖 Создаем бота...")
    
    bot_app = Application.builder().token(BOT_TOKEN).build()
    
    # Подключаем обработчики
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("admin", admin_command))
    bot_app.add_handler(CommandHandler("sendpdf", sendpdf_command))
    bot_app.add_handler(CallbackQueryHandler(button_click))
    bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print(f"🤖 Бот Mr. X запущен. Админ ID: {ADMIN_CHAT_ID}")
    print("🚀 Начинаем polling...")
    
    bot_app.run_polling()

if __name__ == "__main__":
    print("🔥 Запуск Mr. X бота...")
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не задан!")
        exit(1)
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Flask запущен в фоновом потоке")
    
    # Запускаем бота в главном потоке
    run_bot_main()