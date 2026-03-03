from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_menu
from database import add_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    add_user(user.id, user.username, user.full_name)
    
    await message.answer(
        f"Привет, {user.full_name}!\n"
        "Я бот для салона красоты. Выберите действие:",
        reply_markup=main_menu()
    )

@router.message(F.text == "💰 Цены")
async def show_prices(message: Message):
    await message.answer(
        "💰 Наши цены:\n"
        "💇 Стрижка - 1500₽\n"
        "🎨 Окрашивание - от 3000₽\n"
        "💅 Маникюр - 2000₽\n"
        "💆 Массаж - 2500₽"
    )

@router.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    await message.answer(
        "📞 Наши контакты:\n"
        "📍 Адрес: ул. Примерная, д. 1\n"
        "☎️ Телефон: +7 (123) 456-78-90\n"
        "⏰ Время работы: ежедневно 10:00–20:00"
    )

@router.message(F.text == "❓ Задать вопрос")
async def question_start(message: Message):
    await message.answer("Задайте ваш вопрос, я постараюсь помочь.")