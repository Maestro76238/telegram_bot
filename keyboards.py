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

def admin_bookings_keyboard(bookings, page=0):
    items_per_page = 5
    start = page * items_per_page
    end = start + items_per_page
    current_page_bookings = bookings[start:end]
    
    kb = []
    for b in current_page_bookings:
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌'
        }.get(b[6], '❓')
        
        name = b[1] if len(b[1]) < 20 else b[1][:17] + "..."
        button_text = f"{status_emoji} #{b[0]} - {name} ({b[4]})"
        kb.append([InlineKeyboardButton(text=button_text, callback_data=f"booking_view_{b[0]}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"bookings_page_{page-1}"))
    if end < len(bookings):
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"bookings_page_{page+1}"))
    
    if nav_buttons:
        kb.append(nav_buttons)
    
    kb.append([InlineKeyboardButton(text="🔙 В админку", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_booking_action_keyboard(booking_id, current_status):
    kb = []
    
    if current_status == 'pending':
        kb.append([
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"booking_confirm_{booking_id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"booking_cancel_{booking_id}")
        ])
    elif current_status == 'confirmed':
        kb.append([
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"booking_cancel_{booking_id}")
        ])
    elif current_status == 'cancelled':
        kb.append([
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"booking_confirm_{booking_id}")
        ])
    
    kb.append([InlineKeyboardButton(text="🗑 Удалить из базы", callback_data=f"booking_delete_{booking_id}")])
    kb.append([InlineKeyboardButton(text="🔙 К списку", callback_data="admin_bookings")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)