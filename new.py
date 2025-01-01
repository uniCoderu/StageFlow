import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from colorlog import ColoredFormatter

# Настройка логирования
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Токен вашего бота
API_TOKEN = '8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU'

# Константы для состояний
MENU, SETTINGS, SELL_TICKET, VIEW_MARKETPLACE = range(4)

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} начал взаимодействие с ботом.")
    buttons = [
        [KeyboardButton("Настройки")],
        [KeyboardButton("Продать билет")],
        [KeyboardButton("Политическое соглашение")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот для перепродажи билетов на мероприятия. Вся навигация производится через меню.",
        reply_markup=reply_markup
    )
    return MENU

# Настройки
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} вошел в меню настроек.")
    buttons = [
        [InlineKeyboardButton("Добавить реквизиты", callback_data='add_payment')],
        [InlineKeyboardButton("Выбрать город", callback_data='select_city')],
        [InlineKeyboardButton("Связь с поддержкой", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Настройки:", reply_markup=reply_markup)
    return SETTINGS

# Продажа билета
async def sell_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} выбрал продажу билета.")
    await update.message.reply_text(
        "Отправьте файл билета и укажите его цену.")
    return SELL_TICKET

# Обработка загрузки билета
async def handle_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} загрузил билет.")
    await update.message.reply_text("Ваш билет был успешно добавлен на торговую площадку.")
    return MENU

# Торговая площадка
async def view_marketplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} просматривает торговую площадку.")
    city = context.user_data.get('city', 'Все города')
    await update.message.reply_text(f"Список мероприятий в городе {city}:")
    # Пример мероприятий для теста
    events = ["Концерт A", "Концерт B", "Спектакль C"]
    for event in events:
        await update.message.reply_text(event)
    return VIEW_MARKETPLACE

# Политическое соглашение
async def policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Политическое соглашение: ...")
    return MENU

# Обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Произошла ошибка: {context.error}")

# Основная функция
async def main():
    application = ApplicationBuilder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                MessageHandler(filters.Regex("^Настройки$"), settings),
                MessageHandler(filters.Regex("^Продать билет$"), sell_ticket),
                MessageHandler(filters.Regex("^Политическое соглашение$"), policy)
            ],
            SETTINGS: [CallbackQueryHandler(settings)],
            SELL_TICKET: [MessageHandler(filters.Document.ALL, handle_ticket)],
            VIEW_MARKETPLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, view_marketplace)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
