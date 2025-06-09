# handlers/marketplace_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from storage.ticket_storage import marketplace_data
from config import logger, PAYMASTER_API_KEY

async def marketplace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Общий хэндлер торговой площадки:
    – показать список лотов
    – начать продажу
    – показать детали
    – инициировать оплату
    Поддерживает и callback_query, и команду /marketplace.
    """
    # 1) Определяем источник вызова
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        send = lambda text, **kwargs: query.edit_message_text(text, **kwargs)
        reply_target = query.message
        data = query.data
        user_id = query.from_user.id
    else:
        # команда /marketplace
        msg = update.message
        send = lambda text, **kwargs: msg.reply_text(text, **kwargs)
        reply_target = msg
        data = "marketplace"
        user_id = msg.from_user.id

    logger.info(f"[Marketplace] user={user_id} data={data}")

    # 2) Главное меню торговой площадки
    if data == "marketplace":
        buttons = [[InlineKeyboardButton("💳 Продать билет", callback_data="sell_ticket")]]
        for ticket in marketplace_data:
            buttons.append([
                InlineKeyboardButton(
                    f"{ticket['name']} — {ticket['price']}₽",
                    callback_data=f"market_details_{ticket['id']}"
                )
            ])
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        markup = InlineKeyboardMarkup(buttons)
        await send("🔎 Торговая площадка:", reply_markup=markup)
        return

    # 3) Запуск продажи
    if data == "sell_ticket":
        await send(
            "💳 Продажа билета:\n"
            "1️⃣ Введите название билета (например, «Концерт XYZ»)\n"
            "2️⃣ Затем укажите цену в рублях"
        )
        context.user_data["awaiting_ticket_name"] = True
        return

    # 4) Детали выбранного лота
    if data.startswith("market_details_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if str(t["id"]) == ticket_id), None)
        if not ticket:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Назад", callback_data="marketplace")]]
            )
            await send("❌ Билет не найден.", reply_markup=markup)
            return

        text = (
            f"🎫 *{ticket['name']}*\n"
            f"💰 *{ticket['price']}*₽\n\n"
            "Хотите купить?"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Купить", callback_data=f"buy_ticket_{ticket_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="marketplace")]
        ])
        await send(text, reply_markup=markup, parse_mode="Markdown")
        return

    # 5) Начало оплаты
    if data.startswith("buy_ticket_"):
        ticket_id = data.split("_")[2]
        ticket = next((t for t in marketplace_data if str(t["id"]) == ticket_id), None)
        if not ticket:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Назад", callback_data="marketplace")]]
            )
            await send("❌ Билет не найден.", reply_markup=markup)
            return

        prices = [LabeledPrice("Билет", ticket["price"] * 100)]  # в копейках
        await reply_target.reply_invoice(
            title=ticket["name"],
            description=f"Оплата за билет: {ticket['name']}",
            payload=f"purchase_{ticket_id}",
            provider_token=PAYMASTER_API_KEY,
            currency="RUB",
            prices=prices,
            start_parameter="buy_ticket",
            is_flexible=False
        )
        return
