from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from utils import save_ticket, generate_ticket_id, send_invoice

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    await query.answer()

    if query.data == "marketplace":
        # Логика отображения торговой площадки
        pass

    elif query.data == "sell_ticket":
        await query.edit_message_text("Продажа билета: Пожалуйста, введите название билета:")

# Обработка ввода текста
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if context.user_data.get("awaiting_ticket_name"):
        ticket_name = update.message.text
        context.user_data["ticket_name"] = ticket_name
        context.user_data["awaiting_ticket_name"] = False
        context.user_data["awaiting_ticket_file"] = True
        await update.message.reply_text("Пожалуйста, отправьте файл или фото билета:")

    elif context.user_data.get("awaiting_ticket_file"):
        try:
            if update.message.document:
                file = await update.message.document.get_file()
                file_binary = await file.download_as_bytearray()
                file_id = update.message.document.file_id
            elif update.message.photo:
                file = await update.message.photo[-1].get_file()
                file_binary = await file.download_as_bytearray()
                file_id = update.message.photo[-1].file_id
            else:
                await update.message.reply_text("Пожалуйста, отправьте файл или фото билета.")
                return

            context.user_data["ticket_file"] = file_id
            context.user_data["ticket_file_binary"] = file_binary
            context.user_data["awaiting_ticket_file"] = False
            context.user_data["awaiting_ticket_price"] = True
            await update.message.reply_text("Введите цену билета в рублях:")

        except Exception as e:
            await update.message.reply_text(f"Ошибка при загрузке файла: {str(e)}")

    elif context.user_data.get("awaiting_ticket_price"):
        try:
            ticket_price = int(update.message.text)
            ticket_id = generate_ticket_id()
            ticket_name = context.user_data["ticket_name"]
            file_id = context.user_data["ticket_file"]
            file_binary = context.user_data["ticket_file_binary"]

            ticket_file_path = save_ticket(ticket_id, ticket_name, ticket_price, file_id, file_binary)

            await update.message.reply_text(
                f"Ваш билет \"{ticket_name}\" успешно выставлен на торговую площадку по цене {ticket_price} руб!"
            )
            context.user_data["awaiting_ticket_price"] = False
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное число для цены билета.")

