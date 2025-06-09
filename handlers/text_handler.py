# handlers/text_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.user_data import user_data
from storage.ticket_storage import (
    load_marketplace_data,
    save_marketplace_data,
    generate_ticket_id,
    save_ticket
)
from config import logger
from handlers.menu_handler import show_settings_menu
from handlers.marketplace_handler import marketplace_handler

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    message_text = update.message.text or ''
    logger.info(f"Получен текст от пользователя {user_id}: {message_text}")

    # 1) Сохранение реквизитов SBP
    if context.user_data.get("awaiting_sbp_phone"):
        phone = message_text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "СБП", "phone": phone}
        context.user_data.pop("awaiting_sbp_phone", None)
        # Предлагаем выбрать банк
        keyboard = [
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in 
             ["Сбер", "Т-банк", "ВТБ"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in 
             ["Альфа-Банк", "Райфайзен"]],
            [InlineKeyboardButton(bank, callback_data=f"bank_{bank}") for bank in 
             ["OZON Банк", "Яндекс Банк"]]
        ]
        await update.message.reply_text("Выберите банк:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # 2) Сохранение номера карты
    if context.user_data.get("awaiting_card_number"):
        card_number = message_text
        user_data.setdefault(user_id, {})["payment_details"] = {"method": "Номер карты", "card": card_number}
        context.user_data.pop("awaiting_card_number", None)
        await update.message.reply_text("Ваши реквизиты сохранены! Возвращаю вас в меню настроек.")
        await show_settings_menu(update, context)
        return

    # 3) Сохранение города
    if context.user_data.get("awaiting_city"):
        city = message_text
        user_data.setdefault(user_id, {})["city"] = city
        context.user_data.pop("awaiting_city", None)
        await update.message.reply_text(f"Ваш город ({city}) сохранен! Возвращаю вас в меню настроек.")
        await show_settings_menu(update, context)
        return

    # 4) Начало создания нового билета: ожидаем название
    if context.user_data.get("awaiting_ticket_name"):
        ticket_name = message_text
        user_data.setdefault(user_id, {})["ticket_name"] = ticket_name
        context.user_data.pop("awaiting_ticket_name", None)
        context.user_data["awaiting_ticket_file"] = True
        await update.message.reply_text("Пожалуйста, отправьте файл или фото билета:")
        return

    # 5) Обработка файла/фото билета
    if context.user_data.get("awaiting_ticket_file"):
        file_id = None
        file_binary = None
        try:
            if update.message.document:
                file_obj = await update.message.document.get_file()
                file_binary = await file_obj.download_as_bytearray()
                file_id = update.message.document.file_id
            elif update.message.photo:
                photo = update.message.photo[-1]
                file_obj = await photo.get_file()
                file_binary = await file_obj.download_as_bytearray()
                file_id = photo.file_id
            else:
                await update.message.reply_text("Пожалуйста, отправьте документ или фото билета.")
                return
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла: {e}")
            await update.message.reply_text("Не удалось получить файл. Попробуйте снова.")
            return

        # Сохраняем в user_data и переходим к цене
        user_data[user_id]["ticket_file"] = file_id
        user_data[user_id]["ticket_file_binary"] = file_binary
        context.user_data.pop("awaiting_ticket_file", None)
        context.user_data["awaiting_ticket_price"] = True
        await update.message.reply_text("Введите цену билета в рублях:")
        return

    # 6) Обработка цены: финализация создания билета
    if context.user_data.get("awaiting_ticket_price"):
        try:
            ticket_price = int(message_text)
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное число для цены билета.")
            return

        # Получаем данные
        ticket_id = generate_ticket_id()
        ticket_name = user_data[user_id].pop("ticket_name")
        file_id = user_data[user_id].pop("ticket_file")
        file_binary = user_data[user_id].pop("ticket_file_binary")

        # Сохраняем файл на диск
        ticket_file_path = save_ticket(ticket_id, ticket_name, ticket_price, file_id, file_binary)

        # Обновляем JSON-хранилище
        tickets = load_marketplace_data()
        tickets.append({
            "id": ticket_id,
            "name": ticket_name,
            "price": ticket_price,
            "seller_id": user_id,
            "file_id": file_id,
            "file_path": ticket_file_path
        })
        save_marketplace_data(tickets)

        # Сообщаем пользователю и показываем площадку
        await update.message.reply_text(
            f"✅ Ваш билет \"{ticket_name}\" успешно выставлен на торговую площадку по цене {ticket_price} ₽!"
        )
        context.user_data.pop("awaiting_ticket_price", None)
        # Редирект в маркетплейс
        await marketplace_handler(update, context)
        return

    # Если никакое состояние не активировано
    await update.message.reply_text("Пожалуйста, выберите действие из меню.")
