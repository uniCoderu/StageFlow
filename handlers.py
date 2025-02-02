from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем приветственное сообщение пользователю."""
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("💳 Продать билет", callback_data="sell_ticket")],
        [InlineKeyboardButton("📜 Полит. соглашение", callback_data="policy")],
        [InlineKeyboardButton("🏷️ Торговая площадка", callback_data="marketplace")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\n"
            "Используйте меню ниже для выбора нужного действия.",
            reply_markup=reply_markup
        )

# Обработчик нажатий на кнопки меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем нажатия на кнопки меню."""
    query = update.callback_query
    await query.answer()

    if query.data == "settings":
        await query.edit_message_text(text="Настройки")
    elif query.data == "sell_ticket":
        await query.edit_message_text(text="Продажа билетов")
    elif query.data == "policy":
        await query.edit_message_text(text="Политическое соглашение")
    elif query.data == "marketplace":
        await query.edit_message_text(text="Торговая площадка")
