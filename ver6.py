import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, PreCheckoutQueryHandler

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
API_KEY = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

# Платежный ключ для PayMaster
PAYMASTER_API_KEY = "1744374395:TEST:236438f0df3db3a23dd9"

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
        title = ticket['name']
        description = f"Оплата за билет на мероприятие: {ticket['name']}"
        payload = f"purchase_{ticket['id']}"  # Уникальный идентификатор покупки
        currency = "RUB"  # Валюта
        price = ticket['price']  # Цена билета

        prices = [LabeledPrice("Билет", price * 100)]  # Цена в копейках

        # Отправка инвойса
        await query.message.reply_invoice(
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMASTER_API_KEY,
            currency=currency,
            prices=prices,
            start_parameter="buy_ticket",
            is_flexible=False
        )
# Обработка успешного платежа
async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает успешный платеж."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    # Проверим, что платеж был сделан по правильному инвойсу
    if payload.startswith("purchase_"):
        ticket_id = payload.split("_")[1]
        # Находим билет по ID
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if ticket:
            # Информация о билете и подтверждение
            await update.message.reply_text(f"Вы успешно купили билет на \"{ticket['name']}\"!")
            # Отправляем сам файл билета пользователю
            ticket_file_path = os.path.join(TICKETS_DIR, ticket["id"], "ticket_file")
            if os.path.exists(ticket_file_path):
                with open(ticket_file_path, "rb") as f:
                    await update.message.reply_document(document=f, caption=f"Ваш билет: {ticket['name']}")
            # После оплаты, можно удалить билет с торговой площадки
            marketplace_data.remove(ticket)
        else:
            await update.message.reply_text("Ошибка: не удалось найти билет.")

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    # Добавляем обработчик команд и запросов
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, text_handler))

    # Добавляем обработчики платежей
    application.add_handler(PreCheckoutQueryHandler(successful_payment_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    try:
        asyncio.get_event_loop().run_until_complete(main())  # Запуск основного асинхронного процесса
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")
