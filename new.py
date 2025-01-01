import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CallbackContext
import nest_asyncio  # Для корректной работы с уже существующим циклом событий в Colab

# Применяем nest_asyncio, чтобы обойти конфликт циклов
nest_asyncio.apply()

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Настройки бота
API_KEY = '8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU'  # Замените на ваш API ключ

# Состояния для разговоров
SELECT_MENU, SETTINGS, SELL_TICKET, CHOOSE_EVENT, CONFIRM_SALE, WAITING_FOR_PRICE = range(6)

# Хранилище для пользователей и билетов
users_data = {}
tickets_for_sale = {}

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = {'city': '', 'payment_method': '', 'phone': ''}

    # Логируем входное сообщение
    logger.info(f"User {user_id} started the bot.")

    # Создаем меню
    keyboard = [
        [InlineKeyboardButton("Продать билет", callback_data='sell_ticket')],
        [InlineKeyboardButton("Торговая площадка", callback_data='market')],
        [InlineKeyboardButton("Настройки", callback_data='settings')],
        [InlineKeyboardButton("Политика конфиденциальности", callback_data='privacy_policy')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем меню пользователю
    await update.message.reply_text("Добро пожаловать в бот для перепродажи билетов! Выберите действие:", reply_markup=reply_markup)

# Обработчик для кнопки "Продать билет"
async def sell_ticket(update: Update, context: CallbackContext):
    logger.info("User clicked 'Продать билет'")

    explanation = """
    🎟️ **Как продать билет**:
    
    1️⃣ **Шаг 1**: Скиньте файл с билетом на мероприятие (фото, скан).
    
    2️⃣ **Шаг 2**: Укажите цену, за которую вы хотите продать билет.
    
    3️⃣ **Шаг 3**: После этого ваш билет будет выставлен на торговую площадку.
    
    После покупки билета мы свяжемся с вами для подтверждения, и вы получите оплату.
    """
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(explanation)

    return WAITING_FOR_PRICE

# Обработчик для получения файла с билетом
async def receive_ticket_file(update: Update, context: CallbackContext):
    if update.message.document:
        user_id = update.message.from_user.id
        ticket_file = update.message.document

        # Сохраняем билет
        tickets_for_sale[user_id] = {'file_id': ticket_file.file_id}
        
        logger.info(f"User {user_id} uploaded a ticket file.")

        await update.message.reply_text("Билет получен! Теперь укажите цену, за которую вы хотите его продать:")

        return WAITING_FOR_PRICE
    else:
        await update.message.reply_text("Пожалуйста, отправьте файл с билетом.")
        return WAITING_FOR_PRICE

# Обработчик для получения цены билета
async def receive_price(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    ticket_price = update.message.text

    try:
        ticket_price = float(ticket_price)
        if ticket_price <= 0:
            raise ValueError("Цена должна быть больше нуля.")
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную цену (например, 5000).")
        return WAITING_FOR_PRICE

    if user_id in tickets_for_sale:
        tickets_for_sale[user_id]['price'] = ticket_price
        await update.message.reply_text(f"Вы установили цену на билет: {ticket_price}₽. Билет будет выставлен на торговую площадку.")
        
        logger.info(f"User {user_id} set the price: {ticket_price}₽")

        await update.message.reply_text(f"Билет на сумму {ticket_price}₽ теперь доступен на торговой площадке!")

    return SELECT_MENU

# Обработчик для кнопки "Торговая площадка"
async def show_marketplace(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not tickets_for_sale:
        await update.message.reply_text("На данный момент нет доступных билетов на продажу.")
        return

    available_tickets = "\n".join(
        [f"Билет: {ticket['file_id']} - Цена: {ticket['price']}₽" for ticket in tickets_for_sale.values()]
    )
    await update.message.reply_text(f"Доступные билеты:\n{available_tickets}")

# Обработчик для кнопки "Настройки"
async def settings(update: Update, context: CallbackContext):
    logger.info("User clicked 'Настройки'")

    keyboard = [
        [InlineKeyboardButton("Выбрать город", callback_data='choose_city')],
        [InlineKeyboardButton("Указать реквизиты", callback_data='set_payment')],
        [InlineKeyboardButton("Связь с тех. поддержкой", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Настройки", reply_markup=reply_markup)

# Главная функция
async def main():
    application = Application.builder().token(API_KEY).build()

    # Обработчики кнопок
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELL_TICKET: [CallbackQueryHandler(sell_ticket, pattern='sell_ticket')],
            WAITING_FOR_PRICE: [MessageHandler(filters.Document.ALL, receive_ticket_file), MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Обработчик для торговой площадки и настроек
    application.add_handler(CallbackQueryHandler(show_marketplace, pattern='market'))
    application.add_handler(CallbackQueryHandler(settings, pattern='settings'))

    # Добавляем ConversationHandler
    application.add_handler(conversation_handler)

    # Запуск бота с использованием уже существующего цикла событий в Colab
    await application.run_polling()

# В Google Colab используем уже существующий цикл событий:
await main()
