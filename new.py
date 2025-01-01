import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
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

# Задаем токен вашего бота
API_TOKEN = '8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU'

# Константы для состояний
MENU, SETTINGS, SELL_TICKET, VIEW_MARKETPLACE, ADMIN_MENU = range(5)

# Стартовое сообщение
def start(update: Update, context: CallbackContext) -> int:
    logger.info(f"Пользователь {update.effective_user.id} начал взаимодействие с ботом.")
    buttons = [
        [KeyboardButton("Настройки")],
        [KeyboardButton("Продать билет")],
        [KeyboardButton("Политическое соглашение")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    update.message.reply_text(
        "Привет! Я бот для перепродажи билетов на мероприятия. Вся навигация производится через меню.",
        reply_markup=reply_markup
    )
    return MENU

# Настройки
def settings(update: Update, context: CallbackContext) -> int:
    logger.info(f"Пользователь {update.effective_user.id} вошел в меню настроек.")
    buttons = [
        [InlineKeyboardButton("Добавить реквизиты", callback_data='add_payment')],
        [InlineKeyboardButton("Выбрать город", callback_data='select_city')],
        [InlineKeyboardButton("Связь с поддержкой", callback_data='support')]
    ]
    if update.effective_user.id in context.bot_data.get('admins', []):
        buttons.append([InlineKeyboardButton("Админ меню", callback_data='admin_menu')])
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text("Настройки:", reply_markup=reply_markup)
    return SETTINGS

# Продажа билета
def sell_ticket(update: Update, context: CallbackContext) -> int:
    logger.info(f"Пользователь {update.effective_user.id} выбрал продажу билета.")
    update.message.reply_text(
        "Выберите мероприятие и отправьте файл с билетом.")
    return SELL_TICKET

# Торговая площадка
def view_marketplace(update: Update, context: CallbackContext) -> int:
    logger.info(f"Пользователь {update.effective_user.id} просматривает торговую площадку.")
    city = context.user_data.get('city', 'Все города')
    update.message.reply_text(f"Список мероприятий в городе {city}:")
    # Пример мероприятий для теста
    events = ["Концерт A", "Концерт B", "Спектакль C"]
    for event in events:
        update.message.reply_text(event)
    return VIEW_MARKETPLACE

# Обработчик ошибок
def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(f"Произошла ошибка: {context.error}")

# Основная функция
def main() -> None:
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    # Обработчики команд
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                MessageHandler(Filters.regex("^Настройки$"), settings),
                MessageHandler(Filters.regex("^Продать билет$"), sell_ticket),
                MessageHandler(Filters.regex("^Политическое соглашение$"), lambda update, _: update.message.reply_text("Политическое соглашение"))
            ],
            SETTINGS: [CallbackQueryHandler(settings)],
            SELL_TICKET: [MessageHandler(Filters.document, lambda update, _: update.message.reply_text("Билет загружен."))],
            VIEW_MARKETPLACE: [MessageHandler(Filters.text & ~Filters.command, view_marketplace)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
