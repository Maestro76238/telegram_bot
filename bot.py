#!/usr/bin/env python3
import threading
import os
import asyncio
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, VERSION, ADMIN_CHAT_ID
from database import db
from handlers import *

# Flask для Railway
app = Flask(__name__)

def run_bot():
    """Запуск бота с правильным event loop"""
    try:
        # Создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("🤖 Создаем бота...")
        # Создаем приложение бота
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
        
        # Запускаем бота
        bot_app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка в потоке бота: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            loop.close()
        except:
            pass

# Flask заглушка
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

if __name__ == "__main__":
    print("🔥 Запуск Mr. X бота...")
    
    # Проверяем наличие токена
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не задан!")
        exit(1)
    
    # Запускаем бота в отдельном потоке с правильным event loop
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Поток бота запущен")
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Запускаем Flask на порту {port}...")
    app.run(host="0.0.0.0", port=port)