# handlers/text_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.user_data import user_data

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if context.user_data.get("awaiting_sbp_phone"):
        phone = update.message.text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "СБП", "phone": phone}
        context.user_data["awaiting_sbp_phone"] = False

        keyboard = [
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["Сбер", "Т-банк", "ВТБ"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["Альфа-Банк", "Райфайзен"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in ["OZON Банк", "Яндекс Банк"]]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите банк:", reply_markup=reply_markup)

    elif context.user_data.get("awaiting_card_number"):
        card_number = update.message.text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "Номер карты", "card": card_number}
        context.user_data["awaiting_card_number"] = False

        await update.message.reply_text("Ваши реквизиты сохранены! Возвращаю вас в меню настроек.")
        keyboard = [
            [InlineKeyboardButton("💰 Реквизиты", callback_data="payment_details")],
            [InlineKeyboardButton("🌐 Выбор города", callback_data="select_city")],
            [InlineKeyboardButton("📞 Техническая поддержка", url="https://t.me/monekeny")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите настройку:", reply_markup=reply_markup)

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
