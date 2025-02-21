# handlers/marketplace_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from storage.ticket_storage import marketplace_data, TICKETS_DIR
from config import logger, PAYMASTER_API_KEY

async def marketplace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает действия, связанные с торговой площадкой."""
    query = update.callback_query
    if not query:
        logger.error("Callback query отсутствует в update")
        return
    await query.answer()

    user_id = query.from_user.id
    data = query.data
    logger.info(f"Получен callback: {data} от пользователя {user_id}")

    if data == "marketplace":
        if marketplace_data:
            ticket_buttons = [
                [InlineKeyboardButton(f"{ticket['name']} - {ticket['price']} руб.", callback_data=f"market_details_{ticket['id']}")]
                for ticket in marketplace_data
            ]
            ticket_buttons.append([InlineKeyboardButton("Назад", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(ticket_buttons)
            await query.edit_message_text("Список доступных билетов:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("На торговой площадке пока нет билетов.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Назад", callback_data="main_menu")]
            ]))

    elif data.startswith("market_details_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if ticket:
            event_details = (
                f"Информация о билете:\nМероприятие: {ticket['name']}\n"
                f"Цена: {ticket['price']} руб.\n"
                "Вы хотите купить этот билет?"
            )
            keyboard = [
                [InlineKeyboardButton("Купить", callback_data=f"buy_ticket_{ticket['id']}")],
                [InlineKeyboardButton("Назад", callback_data="marketplace")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(event_details, reply_markup=reply_markup)
        else:
            await query.edit_message_text("Билет не найден.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Назад", callback_data="marketplace")]
            ]))

    elif data.startswith("buy_ticket_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if ticket:
            title = ticket['name']
            description = f"Оплата за билет на мероприятие: {ticket['name']}"
            payload = f"purchase_{ticket['id']}"
            currency = "RUB"
            price = ticket['price']
            prices = [LabeledPrice("Билет", price * 100)]  # Цена в копейках

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
        else:
            await query.edit_message_text("Билет не найден.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Назад", callback_data="marketplace")]
            ]))