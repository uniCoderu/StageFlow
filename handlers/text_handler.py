# handlers/text_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage.user_data import user_data
from storage.ticket_storage import save_ticket, generate_ticket_id, marketplace_data
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
        await show_settings_menu(update, context)

    elif context.user_data.get("awaiting_city"):
        city = update.message.text
        user_data.setdefault(user_id, {})["city"] = city
        context.user_data["awaiting_city"] = False
        await update.message.reply_text(f"Ваш город ({city}) сохранен! Возвращаю вас в меню настроек.")
        await show_settings_menu(update, context)

    elif context.user_data.get("awaiting_ticket_name"):
        ticket_name = update.message.text
        user_data.setdefault(user_id, {})["ticket_name"] = ticket_name
        context.user_data["awaiting_ticket_name"] = False
        context.user_data["awaiting_ticket_file"] = True
        await update.message.reply_text("Пожалуйста, отправьте файл или фото билета:")

    elif context.user_data.get("awaiting_ticket_file"):
        try:
            if update.message.document:
                file = await update.message.document.get_file()
                file_binary = await file.download_as_bytearray()
                file_id = update.message.document.file_id
            elif update.message.photo:
                file = await update.message.photo[-1].get_file()
                file_binary = await file.download_as_bytearray()
                file_id = update.message.photo[-1].file_id
            else:
                await update.message.reply_text("Пожалуйста, отправьте файл или фото билета.")
                return

            user_data[user_id]["ticket_file"] = file_id
            user_data[user_id]["ticket_file_binary"] = file_binary
            context.user_data["awaiting_ticket_file"] = False
            context.user_data["awaiting_ticket_price"] = True
            await update.message.reply_text("Введите цену билета в рублях:")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {e}")
            await update.message.reply_text("Произошла ошибка при загрузке файла. Пожалуйста, попробуйте снова.")

    elif context.user_data.get("awaiting_ticket_price"):
        try:
            ticket_price = int(update.message.text)
            ticket_id = generate_ticket_id()
            ticket_name = user_data[user_id]["ticket_name"]
            file_id = user_data[user_id]["ticket_file"]
            file_binary = user_data[user_id]["ticket_file_binary"]

            ticket_file_path = save_ticket(ticket_id, ticket_name, ticket_price, file_id, file_binary)

            user_ticket = {
                "id": ticket_id,
                "name": ticket_name,
                "price": ticket_price,
                "file_id": file_id,
                "file_path": ticket_file_path
            }
            marketplace_data.append(user_ticket)

            await update.message.reply_text(
                f"Ваш билет \"{ticket_name}\" успешно выставлен на торговую площадку по цене {ticket_price} руб.!"
            )
            context.user_data["awaiting_ticket_price"] = False
            # Очищаем временные данные
            del user_data[user_id]["ticket_name"]
            del user_data[user_id]["ticket_file"]
            del user_data[user_id]["ticket_file_binary"]
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное число для цены билета.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении билета: {e}")
            await update.message.reply_text("Произошла ошибка при сохранении билета. Попробуйте снова.")

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
