# handlers/menu_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.user_data import user_data
from config import logger

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        logger.error("Callback query отсутствует в update")
        return
    await query.answer()

    user_id = query.from_user.id
    data = query.data
    logger.info(f"Получен callback: {data} от пользователя {user_id}")

    if data == "settings":
        keyboard = [
            [InlineKeyboardButton("💰 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("🌐 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("📞 Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Пожалуйста, выберите одну из настроек:", reply_markup=reply_markup)

    elif data == "payment_details":
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

    elif data == "sbp":
        await query.edit_message_text("Введите номер телефона, привязанный к банку:")
        context.user_data["awaiting_sbp_phone"] = True

    elif data == "card":
        await query.edit_message_text("Введите номер вашей карты:")
        context.user_data["awaiting_card_number"] = True

    elif data == "edit_payment_details":
        keyboard = [
            [InlineKeyboardButton("СБП", callback_data="sbp")],
            [InlineKeyboardButton("Номер карты", callback_data="card")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите способ получения оплаты:", reply_markup=reply_markup)

    elif data.startswith("bank_"):
        bank_name = data.split("_")[1]
        user_data[user_id]["payment_details"]["bank"] = bank_name
        await query.edit_message_text(f"Ваш выбор ({bank_name}) сохранен! Возвращаю вас в меню настроек.")
        keyboard = [
            [InlineKeyboardButton("💰 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("🌐 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("📞 Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

    elif data == "select_city":
        await query.edit_message_text("Введите название вашего города:")
        context.user_data["awaiting_city"] = True
        logger.info(f"Ожидаем ввод города для пользователя {user_id}")

    elif data == "main_menu":
        # Упрощаем возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🏧 Торговая площадка", callback_data="marketplace_menu")],
            [InlineKeyboardButton("📜 Полит. соглашение", callback_data="policy")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.\n"
            "Используйте меню ниже для выбора нужного действия.",
            reply_markup=reply_markup
        )
        logger.info(f"Возврат в главное меню для пользователя {user_id}")
