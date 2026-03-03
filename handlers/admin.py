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
    
    bookings = get_all_bookings()
    admin_pages[callback.from_user.id] = 0
    
    if not bookings:
        await callback.message.edit_text(
            "📭 Записей пока нет.",
            reply_markup=admin_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "📋 **Список записей:**\n\n"
        "Выберите запись для управления:",
        reply_markup=admin_bookings_keyboard(bookings, 0)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("bookings_page_"))
async def change_page(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.replace("bookings_page_", ""))
    admin_pages[callback.from_user.id] = page
    
    bookings = get_all_bookings()
    
    await callback.message.edit_text(
        "📋 **Список записей:**\n\n"
        "Выберите запись для управления:",
        reply_markup=admin_bookings_keyboard(bookings, page)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("booking_view_"))
async def view_booking(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("booking_view_", ""))
    
    bookings = get_all_bookings()
    booking = None
    for b in bookings:
        if b[0] == booking_id:
            booking = b
            break
    
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'cancelled': '❌'
    }.get(booking[6], '❓')
    
    text = (
        f"🔹 **Запись #{booking[0]}**\n\n"
        f"👤 **Клиент:** {booking[1]}\n"
        f"📞 **Телефон:** {booking[2]}\n"
        f"💇 **Услуга:** {booking[3]}\n"
        f"📅 **Дата:** {booking[4]}\n"
        f"⏰ **Время:** {booking[5]}\n"
        f"📌 **Статус:** {status_emoji} {booking[6]}\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_booking_action_keyboard(booking_id, booking[6])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("booking_confirm_"))
async def confirm_booking_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("booking_confirm_", ""))
    update_booking_status(booking_id, 'confirmed')
    
    bookings = get_all_bookings()
    booking = None
    for b in bookings:
        if b[0] == booking_id:
            booking = b
            break
    
    if booking:
        try:
            await bot.send_message(
                booking[7],
                f"✅ **Запись подтверждена!**\n\n"
                f"Ваша запись #{booking_id} подтверждена администратором.\n"
                f"💇 Услуга: {booking[3]}\n"
                f"📅 Дата: {booking[4]} в {booking[5]}\n\n"
                f"Ждём вас!"
            )
        except:
            pass
    
    await callback.answer("✅ Запись подтверждена", show_alert=True)
    await view_booking(callback)

@router.callback_query(F.data.startswith("booking_cancel_"))
async def cancel_booking_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("booking_cancel_", ""))
    update_booking_status(booking_id, 'cancelled')
    
    bookings = get_all_bookings()
    booking = None
    for b in bookings:
        if b[0] == booking_id:
            booking = b
            break
    
    if booking:
        try:
            await bot.send_message(
                booking[7],
                f"❌ **Запись отменена**\n\n"
                f"Ваша запись #{booking_id} была отменена администратором.\n"
                f"Пожалуйста, свяжитесь с нами для уточнения."
            )
        except:
            pass
    
    await callback.answer("❌ Запись отменена", show_alert=True)
    await view_booking(callback)

@router.callback_query(F.data.startswith("booking_delete_"))
async def delete_booking_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    booking_id = int(callback.data.replace("booking_delete_", ""))
    delete_booking(booking_id)
    
    await callback.answer("🗑 Запись удалена из базы", show_alert=True)
    await show_bookings_list(callback)

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    stats = get_stats()
    
    text = (
        "📊 **Статистика:**\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"📅 Всего записей: {stats['total_bookings']}\n"
        f"✅ Подтверждённых: {stats['confirmed_bookings']}\n"
        f"⏳ Ожидают: {stats['pending_bookings']}\n"
        f"❌ Отменённых: {stats['cancelled_bookings']}\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.message.edit_text(
        "📢 **Рассылка**\n\n"
        "Введите сообщение для отправки всем пользователям:\n\n"
        "⚠️ Отправьте /cancel чтобы отменить",
        reply_markup=None
    )
    await callback.answer()

@router.message(BroadcastStates.waiting_for_message)
async def send_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Рассылка отменена.")
        return
    
    users = get_all_users()
    
    await message.answer(f"📨 Начинаю рассылку {len(users)} пользователям...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await bot.send_message(
                user_id,
                f"📢 **Сообщение от администратора**\n\n{message.text}"
            )
            success += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await state.clear()
    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не удалось: {failed}"
    )

@router.callback_query(F.data == "admin_back")
async def back_to_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👑 Админ-панель\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard()
    )
    await callback.answer()