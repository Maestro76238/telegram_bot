from aiogram import Bot
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
ADMIN_ID = None

def set_admin_id(admin_id):
    global ADMIN_ID
    ADMIN_ID = admin_id