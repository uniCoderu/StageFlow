from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.ticket_storage import marketplace_data
from handlers.start_handler import start

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        ticket = marketplace_data.pop(index)
        ticket_folder = os.path.join(TICKETS_DIR, ticket["id"])
        ticket_file_path = os.path.join(ticket_folder, "ticket_file")

        await query.edit_message_text(
            f"Вы успешно купили билет \"{ticket['name']}\" за {ticket['price']} руб."
        )
        if os.path.exists(ticket_file_path):
            with open(ticket_file_path, "rb") as f:
                await query.message.reply_document(document=f, caption=f"Ваш билет: {ticket['name']}")
        await start(update, context)

    elif query.data == "sell_ticket":
        await query.edit_message_text(
            "Продажа билета:\n"
            "1️⃣ Укажите название вашего билета (например, \"Концерт XYZ\").\n"
            "Пожалуйста, введите название билета:"
        )
        context.user_data["awaiting_ticket_name"] = True