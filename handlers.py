import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

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
        "📘 Здесь ты можешь купить мой пошаговый план за 50 рублей.",
        reply_markup=get_main_reply_keyboard()
    )

async def handle_reply_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на нижние кнопки"""
    user = update.effective_user
    text = update.message.text
    
    # Админские кнопки
    if user.id == ADMIN_CHAT_ID:
        if text == "📊 Статистика":
            stats = db.get_stats()
            await update.message.reply_text(
                f"📊 **СТАТИСТИКА:**\n\n"
                f"👥 Пользователей: {stats['users']}\n"
                f"✅ Продаж: {stats['sales']}\n"
                f"💰 Выручка: {stats['revenue']} руб.\n\n"
                f"🖼 **Чеки:**\n"
                f"⏳ Ожидают: {stats['pending']}\n"
                f"✅ Одобрено: {stats['approved']}\n"
                f"❌ Отказано: {stats['rejected']}",
                parse_mode='Markdown'
            )
            return
        
        elif text == "🖼 Чеки":
            pending = db.get_pending_payments()
            if not pending:
                await update.message.reply_text("✅ Нет чеков на проверке!")
                return
            
            await update.message.reply_text(
                f"🖼 **Чеки на проверку ({len(pending)}):**",
                parse_mode='Markdown',
                reply_markup=admin_checks_keyboard(pending)
            )
            return
        
        elif text == "💬 Ответить":
            if not db.user_chats:
                await update.message.reply_text("❌ Нет пользователей.")
                return
            await update.message.reply_text(
                "Выбери пользователя:",
                reply_markup=users_list_keyboard(db.user_chats)
            )
            return
        
        elif text == "📨 Рассылка":
            context.user_data['broadcast_mode'] = True
            await update.message.reply_text(
                "📨 Отправь сообщение для рассылки всем:",
                reply_markup=back_button()
            )
            return
        
        elif text == "👥 Пользователи":
            if not db.user_chats:
                await update.message.reply_text("❌ Нет чатов.")
                return
            text = "👥 **Активные пользователи:**\n\n"
            for uid, info in db.user_chats.items():
                text += f"• {info['first_name']} (@{info['username']}) | ID: {uid}\n"
            if len(text) > 4000:
                text = text[:4000] + "..."
            await update.message.reply_text(text, parse_mode='Markdown')
            return
        
        elif text == "🔙 Выход из админки":
            context.user_data.clear()
            await update.message.reply_text(
                "Вышел из админки",
                reply_markup=get_main_reply_keyboard()
            )
            return
    
    # Обычные пользовательские кнопки
    if text == "💳 Купить план":
        await update.message.reply_text(
            "💳 **Как оплатить:**\n\n"
            "1. Переведи 50 рублей на карту Сбера: `2200 0000 0000 0000`\n"
            "   Получатель: Михаил А.\n"
            "2. Нажми 'Я оплатил'\n"
            "3. Отправь скриншот",
            parse_mode='Markdown',
            reply_markup=paid_button()
        )
    
    elif text == "❓ Как оплатить":
        await update.message.reply_text(
            "💳 **Способы оплаты:**\n\n"
            "• **СБЕР**: `2200 0000 0000 0000`\n"
            "• **ЮMoney**: `4100 0000 0000 0000`\n\n"
            "После перевода нажми 'Купить' → 'Я оплатил' и отправь скриншот.",
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif text == "📞 Поддержка":
        await update.message.reply_text(
            "📞 Напиши свой вопрос сюда, я отвечу в ближайшее время.",
            reply_markup=back_button()
        )
    
    elif text == "📊 Статус":
        if db.is_paid(user.id):
            await update.message.reply_text("✅ Ты уже купил план! Спасибо!")
        else:
            await update.message.reply_text("⏳ Ты еще не покупал план. Хочешь купить?", reply_markup=main_menu())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех нажатий на inline кнопки"""
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    
    # ===== АДМИНКА =====
    if user.id == ADMIN_CHAT_ID:
        
        if query.data == "admin_stats":
            stats = db.get_stats()
            text = (f"📊 **СТАТИСТИКА:**\n\n"
                    f"👥 Пользователей: {stats['users']}\n"
                    f"✅ Продаж: {stats['sales']}\n"
                    f"💰 Выручка: {stats['revenue']} руб.\n\n"
                    f"🖼 **Чеки:**\n"
                    f"⏳ Ожидают: {stats['pending']}\n"
                    f"✅ Одобрено: {stats['approved']}\n"
                    f"❌ Отказано: {stats['rejected']}\n"
                    f"📦 Всего платежей: {stats['total_payments']}")
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=admin_main_menu())
            return
        
        elif query.data == "admin_checks":
            pending = db.get_pending_payments()
            if not pending:
                await query.edit_message_text("✅ Нет чеков на проверке!", reply_markup=admin_main_menu())
                return
            
            await query.edit_message_text(
                f"🖼 **Чеки на проверку ({len(pending)}):**\n\nВыбери чек:",
                parse_mode='Markdown',
                reply_markup=admin_checks_keyboard(pending)
            )
            return
        
        elif query.data.startswith("check_"):
            payment_id = query.data.replace("check_", "")
            payment = db.payments.get(payment_id)
            
            if not payment:
                await query.edit_message_text("❌ Чек не найден!", reply_markup=admin_main_menu())
                return
            
            context.user_data['current_payment'] = payment_id
            
            text = (f"🖼 **Чек {payment_id}**\n\n"
                    f"👤 Пользователь: {payment['first_name']} (@{payment['username']})\n"
                    f"🆔 ID: {payment['user_id']}\n"
                    f"📅 Отправлен: {payment['created_at'][:19]}\n"
                    f"📸 Фото: {payment['photo']}\n\n"
                    f"Выбери действие:")
            
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=payment_action_keyboard(payment_id))
            return
        
        elif query.data.startswith("approve_"):
            payment_id = query.data.replace("approve_", "")
            
            if db.approve_payment(payment_id):
                payment = db.payments[payment_id]
                user_id = payment['user_id']
                
                try:
                    if os.path.exists(PDF_FILE_PATH):
                        with open(PDF_FILE_PATH, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=user_id,
                                document=f,
                                filename="Metod_Mr_X.pdf",
                                caption="✅ **Оплата подтверждена!**\n\nСпасибо за покупку. Держи мой план.\nЕсли поможет — расскажи друзьям."
                            )
                        
                        await query.edit_message_text(
                            f"✅ Чек {payment_id} одобрен!\nФайл отправлен пользователю.",
                            reply_markup=admin_main_menu()
                        )
                    else:
                        await query.edit_message_text(
                            f"⚠️ Чек одобрен, но файл {PDF_FILE_PATH} не найден!\nОтправь пользователю вручную: /sendpdf {user_id}",
                            reply_markup=admin_main_menu()
                        )
                except Exception as e:
                    await query.edit_message_text(
                        f"⚠️ Чек одобрен, но ошибка отправки: {e}\nОтправь вручную: /sendpdf {user_id}",
                        reply_markup=admin_main_menu()
                    )
            else:
                await query.edit_message_text("❌ Ошибка при подтверждении!", reply_markup=admin_main_menu())
            return
        
        elif query.data.startswith("reject_"):
            payment_id = query.data.replace("reject_", "")
            context.user_data['reject_payment'] = payment_id
            context.user_data['awaiting_reject_reason'] = True
            
            await query.edit_message_text(
                f"❌ **Отказ для {payment_id}**\n\n"
                f"Напиши причину отказа. Пользователь получит это сообщение.\n"
                f"(Например: 'Не видно сумму', 'Не тот получатель', 'Скриншот нечитаемый')\n\n"
                f"Чтобы отменить, напиши /cancel",
                parse_mode='Markdown',
                reply_markup=back_button()
            )
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
            if db.save():
                await query.edit_message_text("✅ База сохранена!", reply_markup=admin_main_menu())
            else:
                await query.edit_message_text("❌ Ошибка сохранения!", reply_markup=admin_main_menu())
            return
        
        elif query.data == "admin_back":
            await query.edit_message_text("🔙 Админка:", reply_markup=admin_main_menu())
            return
        
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
        await query.edit_message_text(
            "📸 Отправь скриншот перевода.\n\n"
            "Я передам его на проверку. Обычно это занимает несколько минут.",
            reply_markup=back_button()
        )
    
    elif query.data == 'how_to_pay':
        await query.edit_message_text(
            "💳 **Способы оплаты:**\n\n"
            "• **СБЕР**: `2200 0000 0000 0000`\n"
            "• **ЮMoney**: `4100 0000 0000 0000`\n\n"
            "После перевода нажми 'Купить' → 'Я оплатил' и отправь скриншот.",
            parse_mode='Markdown',
            reply_markup=back_button()
        )
    
    elif query.data == 'support':
        await query.edit_message_text(
            "📞 Напиши свой вопрос сюда, я отвечу в ближайшее время.",
            reply_markup=back_button()
        )
    
    elif query.data == 'back_to_main':
        await query.edit_message_text("Главное меню:", reply_markup=main_menu())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user = update.effective_user
    text = update.message.text
    
    # Сначала проверяем, может это кнопка с нижней клавиатуры
    if text in ["💳 Купить план", "❓ Как оплатить", "📞 Поддержка", "📊 Статус",
                "📊 Статистика", "🖼 Чеки", "💬 Ответить", "📨 Рассылка", "👥 Пользователи", "🔙 Выход из админки"]:
        await handle_reply_buttons(update, context)
        return
    
    # Отмена операции
    if text == "/cancel":
        context.user_data.clear()
        await update.message.reply_text("✅ Операция отменена.", reply_markup=get_main_reply_keyboard())
        return
    
    # ===== АДМИН: ОТКАЗ С ПРИЧИНОЙ =====
    if user.id == ADMIN_CHAT_ID and context.user_data.get('awaiting_reject_reason'):
        payment_id = context.user_data.get('reject_payment')
        reason = text
        
        if payment_id and reason:
            payment = db.payments.get(payment_id)
            if payment:
                user_id = payment['user_id']
                
                db.reject_payment(payment_id, reason)
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"❌ **Платеж отклонен**\n\n"
                             f"Твой платеж по чеку {payment_id} не прошел проверку.\n"
                             f"**Причина:** {reason}\n\n"
                             f"Если хочешь попробовать снова — нажми /start и оплати заново.\n"
                             f"Если считаешь, что ошибка — напиши в поддержку."
                    )
                    
                    await update.message.reply_text(
                        f"✅ Чек {payment_id} отклонен.\n"
                        f"Причина отправлена пользователю."
                    )
                except Exception as e:
                    await update.message.reply_text(
                        f"⚠️ Чек отклонен, но не удалось уведомить пользователя: {e}"
                    )
                
                context.user_data.pop('awaiting_reject_reason', None)
                context.user_data.pop('reject_payment', None)
                return
            else:
                await update.message.reply_text("❌ Платеж не найден")
                context.user_data.clear()
                return
    
    # ===== АДМИН: ОТВЕТ ПОЛЬЗОВАТЕЛЮ =====
    if user.id == ADMIN_CHAT_ID:
        if context.user_data.get('awaiting_reply'):
            target_id = context.user_data.get('reply_target')
            if target_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=f"✉️ **Mr. X (поддержка):**\n\n{text}"
                    )
                    await update.message.reply_text(f"✅ Ответ отправлен")
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка: {e}")
                context.user_data['awaiting_reply'] = False
                return
        
        if context.user_data.get('broadcast_mode'):
            sent = 0
            failed = 0
            for uid in db.user_chats:
                try:
                    await context.bot.send_message(int(uid), f"📢 **Сообщение от Mr. X:**\n\n{text}")
                    sent += 1
                except:
                    failed += 1
                await asyncio.sleep(0.05)
            await update.message.reply_text(f"✅ Рассылка завершена!\nОтправлено: {sent}\nОшибок: {failed}")
            context.user_data['broadcast_mode'] = False
            return
    
    # ===== ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ: СООБЩЕНИЕ В ПОДДЕРЖКУ =====
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"💬 **Сообщение от пользователя**\n"
        f"От: {user.first_name} (@{user.username})\n"
        f"ID: {user.id}\n\n"
        f"{text}"
    )
    await update.message.reply_text("✅ Сообщение передано поддержке. Ожидай ответа.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка скриншотов оплаты"""
    user = update.effective_user
    
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    
    # Создаем папку для чеков
    os.makedirs("receipts", exist_ok=True)
    photo_path = f"receipts/{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    payment_id = db.create_payment(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        photo_path=photo_path
    )
    
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🔔 **НОВЫЙ ЧЕК НА ПРОВЕРКУ!**\n\n"
             f"🧾 Номер: {payment_id}\n"
             f"👤 Пользователь: {user.first_name} (@{user.username})\n"
             f"🆔 ID: {user.id}\n"
             f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
             f"Зайди в админку → 'Чеки на проверку'",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👀 Проверить", callback_data="admin_checks")
        ]])
    )
    
    with open(photo_path, 'rb') as f:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=f,
            caption=f"Чек {payment_id}"
        )
    
    await update.message.reply_text(
        "✅ Скриншот получен! Я передал его на проверку.\n"
        "Обычно это занимает несколько минут. Как только проверю — пришлю файл или напишу причину отказа."
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin"""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("У тебя нет доступа к админке.")
        return
    
    stats = db.get_stats()
    text = (f"🔐 **АДМИН-ПАНЕЛЬ Mr. X**\n\n"
            f"📊 **Текущая статистика:**\n"
            f"👥 Пользователей: {stats['users']}\n"
            f"✅ Продаж: {stats['sales']}\n"
            f"💰 Выручка: {stats['revenue']} руб.\n"
            f"🖼 Чеков ожидает: {stats['pending']}\n\n"
            f"Выбери действие:")
    
    await update.message.reply_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=admin_main_menu()
    )
    
    # Меняем нижнюю клавиатуру на админскую
    await update.message.reply_text(
        "Нижняя клавиатура переключена в режим админа:",
        reply_markup=get_admin_reply_keyboard()
    )

async def sendpdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручная отправка PDF пользователю"""
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
        await update.message.reply_text(f"❌ Файл {PDF_FILE_PATH} не найден!")
        return
    
    try:
        with open(PDF_FILE_PATH, 'rb') as f:
            await context.bot.send_document(
                chat_id=user_id,
                document=f,
                filename="Metod_Mr_X.pdf",
                caption="✅ Оплата подтверждена! Держи план."
            )
        
        db.add_paid(user_id)
        await update.message.reply_text(f"✅ PDF отправлен {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")