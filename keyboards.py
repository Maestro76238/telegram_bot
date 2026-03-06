from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# ========== ОСНОВНАЯ КЛАВИАТУРА (ВСЕГДА ВНИЗУ) ==========

def get_main_reply_keyboard():
    """Постоянная клавиатура внизу экрана"""
    keyboard = [
        [KeyboardButton("💳 Купить план")],
        [KeyboardButton("❓ Как оплатить"), KeyboardButton("📞 Поддержка")],
        [KeyboardButton("📊 Статус")],
        [KeyboardButton("📄 Шаблон заявления")]  # КНОПКА ДЛЯ ШАБЛОНА
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        input_field_placeholder="Выбери действие..."
    )

def get_admin_reply_keyboard():
    """Постоянная клавиатура для админа"""
    keyboard = [
        [KeyboardButton("📊 Статистика"), KeyboardButton("🖼 Чеки")],
        [KeyboardButton("💬 Ответить"), KeyboardButton("📨 Рассылка")],
        [KeyboardButton("👥 Пользователи")],
        [KeyboardButton("🔙 Выход из админки")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        input_field_placeholder="Админ-панель"
    )

# ========== INLINE КЛАВИАТУРЫ (для сообщений) ==========

def main_menu():
    """Главное меню (inline)"""
    keyboard = [
        [InlineKeyboardButton("💳 Купить план за 50₽", callback_data='buy')],
        [InlineKeyboardButton("❓ Как оплатить", callback_data='how_to_pay')],
        [InlineKeyboardButton("📞 Поддержка", callback_data='support')],
        [InlineKeyboardButton("📄 Шаблон заявления", callback_data='template')]  # КНОПКА ДЛЯ ШАБЛОНА
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

# ========== КНОПКИ ДЛЯ ШАБЛОНА ==========

def subscription_check_keyboard():
    """Кнопки для проверки подписки на канал"""
    keyboard = [
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub_after")],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def subscription_link_keyboard(channel_link):
    """Кнопка с ссылкой на канал"""
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url=channel_link)],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub_after")],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== АДМИНСКИЕ INLINE КЛАВИАТУРЫ ==========

def admin_main_menu():
    """Главное меню для админа (inline)"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🖼 Чеки на проверку", callback_data="admin_checks")],
        [InlineKeyboardButton("💬 Ответить пользователю", callback_data="admin_reply")],
        [InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Активные чаты", callback_data="admin_chats")],
        [InlineKeyboardButton("🔄 Сохранить БД", callback_data="admin_save")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_checks_keyboard(payments):
    """Список чеков на проверку"""
    keyboard = []
    for payment_id, payment in payments.items():
        btn_text = f"{payment_id} | {payment['first_name']} (@{payment['username']})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"check_{payment_id}")])
    
    if not payments:
        keyboard.append([InlineKeyboardButton("✅ Нет чеков", callback_data="noop")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(keyboard)

def payment_action_keyboard(payment_id):
    """Кнопки для конкретного чека"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{payment_id}"),
            InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{payment_id}")
        ],
        [InlineKeyboardButton("🔙 К списку чеков", callback_data="admin_checks")]
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