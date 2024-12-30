import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CallbackContext
from pyngrok import ngrok
import os
from flask import Flask, request

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
GENDER, CITY, PAYMENT_METHOD, EVENT_TYPE, TICKET_FILE, PRICE, AGREEMENT = range(7)

# Установим Flask и ngrok для работы в Google Colab (если необходимо)
app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram bot is running"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    dispatcher.process_update(update)
    return 'ok', 200

# Основная функция старта
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f"User {user.first_name} started the bot.")

    # Главное меню с кнопками
    keyboard = [
        [KeyboardButton("Продать билет"), KeyboardButton("Торговая площадка")],
        [KeyboardButton("Настройки"), KeyboardButton("Политическое соглашение")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Привет! Я помогу тебе с продажей билетов. Выберите нужный раздел.", reply_markup=reply_markup)

# Меню настроек
async def settings(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Реквизиты для оплаты"), KeyboardButton("Город")],
        [KeyboardButton("Связь с техподдержкой")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Выберите настройки:", reply_markup=reply_markup)

# Продажа билета
async def sell_ticket(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Концерт"), KeyboardButton("Спортивное мероприятие")],
        [KeyboardButton("Театр"), KeyboardButton("Другие мероприятия")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Выберите тип мероприятия, для которого хотите продать билет:", reply_markup=reply_markup)

    return EVENT_TYPE

# Обработка выбора типа мероприятия
async def event_type(update: Update, context: CallbackContext):
    user_choice = update.message.text
    context.user_data['event_type'] = user_choice
    logger.info(f"User selected event type: {user_choice}")

    await update.message.reply_text("Пожалуйста, загрузите файл с билетом.")
    return TICKET_FILE

# Загрузка билета
async def ticket_file(update: Update, context: CallbackContext):
    file = update.message.document
    context.user_data['ticket_file'] = file
    await update.message.reply_text("Введите цену, за которую вы хотите продать билет:")
    return PRICE

# Указание цены
async def price(update: Update, context: CallbackContext):
    price = update.message.text
    context.user_data['price'] = price
    await update.message.reply_text(f"Вы хотите продать билет за {price} рублей. Подтвердите, пожалуйста.")

    keyboard = [
        [InlineKeyboardButton("Я согласен", callback_data='agree')],
        [InlineKeyboardButton("Я не согласен", callback_data='disagree')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Подтвердите продажу:", reply_markup=reply_markup)
    return AGREEMENT

# Обработка подтверждения продажи
async def agreement(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'agree':
        # Логика добавления билета на торговую площадку
        await query.edit_message_text("Ваш билет добавлен на торговую площадку!")
        logger.info(f"Ticket successfully listed for sale at {context.user_data['price']}")

    else:
        await query.edit_message_text("Вы отменили продажу.")
    return ConversationHandler.END

# Настройка webhook для Google Colab
def setup_webhook():
    public_url = ngrok.connect(5000)
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")
    bot.set_webhook(public_url + "/webhook")

# Основная функция для запуска
def main():
    # Ваш токен Telegram бота
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type)],
            TICKET_FILE: [MessageHandler(filters.Document(), ticket_file)],  # Исправлено здесь
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            AGREEMENT: [CallbackQueryHandler(agreement)],
        },
        fallbacks=[CommandHandler('settings', settings)],
    )

    application.add_handler(conv_handler)

    # Запускаем Flask сервер для работы с webhook
    setup_webhook()
    app.run(port=5000)

if __name__ == '__main__':
    main()
