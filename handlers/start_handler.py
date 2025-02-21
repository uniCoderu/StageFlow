# handlers/start_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏧 Торговая площадка", callback_data="marketplace_menu")],
        [InlineKeyboardButton("📜 Полит. соглашение", callback_data="policy")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\nИспользуйте меню ниже для выбора нужного действия."

    query = update.callback_query
    if query:  # Если это callback-запрос
        await query.edit_message_text(text, reply_markup=reply_markup)
        logger.info(f"Главное меню отображено для пользователя {query.from_user.id} через callback")
    else:  # Если это команда /start или другой случай
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
        logger.info(f"Команда /start выполнена для пользователя {update.effective_user.id}")
