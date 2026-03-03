from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import services_keyboard, time_keyboard, confirm_keyboard, main_menu
from database import save_booking, update_user_phone, get_user_phone
from bot_instance import bot, ADMIN_ID
import datetime

router = Router()

class BookingStates(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    asking_phone = State()
    confirming = State()

@router.message(F.text == "📅 Записаться")
async def booking_start(message: Message, state: FSMContext):
    await state.set_state(BookingStates.choosing_service)
    await message.answer("Выберите услугу:", reply_markup=services_keyboard())

@router.callback_query(F.data.startswith("service_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.replace("service_", "")
    await state.update_data(service=service)
    await state.set_state(BookingStates.choosing_date)
    await callback.message.edit_text(
        f"Выбрано: {service}\nВведите дату в формате ДД.ММ.ГГГГ (например, 25.04.2026):"
    )
    await callback.answer()

@router.message(BookingStates.choosing_date)
async def choose_date(message: Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, "%d.%m.%Y").date()
        if date < datetime.date.today():
            await message.answer("Дата не может быть в прошлом. Введите будущую дату:")
            return
        await state.update_data(date=message.text)
        await state.set_state(BookingStates.choosing_time)
        await message.answer("Выберите время:", reply_markup=time_keyboard())
    except ValueError:
        await message.answer("Неверный формат. Введите дату в формате ДД.ММ.ГГГГ:")

@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.replace("time_", "")
    await state.update_data(time=time)
    
    user_id = callback.from_user.id
    phone = get_user_phone(user_id)
    
    if phone:
        await state.update_data(phone=phone)
        data = await state.get_data()
        await state.set_state(BookingStates.confirming)
        await callback.message.edit_text(
            f"Проверьте данные:\n"
            f"Услуга: {data['service']}\n"
            f"Дата: {data['date']}\n"
            f"Время: {data['time']}\n"
            f"Телефон: {phone}\n\n"
            "Всё верно?",
            reply_markup=confirm_keyboard()
        )
    else:
        await state.set_state(BookingStates.asking_phone)
        await callback.message.edit_text("Введите ваш номер телефона (например, +71234567890):")
    
    await callback.answer()

@router.message(BookingStates.asking_phone)
async def ask_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith("+") or len(phone) < 10:
        await message.answer("Пожалуйста, введите номер в формате +71234567890:")
        return
    
    update_user_phone(message.from_user.id, phone)
    await state.update_data(phone=phone)
    
    data = await state.get_data()
    await state.set_state(BookingStates.confirming)
    await message.answer(
        f"Проверьте данные:\n"
        f"Услуга: {data['service']}\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['time']}\n"
        f"Телефон: {phone}\n\n"
        "Всё верно?",
        reply_markup=confirm_keyboard()
    )

@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    
    booking_id = save_booking(
        user_id, 
        data['service'], 
        data['date'], 
        data['time']
    )
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Запись подтверждена! Номер записи: {booking_id}\n"
        "Мы напомним вам за час до визита.",
        reply_markup=None
    )
    
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Новая запись!\n"
        f"Клиент: {callback.from_user.full_name} (@{callback.from_user.username})\n"
        f"Услуга: {data['service']}\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['time']}\n"
        f"Телефон: {data.get('phone', 'не указан')}"
    )
    
    await callback.answer()

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запись отменена.")
    await callback.answer()

@router.callback_query(F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingStates.choosing_service)
    await callback.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()