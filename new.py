import logging
import coloredlogs
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
from telegram import ReplyKeyboardMarkup

# Настройка логирования
coloredlogs.install(level='DEBUG', fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Константы для состояний
MENU, SELL_TICKET, SHOW_MARKET, SETTINGS = range(4)

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Приветствие пользователя и отображение основного меню."""
    user = update.message.from_user
    logging.info(f"User {user.username} started the bot.")
    
    keyboard = [
        ['Продать билет', 'Торговая площадка'],
        ['Настройки', 'Политика'],
    ]
    await update.message.reply_text(
        "Привет! Я бот для продажи билетов на мероприятия. Что вы хотите сделать?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU

# Настройки
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Меню настроек: реквизиты, город и поддержка."""
    keyboard = [['Сохранить реквизиты', 'Выбрать город', 'Связь с тех. поддержкой']]
    await update.message.reply_text(
        "Выберите опцию настройки.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SETTINGS

# Продажа билета
async def sell_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Процесс продажи билета."""
    await update.message.reply_text(
        "Пожалуйста, выберите тип мероприятия (например, концерт)."
    )
    return SELL_TICKET

# Торговая площадка
async def show_market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показать торговую площадку с билетами."""
    await update.message.reply_text("Вот доступные билеты. Выберите интересующее вас мероприятие.")
    return SHOW_MARKET

# Обработчик сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка обычных сообщений пользователя."""
    text = update.message.text
    logging.debug(f"Received message: {text}")
    
    if text == 'Продать билет':
        return await sell_ticket(update, context)
    elif text == 'Торговая площадка':
        return await show_market(update, context)
    elif text == 'Настройки':
        return await settings(update, context)
    else:
        await update.message.reply_text("Команда не распознана. Выберите одну из кнопок.")
        return MENU

# Основная функция
def main():
    """Запуск бота."""
    token = "YOUR_BOT_API_KEY"
    application = Application.builder().token(token).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Для перехода по состояниям
    application.add_handler(CallbackQueryHandler(settings, pattern='^settings$'))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
