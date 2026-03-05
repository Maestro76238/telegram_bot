from telegram import Update
from telegram.ext import ContextTypes
import os
from datetime import datetime

from config import ADMIN_CHAT_ID, PDF_FILE_PATH
from database import db
from keyboards import *

# ========== ОБЩИЕ ОБРАБОТЧИКИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    await update.message.reply_html(
        rf"👋 Привет, {user.mention_html()}! Я — Mr. X.",
        reply_markup=main_menu()
    )
    await update.message.reply_text(
        "Тот самый парень, который вылез из 2 млн долгов в 19 лет.\n\n"
        "📘 Здесь ты можешь купить мой пошаговый план за 50 рублей."
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех нажатий на кнопки"""
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    
    # ===== АДМИНКА =====
    if user.id == ADMIN_CHAT_ID:
        if query.data == "admin_stats":
            stats = db.get_stats()
            text = (f"📊 **Статистика:**\n\n"
                    f"👥 Пользователей: {stats['users']}\n"
                    f"✅ Продаж: {stats['sales']}\n"
                    f"💰 Выручка: {stats['revenue']} руб.\n"
                    f"⏳ Ожидают: {stats['waiting']}")
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=admin_main_menu())
            return
        
        elif query.data == "admin_reply":
            if not db.user_chats:
                await query.edit_message_text("❌ Нет пользователей.", reply_markup=admin_main_menu())
                return
            await query.edit_message_text("Выбери пользователя:", reply_markup=users_list_keyboard(db.user_chats))
            return
        
        elif query.data == "admin_chats":
            if not db.user_chats:
                await query.edit_message_text("❌ Нет чатов.", reply_markup=admin_main_menu())
                return
            text = "👥 **Активные пользователи:**\n\n"
            for uid, info in db.user_chats.items():
                text += f"• {info['first_name']} (@{info['username']}) | ID: {uid}\n"
            if len(text) > 4000:
                text = text[:4000] + "..."
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=admin_main_menu())
            return
        
        elif query.data == "admin_broadcast":
            context.user_data['broadcast_mode'] = True
            await query.edit_message_text(
                "📨 Отправь сообщение для рассылки всем:",
                reply_markup=back_button()
            )
            return
        
        elif query.data == "admin_save":
            db.save()
            await query.edit_message_text("✅ База сохранена!", reply_markup=admin_main_menu())
            return
        
        elif query.data == "admin_back":
            await query.edit_message_text("🔙 Админка:", reply_markup=admin_main_menu())
            return
        
        # Ответ конкретному пользователю
        if query.data.startswith("reply_to_"):
            user_id = int(query.data.replace("reply_to_", ""))
            context.user_data['reply_target'] = user_id
            await query.edit_message_text(f"✏️ Напиши ответ пользователю {user_id}:", reply_markup=back_button())
            context.user_data['awaiting_reply'] = True
            return
    
    # ===== ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ =====
    
    if query.data == 'buy':
        await query.edit_message_text(
            "💳 **Как оплатить:**\n\n"
            "1. Переведи 50 рублей на карту Сбера: `2200 0000 0000 0000`\n"
            "   Получатель: Михаил А.\n"
            "2. Нажми 'Я оплатил'\n"
            "3. Отправь скриншот",
            parse_mode='Markdown',
            reply_markup=paid_button()
        )
    
    elif query.data == 'paid':
        db.waiting_payment.add(user.id)
        await query.edit_message_text(
            "📸 Отправь скриншот перевода.",
            reply_markup=back_button()
        )
    
    elif query.data == 'how_to_pay':
        await query.edit_message_text(
            "💳 **Способы оплаты:**\n\n"
            "• **СБЕР**: `2200 0000 0000 0000`\n"
            "• **ЮMoney**: `4100 0000 0000 0000`\n\n"
            "После перевода нажми 'Купить' → 'Я оплатил'.",
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif query.data == 'support':
        await query.edit_message_text(
            "📞 Напиши свой вопрос сюда, я отвечу.",
            reply_markup=back_button()
        )
    
    elif query.data == 'back_to_main':
        await query.edit_message_text("Главное меню:", reply_markup=main_menu())

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user = update.effective_user
    text = update.message.text
    
    # Админ отвечает пользователю
    if user.id == ADMIN_CHAT_ID:
        if context.user_data.get('awaiting_reply'):
            target_id = context.user_data.get('reply_target')
            if target_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=f"✉️ **Mr. X:**\n\n{text}"
                    )
                    await update.message.reply_text(f"✅ Ответ отправлен")
                except:
                    await update.message.reply_text("❌ Ошибка")
                context.user_data['awaiting_reply'] = False
                return
        
        if context.user_data.get('broadcast_mode'):
            sent = 0
            for uid in db.user_chats:
                try:
                    await context.bot.send_message(uid, f"📢 **Mr. X:**\n\n{text}")
                    sent += 1
                except:
                    pass
            await update.message.reply_text(f"✅ Отправлено {sent} пользователям")
            context.user_data['broadcast_mode'] = False
            return
    
    # Обычный пользователь пишет в поддержку
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"💬 От @{user.username} (ID {user.id}):\n\n{text}"
    )
    await update.message.reply_text("✅ Передал поддержке. Жди ответа.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка скриншотов оплаты"""
    user = update.effective_user
    
    if user.id not in db.waiting_payment:
        await update.message.reply_text("Я не жду скриншот.")
        return
    
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"🔔 **Оплата от {user.id} (@{user.username})**\n"
        f"Команда: /sendpdf {user.id}"
    )
    
    # Пересылаем фото
    await photo_file.download_to_drive(f"temp_{user.id}.jpg")
    with open(f"temp_{user.id}.jpg", 'rb') as f:
        await context.bot.send_photo(ADMIN_CHAT_ID, f)
    os.remove(f"temp_{user.id}.jpg")
    
    await update.message.reply_text("✅ Скрин получил, проверю.")
    db.waiting_payment.discard(user.id)

# ========== АДМИН-КОМАНДЫ ==========

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin"""
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    await update.message.reply_text("🔐 Админка:", reply_markup=admin_main_menu())

async def sendpdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка PDF пользователю"""
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /sendpdf user_id")
        return
    
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("ID должен быть числом")
        return
    
    if not os.path.exists(PDF_FILE_PATH):
        await update.message.reply_text("Файл не найден")
        return
    
    with open(PDF_FILE_PATH, 'rb') as f:
        await context.bot.send_document(
            chat_id=user_id,
            document=f,
            filename="Metod_Mr_X.pdf",
            caption="✅ Оплата подтверждена! Держи план."
        )
    
    db.add_paid(user_id)
    await update.message.reply_text(f"✅ PDF отправлен {user_id}")