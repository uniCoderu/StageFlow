from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import logging

API_TOKEN = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

logging.basicConfig(level=logging.INFO)

ADD_TICKET, CONFIRM_PURCHASE = range(2)

tickets = []

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Купить билет", callback_data="buy_ticket")],
        [InlineKeyboardButton("Продать билет", callback_data="sell_ticket")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать в маркетплейс билетов! Выберите действие:", reply_markup=reply_markup)

def sell_ticket(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.edit_message_text("Введите информацию о билете в формате: название, цена, контакт.")
    return ADD_TICKET

def add_ticket(update: Update, context: CallbackContext) -> int:
    ticket_info = update.message.text
    tickets.append({"info": ticket_info, "seller_id": update.message.from_user.id})
    update.message.reply_text("Ваш билет добавлен в список!")
    return ConversationHandler.END

def list_tickets(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()
    if not tickets:
        update.callback_query.edit_message_text("Сейчас нет доступных билетов.")
        return

    for idx, ticket in enumerate(tickets):
        keyboard = [[InlineKeyboardButton("Купить", callback_data=f"buy_{idx}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(f"{idx + 1}. {ticket['info']}", reply_markup=reply_markup)

def buy_ticket(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    ticket_index = int(query.data.split("_")[1])
    ticket = tickets[ticket_index]

    if query.from_user.id == ticket["seller_id"]:
        query.edit_message_text("Вы не можете купить свой собственный билет.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{ticket_index}"),
         InlineKeyboardButton("Отменить", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Подтвердите покупку билета:", reply_markup=reply_markup)
    context.user_data["ticket_index"] = ticket_index
    return CONFIRM_PURCHASE

def confirm_purchase(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    ticket_index = context.user_data.get("ticket_index")
    ticket = tickets.pop(ticket_index)

    seller_id = ticket["seller_id"]
    buyer_id = query.from_user.id

    context.bot.send_message(seller_id, f"Ваш билет куплен! Покупатель: @{query.from_user.username}")
    query.edit_message_text("Покупка успешно завершена! Продавец уведомлен.")
    return ConversationHandler.END

def cancel_purchase(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.edit_message_text("Покупка отменена.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def main() -> None:
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CallbackQueryHandler(sell_ticket, pattern="sell_ticket"), CallbackQueryHandler(list_tickets, pattern="buy_ticket")],
        states={
            ADD_TICKET: [MessageHandler(Filters.text & ~Filters.command, add_ticket)],
            CONFIRM_PURCHASE: [
                CallbackQueryHandler(confirm_purchase, pattern="confirm_\\d+"),
                CallbackQueryHandler(cancel_purchase, pattern="cancel")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
