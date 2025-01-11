import logging
import sys
import os

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
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
# Токен платежной системы PayMaster
PAYMENT_TOKEN = "1744374395:TEST:236438f0df3db3a23dd9"

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

# Сохранение информации о билете и файла
def save_ticket(ticket_id, name, price, file_id, file_binary):
    ticket_folder = os.path.join(TICKETS_DIR, ticket_id)
    if not os.path.exists(ticket_folder):
        os.makedirs(ticket_folder)

    # Сохраняем информацию о билете
    info_path = os.path.join(ticket_folder, "info.txt")
    with open(info_path, "w") as f:
        f.write(f"Название: {name}\n")
        f.write(f"Цена: {price}\n")
        f.write(f"ID файла: {file_id}\n")

    # Сохраняем файл билета
    file_path = os.path.join(ticket_folder, "ticket_file")
    with open(file_path, "wb") as f:
        f.write(file_binary)
    return file_path

# Функция для отправки инвойса
async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, ticket):
    """
    Отправляет инвойс пользователю для оплаты.
    :param update: Объект Update от Telegram.
    :param context: Контекст выполнения.
    :param ticket: Словарь с информацией о билете (id, name, price).
    """
    prices = [LabeledPrice(label=ticket['name'], amount=ticket['price'] * 100)]  # цена в копейках
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=ticket['name'],
        description=f"Оплата за билет: {ticket['name']}",
        payload=f"ticket_{ticket['id']}",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="buy-ticket"
    )

# Обработчик успешной оплаты
async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает успешный платеж.
    :param update: Объект Update от Telegram.
    :param context: Контекст выполнения.
    """
    payment_info = update.message.successful_payment
    await update.message.reply_text(
        f"Спасибо за покупку! Ваш платеж на сумму {payment_info.total_amount / 100:.2f} {payment_info.currency} был успешно обработан."
    )

# Основная команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start и выводит приветственное сообщение."""
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

# Обработчик кнопок меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки меню."""
    query = update.callback_query
    await query.answer()

    if query.data == "settings":
        keyboard = [
            [InlineKeyboardButton("💰 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("🌍 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("📞 Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Пожалуйста, выберите одну из настроек:", reply_markup=reply_markup)

    elif query.data == "main_menu":
        await start(update, context)

    elif query.data == "marketplace":
        if marketplace_data:
            ticket_buttons = [
                [InlineKeyboardButton(f"{ticket['name']} - {ticket['price']} руб.", callback_data=f"market_details_{i}")]
                for i, ticket in enumerate(marketplace_data)
            ]
            ticket_buttons.append([InlineKeyboardButton("Назад", callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(ticket_buttons)
            await query.edit_message_text("Список доступных билетов:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("На торговой площадке пока нет билетов.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Назад", callback_data="main_menu")]
            ]))

    elif query.data.startswith("market_details_"):
        index = int(query.data.split("_")[2])
        ticket = marketplace_data[index]
        event_details = (
            f"Информация о билете:\nМероприятие: {ticket['name']}\n"
            f"Цена: {ticket['price']} руб.\n"
            "Вы хотите купить этот билет?"
        )
        keyboard = [
            [InlineKeyboardButton("Купить", callback_data=f"buy_ticket_{index}")],
            [InlineKeyboardButton("Назад", callback_data="marketplace")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(event_details, reply_markup=reply_markup)

    elif query.data.startswith("buy_ticket_"):
        index = int(query.data.split("_")[2])
        ticket = marketplace_data[index]
        await send_invoice(update, context, ticket)  # Отправляем инвойс

    elif query.data == "sell_ticket":
        await query.edit_message_text(
            "Продажа билета:\n"
            "1️⃣ Укажите название вашего билета (например, \"Концерт XYZ\").\n"
            "Пожалуйста, введите название билета:"
        )
        context.user_data["awaiting_ticket_name"] = True

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()

    try:
        loop = asyncio.get_event_loop()
        logger.info("Цикл событий запускается...")
        loop.create_task(main())  # Добавляем main как задачу
        loop.run_forever()  # Оставляем цикл событий активным
    except KeyboardInterrupt:
        logger.info("Остановка бота вручную...")
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")

