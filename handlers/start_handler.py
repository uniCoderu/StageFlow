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

    if update.callback_query:  # Обработка callback-запроса (например, "Назад")
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        logger.info(f"Главное меню отображено для пользователя {update.callback_query.from_user.id} через callback")
    elif update.message:  # Обработка команды /start
        await update.message.reply_text(text, reply_markup=reply_markup)
        logger.info(f"Команда /start выполнена для пользователя {update.message.from_user.id}")
    else:
        logger.error("start вызван с некорректным update")
