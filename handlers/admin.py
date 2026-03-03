from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from bot_instance import bot, ADMIN_ID
from database import get_all_bookings, get_all_users, get_stats, update_booking_status, delete_booking
from keyboards import admin_keyboard, admin_bookings_keyboard, admin_booking_action_keyboard

router = Router()

def is_admin(user_id):
    return user_id == ADMIN_ID

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

admin_pages = {}

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    
    await message.answer(
        "👑 Админ-панель\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard()
    )

@router.callback_query(F.data == "admin_bookings")
async def show_bookings_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    print("🔍 [АДМИН] Запрос списка записей")
    
    bookings = get_all_bookings()
    
    print(f"🔍 [АДМИН] Получено записей из БД: {len(bookings)}")
    
    admin_pages[callback.from_user.id] = 0
    
    if not bookings:
        print("🔍 [АДМИН] Записей нет")
        text = "📭 Записей пока нет."
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=admin_keyboard())
        await callback.answer()
        return
    
    print(f"🔍 [АДМИН] Показываем список с {len(bookings)} записями")
    
    text = "📋 **Список записей:**\n\nВыберите запись для управления:"
    
    try:
        keyboard = admin_bookings_keyboard(bookings, 0)
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        print(f"❌ Ошибка при создании клавиатуры: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка отображения записей: {e}",
            reply_markup=admin_keyboard()
        )
    
    await callback.answer()

# ... остальные функции без изменений (из предыдущего полного файла admin.py)