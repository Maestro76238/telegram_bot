#!/usr/bin/env python3
import threading
import os
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, VERSION
from database import db
from handlers import *

# Flask для Railway
app = Flask(__name__)

# Создаем бота
bot_app = Application.builder().token(BOT_TOKEN).build()

# Подключаем обработчики
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("admin", admin_command))
bot_app.add_handler(CommandHandler("sendpdf", sendpdf_command))
bot_app.add_handler(CallbackQueryHandler(button_click))
bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

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

def run_bot():
    print("🤖 Бот запущен...")
    bot_app.run_polling()

if __name__ == "__main__":
    # Запуск бота в фоне
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    
    # Запуск Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)