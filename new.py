import logging
import coloredlogs
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext

# Настройка логирования
coloredlogs.install(level='DEBUG', fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Константы для состояний
MENU, SELL_TICKET, SHOW_MARKET, SETTINGS = range(4)

# Команды бота
def start(update: Update, context: CallbackContext) -> int:
    """Приветствие пользователя и отображение основного меню."""
    user = update.message.from_user
    logging.info(f"User {user.username} started the bot.")
    
    keyboard = [
        ['Продать билет', 'Торговая площадка'],
        ['Настройки', 'Политика'],
    ]
    update.message.reply_text(
        "Привет! Я бот для продажи билетов на мероприятия. Что вы хотите сделать?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU

# Настройки
def settings(update: Update, context: CallbackContext) -> int:
    """Меню настроек: реквизиты, город и поддержка."""
    keyboard = [['Сохранить реквизиты', 'Выбрать город', 'Связь с тех. поддержкой']]
    update.message.reply_text(
        "Выберите опцию настройки.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SETTINGS

# Продажа билета
def sell_ticket(update: Update, context: CallbackContext) -> int:
    """Процесс продажи билета."""
    update.message.reply_text(
        "Пожалуйста, выберите тип мероприятия (например, концерт)."
    )
    return SELL_TICKET

# Торговая площадка
def show_market(update: Update, context: CallbackContext) -> int:
    """Показать торговую площадку с билетами."""
    update.message.reply_text("Вот доступные билеты. Выберите интересующее вас мероприятие.")
    return SHOW_MARKET

# Обработчик сообщения
def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработка обычных сообщений пользователя."""
    text = update.message.text
    logging.debug(f"Received message: {text}")
    
    if text == 'Продать билет':
        return sell_ticket(update, context)
    elif text == 'Торговая площадка':
        return show_market(update, context)
    elif text == 'Настройки':
        return settings(update, context)
    else:
        update.message.reply_text("Команда не распознана. Выберите одну из кнопок.")
        return MENU

# Основная функция
def main():
    """Запуск бота."""
    token = "YOUR_BOT_API_KEY"
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    
    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Для перехода по состояниям
    dp.add_handler(CallbackQueryHandler(settings, pattern='^settings$'))
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
