# handlers/text_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.user_data import user_data
from config import logger
from handlers.menu_handler import show_settings_menu

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    logger.info(f"Получен текст от пользователя {user_id}: {update.message.text}")

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
        await show_settings_menu(update, context)  # Используем тот же текст по умолчанию

    elif context.user_data.get("awaiting_city"):
        city = update.message.text
        user_data.setdefault(user_id, {})["city"] = city
        context.user_data["awaiting_city"] = False

        await update.message.reply_text(f"Ваш город ({city}) сохранен! Возвращаю вас в меню настроек.")
        await show_settings_menu(update, context)  # Используем тот же текст по умолчанию
        logger.info(f"Город {city} сохранен для пользователя {user_id}")

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
