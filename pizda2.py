from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import logging

API_TOKEN = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

logging.basicConfig(level=logging.INFO)

ADD_TICKET, CONFIRM_PURCHASE = range(2)

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
    await query.edit_message_text("Введите информацию о билете в формате: название, цена, контакт.")
    return ADD_TICKET

async def add_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ticket_info = update.message.text
    tickets.append({"info": ticket_info, "seller_id": update.message.from_user.id})
    await update.message.reply_text("Ваш билет добавлен в список!")
    return ConversationHandler.END

async def list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not tickets:
        await query.edit_message_text("Сейчас нет доступных билетов.")
        return

    for idx, ticket in enumerate(tickets):
        keyboard = [[InlineKeyboardButton("Купить", callback_data=f"buy_{idx}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"{idx + 1}. {ticket['info']}", reply_markup=reply_markup)

async def buy_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    ticket_index = int(query.data.split("_")[1])
    ticket = tickets[ticket_index]

    if query.from_user.id == ticket["seller_id"]:
        await query.edit_message_text("Вы не можете купить свой собственный билет.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{ticket_index}"),
         InlineKeyboardButton("Отменить", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Подтвердите покупку билета:", reply_markup=reply_markup)
    context.user_data["ticket_index"] = ticket_index
    return CONFIRM_PURCHASE

async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    ticket_index = context.user_data.get("ticket_index")
    ticket = tickets.pop(ticket_index)

    seller_id = ticket["seller_id"]
    buyer_id = query.from_user.id

    await context.bot.send_message(seller_id, f"Ваш билет куплен! Покупатель: @{query.from_user.username}")
    await query.edit_message_text("Покупка успешно завершена! Продавец уведомлен.")
    return ConversationHandler.END

async def cancel_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Покупка отменена.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ADD_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_ticket)],
            CONFIRM_PURCHASE: [
                CallbackQueryHandler(confirm_purchase, pattern="confirm_\\d+"),
                CallbackQueryHandler(cancel_purchase, pattern="cancel")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(sell_ticket, pattern="sell_ticket"))
    application.add_handler(CallbackQueryHandler(list_tickets, pattern="buy_ticket"))

    application.run_polling()

if __name__ == "__main__":
    main()
