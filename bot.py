import asyncio
import logging
import os
import sys
from flask import Flask
from threading import Thread

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🚀 ЗАПУСК БОТА НА RAILWAY")
print("=" * 60)

# ================== FLASK ДЛЯ HEALTHCHECK ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! 🚀"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
logger.info("✅ Flask сервер запущен")

# ================== ИМПОРТЫ ==================
try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Message, CallbackQuery
    from aiogram.filters import Command
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.fsm.storage.memory import MemoryStorage
    logger.info("✅ aiogram импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка импорта aiogram: {e}")
    sys.exit(1)

# ================== ПРОВЕРКА ПЕРЕМЕННЫХ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN or not ADMIN_ID:
    logger.error("❌ BOT_TOKEN или ADMIN_ID не найдены")
    sys.exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)
    logger.info(f"✅ ADMIN_ID: {ADMIN_ID}")
except:
    logger.error("❌ ADMIN_ID должен быть числом")
    sys.exit(1)

# ================== СОЗДАНИЕ БОТА ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logger.info("✅ Бот создан")

# ================== КЛАВИАТУРЫ ==================
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = [
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="❓ Задать вопрос"), KeyboardButton(text="💰 Цены")],
        [KeyboardButton(text="📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def services_keyboard():
    kb = [
        [InlineKeyboardButton(text="💇 Стрижка", callback_data="service_стрижка")],
        [InlineKeyboardButton(text="🎨 Окрашивание", callback_data="service_окрашивание")],
        [InlineKeyboardButton(text="💅 Маникюр", callback_data="service_маникюр")],
        [InlineKeyboardButton(text="💆 Массаж", callback_data="service_массаж")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def time_keyboard():
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    inline_kb = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(text=t, callback_data=f"time_{t}"))
        if len(row) == 3:
            inline_kb.append(row)
            row = []
    if row:
        inline_kb.append(row)
    inline_kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_services")])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def confirm_keyboard():
    kb = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_keyboard():
    kb = [
        [InlineKeyboardButton(text="📋 Список записей", callback_data="admin_bookings")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 Выход", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================== БАЗА ДАННЫХ ==================
import sqlite3
import datetime

DB_NAME = 'salon.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            registered_at TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ База данных инициализирована")

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_booking(user_id, service, date, time):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (user_id, service, date, time, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service, date, time, datetime.datetime.now().isoformat()))
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id

def get_user_phone(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT phone FROM users WHERE user_id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def update_user_phone(user_id, phone):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE users SET phone=? WHERE user_id=?', (phone, user_id))
    conn.commit()
    conn.close()

def get_all_bookings():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT bookings.id, users.full_name, users.phone, bookings.service, 
               bookings.date, bookings.time, bookings.status, users.user_id
        FROM bookings
        JOIN users ON bookings.user_id = users.user_id
        ORDER BY bookings.created_at DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    total_users = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM bookings')
    total_bookings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'")
    pending = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'")
    confirmed = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='cancelled'")
    cancelled = cur.fetchone()[0]
    conn.close()
    return {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'pending_bookings': pending,
        'confirmed_bookings': confirmed,
        'cancelled_bookings': cancelled
    }

def update_booking_status(booking_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id))
    conn.commit()
    conn.close()

def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()

# Инициализация БД при старте
init_db()

# ================== СОСТОЯНИЯ ДЛЯ FSM ==================
class BookingStates(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    asking_phone = State()
    confirming = State()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

# ================== ХРАНИЛИЩЕ ДЛЯ ПАГИНАЦИИ ==================
admin_pages = {}

# ================== ПРОВЕРКА НА АДМИНА ==================
def is_admin(user_id):
    return user_id == ADMIN_ID

# ================== ОБРАБОТЧИКИ ==================

# Старт
@dp.message(Command("start"))
async def cmd_start(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\nЯ бот для салона красоты. Выберите действие:",
        reply_markup=main_menu()
    )

# Цены
@dp.message(lambda message: message.text == "💰 Цены")
async def show_prices(message: Message):
    await message.answer(
        "💰 Наши цены:\n"
        "💇 Стрижка - 1500₽\n"
        "🎨 Окрашивание - от 3000₽\n"
        "💅 Маникюр - 2000₽\n"
        "💆 Массаж - 2500₽"
    )

# Контакты
@dp.message(lambda message: message.text == "📞 Контакты")
async def show_contacts(message: Message):
    await message.answer(
        "📞 Наши контакты:\n"
        "📍 Адрес: ул. Примерная, д. 1\n"
        "☎️ Телефон: +7 (123) 456-78-90\n"
        "⏰ Время работы: ежедневно 10:00–20:00"
    )

# Вопрос
@dp.message(lambda message: message.text == "❓ Задать вопрос")
async def question_start(message: Message):
    await message.answer("Задайте ваш вопрос, я постараюсь помочь.")

# ================== ЗАПИСЬ ==================
@dp.message(lambda message: message.text == "📅 Записаться")
async def booking_start(message: Message, state: FSMContext):
    await state.set_state(BookingStates.choosing_service)
    await message.answer("Выберите услугу:", reply_markup=services_keyboard())

@dp.callback_query(lambda c: c.data.startswith("service_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.replace("service_", "")
    await state.update_data(service=service)
    await state.set_state(BookingStates.choosing_date)
    await callback.message.edit_text(
        f"Выбрано: {service}\nВведите дату в формате ДД.ММ.ГГГГ (например, 25.03.2026):"
    )
    await callback.answer()

@dp.message(BookingStates.choosing_date)
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

@dp.callback_query(lambda c: c.data.startswith("time_"))
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

@dp.message(BookingStates.asking_phone)
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

@dp.callback_query(lambda c: c.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = save_booking(
        callback.from_user.id,
        data['service'],
        data['date'],
        data['time']
    )
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Запись подтверждена! Номер записи: {booking_id}\n"
        "Мы напомним вам за час до визита."
    )
    
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Новая запись!\n"
        f"Клиент: {callback.from_user.full_name}\n"
        f"Услуга: {data['service']}\n"
        f"Дата: {data['date']} в {data['time']}\n"
        f"Телефон: {data.get('phone', 'не указан')}"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запись отменена.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingStates.choosing_service)
    await callback.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()

# ================== АДМИНКА ==================
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    await message.answer("👑 Админ-панель", reply_markup=admin_keyboard())

@dp.callback_query(lambda c: c.data == "admin_bookings")
async def show_bookings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    bookings = get_all_bookings()
    if not bookings:
        await callback.message.edit_text("📭 Записей пока нет.", reply_markup=admin_keyboard())
        await callback.answer()
        return
    
    text = "📋 Все записи:\n\n"
    for b in bookings[:5]:
        text += f"#{b[0]} {b[1]} - {b[3]} {b[4]} {b[5]} ({b[6]})\n"
    
    await callback.message.edit_text(text, reply_markup=admin_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def show_stats_cmd(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    stats = get_stats()
    text = (
        f"📊 Статистика:\n\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"📅 Записей: {stats['total_bookings']}\n"
        f"✅ Подтверждено: {stats['confirmed_bookings']}\n"
        f"⏳ Ожидают: {stats['pending_bookings']}\n"
        f"❌ Отменено: {stats['cancelled_bookings']}"
    )
    await callback.message.edit_text(text, reply_markup=admin_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_back")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.edit_text("👑 Админ-панель", reply_markup=admin_keyboard())
    await callback.answer()

# ================== ЗАПУСК ==================
async def main():
    logger.info("🚀 Запуск polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())