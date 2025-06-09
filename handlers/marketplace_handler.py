# handlers/marketplace_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from storage.ticket_storage import marketplace_data, TICKETS_DIR
from config import logger, PAYMASTER_API_KEY

async def marketplace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает и показ списка лотов, и детали, и продажу/покупку."""
    # Определяем, кто и откуда вызвал:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        send = lambda text, **kwargs: query.edit_message_text(text, **kwargs)
        user_id = query.from_user.id
        data = query.data
    else:
        # команда /marketplace или MessageHandler
        msg = update.message
        send = lambda text, **kwargs: msg.reply_text(text, **kwargs)
        user_id = msg.from_user.id
        data = "marketplace"

    logger.info(f"[Marketplace] вызвано пользователем {user_id} с data={data}")

    # 1) Главное меню маркетплейса
    if data == "marketplace":
        keyboard = [
            [InlineKeyboardButton("💳 Продать билет", callback_data="sell_ticket")]
        ]
        # список лотов
        for ticket in marketplace_data:
            btn = InlineKeyboardButton(
                f"{ticket['name']} — {ticket['price']}₽",
                callback_data=f"market_details_{ticket['id']}"
            )
            keyboard.append([btn])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])

        markup = InlineKeyboardMarkup(keyboard)
        await send("🔎 Торговая площадка:", reply_markup=markup)
        return

    # 2) Начало продажи
    if data == "sell_ticket":
        await send(
            "💳 Продажа билета:\n"
            "1️⃣ Введите название (например, «Концерт XYZ»)\n"
            "2️⃣ После названия укажите цену в рублях"
        )
        context.user_data["awaiting_ticket_name"] = True
        return

    # 3) Детали конкретного лота
    if data.startswith("market_details_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if not ticket:
            await send("⚠️ Билет не найден.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="marketplace")]
            ]))
            return

        text = (
            f"🎫 *{ticket['name']}*\n"
            f"💰 Цена: *{ticket['price']}*₽\n\n"
            "Хотите купить?"
        )
        buy_btn = InlineKeyboardButton("✅ Купить", callback_data=f"buy_ticket_{ticket_id}")
        back_btn = InlineKeyboardButton("🔙 Назад", callback_data="marketplace")
        await send(text, reply_markup=InlineKeyboardMarkup([[buy_btn], [back_btn]]), parse_mode="Markdown")
        return

    # 4) Оплата выбранного лота
    if data.startswith("buy_ticket_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if not ticket:
            await send("⚠️ Билет не найден.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="marketplace")]
            ]))
            return

        title = ticket['name']
        description = f"Оплата билета: {ticket['name']}"
        payload = f"purchase_{ticket_id}"
        prices = [LabeledPrice("Билет", ticket['price'] * 100)]  # в копейках

        # шлём invoice
        await query.message.reply_invoice(
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMASTER_API_KEY,
            currency="RUB",
            prices=prices,
            start_parameter="buy_ticket",
            is_flexible=False
        )
        return
