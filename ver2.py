import logging
import sys

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
except ModuleNotFoundError:
    sys.stderr.write("Модуль 'telegram' не найден. Установите его командой 'pip install python-telegram-bot' и попробуйте снова.\n")
    sys.exit(1)

# Настраиваем логирование
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"{record.msg}"
        return super().format(record)

formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Ваш Telegram API ключ
API_KEY = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

# Хранилище данных пользователей
user_data = {}

# Основная команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start и выводит приветственное сообщение."""
    keyboard = [
        [InlineKeyboardButton("Настройки", callback_data="settings")],
        [InlineKeyboardButton("Продать билет", callback_data="sell_ticket")],
        [InlineKeyboardButton("Политика соглашения", callback_data="policy")],
        [InlineKeyboardButton("Торговая площадка", callback_data="marketplace")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\n"
            "Используйте меню ниже для выбора нужного действия.",
            reply_markup=reply_markup
        )

# Добавление функциональности торговой площадки
async def marketplace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие на кнопку 'Торговая площадка'."""
    query = update.callback_query
    await query.answer()

    # Заглушка для списка билетов
    tickets = [
        {"event": "Концерт группы XYZ", "price": 2000, "details": "market_details_1"},
        {"event": "Футбольный матч", "price": 1500, "details": "market_details_2"},
    ]

    ticket_buttons = [
        [InlineKeyboardButton(f"{ticket['event']} - {ticket['price']} руб.", callback_data=ticket["details"])]
        for ticket in tickets
    ]
    ticket_buttons.append([InlineKeyboardButton("Назад", callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(ticket_buttons)
    await query.edit_message_text("Список доступных билетов:", reply_markup=reply_markup)

# Просмотр информации о мероприятии
async def event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает полную информацию о мероприятии и позволяет предложить свою цену."""
    query = update.callback_query
    await query.answer()

    event_details = "Это пример полной информации о мероприятии."
    keyboard = [
        [InlineKeyboardButton("Предложить свою цену", callback_data="offer_price")],
        [InlineKeyboardButton("Назад", callback_data="marketplace")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(event_details, reply_markup=reply_markup)

# Обработка предложения цены
async def offer_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позволяет пользователю предложить свою цену за билет."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Введите вашу цену:")
    context.user_data["awaiting_offer_price"] = True

# Обработка пользовательского ввода для цены
async def handle_offer_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет предложенную цену пользователя."""
    if context.user_data.get("awaiting_offer_price"):
        try:
            offered_price = int(update.message.text)
            await update.message.reply_text(f"Ваша цена {offered_price} руб. отправлена продавцу!")
            context.user_data["awaiting_offer_price"] = False
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное число.")

# Добавляем обработчики
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(marketplace_handler, pattern="marketplace"))
    application.add_handler(CallbackQueryHandler(event_details, pattern="market_details_.*"))
    application.add_handler(CallbackQueryHandler(offer_price, pattern="offer_price"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_offer_price))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()


if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")
