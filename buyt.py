import logging
import sys

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

# Хранилище данных пользователей
user_data = {}

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
        user_data[user_id]["payment_details"]["bank"] = bank_name
        await query.edit_message_text(f"Ваш выбор ({bank_name}) сохранен! Возвращаю вас в меню настроек.")

        # Возвращаем пользователя в меню настроек
        keyboard = [
            [InlineKeyboardButton("💰 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("🌍 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("📞 Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("💳 Продать билет", callback_data="sell_ticket")],
            [InlineKeyboardButton("📜 Полит. соглашение", callback_data="policy")],
            [InlineKeyboardButton("🏷️ Торговая площадка", callback_data="marketplace")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\n"
            "Используйте меню ниже для выбора нужного действия.",
            reply_markup=reply_markup
        )

    elif query.data == "edit_payment_details":
        keyboard = [
            [InlineKeyboardButton("СБП", callback_data="sbp")],
            [InlineKeyboardButton("Номер карты", callback_data="card")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите способ получения оплаты:", reply_markup=reply_markup)

# Обработчик текстовых сообщений
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Этап 2: Получение билета
    if context.user_data.get("awaiting_ticket"):
        ticket_data = update.message.text or update.message.photo or update.message.document
        if not ticket_data:
            await update.message.reply_text("Пожалуйста, отправьте билет в формате текста, фото или документа.")
            return
        user_data.setdefault(user_id, {})["ticket"] = ticket_data
        await update.message.reply_text("Билет получен. Укажите цену билета в рублях:")
        context.user_data["awaiting_ticket"] = False
        context.user_data["awaiting_price"] = True

    # Этап 3: Получение цены билета
    elif context.user_data.get("awaiting_price"):
        try:
            price = float(update.message.text)
            if price <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректную цену в рублях.")
            return
        user_data[user_id]["price"] = price
        await update.message.reply_text(
            f"Ваш билет выставлен на продажу за {price} рублей! Проверьте на торговой площадке."
        )
        context.user_data["awaiting_price"] = False

        # Этап 4: Логика для торговой площадки (упрощенно)
        # Здесь можно добавить вызов API для публикации билета или другую логику
        marketplace_list = user_data.get("marketplace", [])
        marketplace_list.append({"ticket": user_data[user_id]["ticket"], "price": price})
        user_data["marketplace"] = marketplace_list

async def sell_ticket_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Этап 1: Сообщение о продаже билетов
    if query.data == "sell_ticket":
        await query.edit_message_text(
            "Как работает продажа билета:\n"
            "1. Вы отправляете билет на мероприятие.\n"
            "2. Указываете цену.\n"
            "3. Билет будет выставлен на торговую площадку.\n"
            "Это безопасный процесс, так как все транзакции защищены."
        )
        await query.message.reply_text("Отправьте мне ваш билет (в виде фото, файла или текста):")
        context.user_data["awaiting_ticket"] = True

# Запуск бота
async def main():
    # Создаем приложение
    application = ApplicationBuilder().token(API_KEY).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем приложение
    await application.initialize()
    logger.info("Бот запущен и готов к работе.")
    await application.start()
    await application.updater.start_polling()

    # Удерживаем приложение в рабочем состоянии
    await application.updater.idle()

    # Завершаем работу
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("asyncio.run() cannot be called from a running event loop"):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
