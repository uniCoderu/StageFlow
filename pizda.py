from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import logging

API_TOKEN = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

logging.basicConfig(level=logging.INFO)

ADD_NAME, ADD_PRICE, ADD_FILE = range(3)

tickets = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Купить билет", callback_data="buy_ticket")],
        [InlineKeyboardButton("Продать билет", callback_data="sell_ticket")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в маркетплейс билетов! Выберите действие:", reply_markup=reply_markup)

async def sell_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите название билета:")
    return ADD_NAME

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"Received ticket name: {update.message.text}")
    await update.message.reply_text("Введите цену билета:")
    return ADD_PRICE
    
async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price = float(update.message.text)
        logging.info(f"Received ticket price: {price}")
        await update.message.reply_text("Билет добавлен успешно!")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Цена должна быть числом. Попробуйте снова:")
        return ADD_PRICE

async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.document:
        ticket_file = update.message.document
        ticket_data = {
            "name": context.user_data['ticket_name'],
            "price": context.user_data['ticket_price'],
            "file_id": ticket_file.file_id,
            "seller_id": update.message.from_user.id
        }
        tickets.append(ticket_data)
        await update.message.reply_text("Ваш билет успешно добавлен!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, загрузите файл с билетом:")
        return ADD_FILE

async def list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not tickets:
        await query.edit_message_text("Сейчас нет доступных билетов.")
        return

    for idx, ticket in enumerate(tickets):
        keyboard = [[InlineKeyboardButton("Купить", callback_data=f"buy_{idx}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"{idx + 1}. {ticket['name']} - {ticket['price']} руб.",
            reply_markup=reply_markup
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)],
            ADD_FILE: [MessageHandler(filters.Document.ALL, add_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(sell_ticket, pattern="sell_ticket"))
    application.add_handler(CallbackQueryHandler(list_tickets, pattern="buy_ticket"))

    application.run_polling()

if __name__ == "__main__":
    main()
