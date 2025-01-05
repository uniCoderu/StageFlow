import nest_asyncio
nest_asyncio.apply()

import logging
import sys
import os

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
except ModuleNotFoundError:
    sys.stderr.write("Модуль 'telegram' не найден. Установите его командой 'pip install python-telegram-bot' и попробуйте снова.\n")
    sys.exit(1)

# Настраиваем логирование с цветным выводом
class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[92m",
        "INFO": "\033[94m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m"
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)

formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Ваш Telegram API ключ
API_KEY = "8018543300:AAFgPgp3_U7cjsa5s7mF3gV6YxuEzj6pbf0"

# Директория для хранения данных билетов
TICKETS_DIR = "tickets"
if not os.path.exists(TICKETS_DIR):
    os.makedirs(TICKETS_DIR)

# Хранилище данных пользователей
user_data = {}
marketplace_data = []  # Глобальное хранилище для выставленных билетов

# Генерация ID билета
def generate_ticket_id():
    return f"ticket_{len(marketplace_data) + 1}"

# Основная команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start и выводит приветственное сообщение."""
    keyboard = [
        [InlineKeyboardButton("\ud83c\udfe7 Торговая площадка", callback_data="marketplace_menu")],
        [InlineKeyboardButton("\ud83d\udcdc Полит. соглашение", callback_data="policy")],
        [InlineKeyboardButton("\u2699\ufe0f Настройки", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\n"
            "Используйте меню ниже для выбора нужного действия.",
            reply_markup=reply_markup
        )

# Обработчик кнопок меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки меню."""
    query = update.callback_query
    await query.answer()

    if query.data == "settings":
        keyboard = [
            [InlineKeyboardButton("\ud83d\udcb0 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("\ud83c\udf10 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("\ud83d\udcde Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Пожалуйста, выберите одну из настроек:", reply_markup=reply_markup)

    elif query.data == "payment_details":
        user_id = query.from_user.id
        user_payment_data = user_data.get(user_id, {}).get("payment_details")
        if user_payment_data:
            keyboard = [
                [InlineKeyboardButton("Да", callback_data="edit_payment_details")],
                [InlineKeyboardButton("Нет", callback_data="settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Ваши реквизиты уже сохранены. Хотите изменить их?", reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("СБП", callback_data="sbp")],
                [InlineKeyboardButton("Номер карты", callback_data="card")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Выберите способ получения оплаты:", reply_markup=reply_markup)

    elif query.data == "sbp":
        await query.edit_message_text("Введите номер телефона, привязанный к банку:")
        context.user_data["awaiting_sbp_phone"] = True

    elif query.data == "card":
        await query.edit_message_text("Введите номер вашей карты:")
        context.user_data["awaiting_card_number"] = True

    elif query.data == "select_city":
        await query.edit_message_text("Введите название вашего города:")
        context.user_data["awaiting_city"] = True

    elif query.data.startswith("bank_"):
        bank_name = query.data.split("_")[1]
        user_id = query.from_user.id
        user_data[user_id]["payment_details"] = user_data[user_id].get("payment_details", {})
        user_data[user_id]["payment_details"]["bank"] = bank_name
        await query.edit_message_text(f"Ваш выбор ({bank_name}) сохранен! Возвращаю вас в меню настроек.")

        # Возвращаем пользователя в меню настроек
        keyboard = [
            [InlineKeyboardButton("\ud83d\udcb0 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("\ud83c\udf10 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("\ud83d\udcde Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

    elif query.data == "main_menu":
        await start(update, context)

    elif query.data == "edit_payment_details":
        keyboard = [
            [InlineKeyboardButton("СБП", callback_data="sbp")],
            [InlineKeyboardButton("Номер карты", callback_data="card")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите способ получения оплаты:", reply_markup=reply_markup)

# Обработчик текстовых сообщений
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения от пользователя."""
    user_id = update.message.from_user.id

    if context.user_data.get("awaiting_sbp_phone"):
        phone = update.message.text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "СБП", "phone": phone}

        keyboard = [
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["Сбер", "Т-банк", "ВТБ"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["Альфа-Банк", "Райфайзен"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["OZON Банк", "Яндекс Банк"]]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите банк:", reply_markup=reply_markup)
        context.user_data["awaiting_sbp_phone"] = False

    elif context.user_data.get("awaiting_card_number"):
        card_number = update.message.text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "Номер карты", "card": card_number}
        await update.message.reply_text("Ваши реквизиты сохранены! Возвращаю вас в меню настроек.")
        context.user_data["awaiting_card_number"] = False

        keyboard = [
            [InlineKeyboardButton("\ud83d\udcb0 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("\ud83c\udf10 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("\ud83d\udcde Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

    elif context.user_data.get("awaiting_city"):
        city = update.message.text
        user_data.setdefault(user_id, {})["city"] = city
        await update.message.reply_text(f"Ваш город ({city}) сохранен! Возвращаю вас в меню настроек.")
        context.user_data["awaiting_city"] = False

        keyboard = [
            [InlineKeyboardButton("\ud83d\udcb0 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("\ud83c\udf10 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("\ud83d\udcde Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
            loop.close()
        asyncio.run(main())
    except RuntimeError as e:
        if "This event loop is already running" in str(e):
            logger.warning("Цикл событий уже активен. Используется альтернативный запуск.")
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            logger.error(f"Ошибка выполнения: {e}")
