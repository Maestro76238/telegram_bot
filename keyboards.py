from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    """Главное меню для пользователя"""
    keyboard = [
        [InlineKeyboardButton("💳 Купить план за 50₽", callback_data='buy')],
        [InlineKeyboardButton("❓ Как оплатить", callback_data='how_to_pay')],
        [InlineKeyboardButton("📞 Поддержка", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    """Кнопка 'Назад'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ])

def paid_button():
    """Кнопка 'Я оплатил'"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid")],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ])

# ========== АДМИНСКИЕ КЛАВИАТУРЫ ==========

def admin_main_menu():
    """Главное меню для админа"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("💬 Ответить пользователю", callback_data="admin_reply")],
        [InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Активные чаты", callback_data="admin_chats")],
        [InlineKeyboardButton("🔄 Сохранить БД", callback_data="admin_save")]
    ]
    return InlineKeyboardMarkup(keyboard)

def users_list_keyboard(user_chats):
    """Список пользователей для выбора (максимум 10)"""
    keyboard = []
    for user_id, info in list(user_chats.items())[:10]:
        name = info.get("first_name", "Без имени")
        username = info.get("username", "")
        btn_text = f"{name} (@{username})" if username else name
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"reply_to_{user_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(keyboard)