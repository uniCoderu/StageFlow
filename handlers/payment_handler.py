# handlers/payment_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from storage.ticket_storage import marketplace_data, TICKETS_DIR
from config import logger
import os

async def pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает предварительный запрос на оплату."""
    query = update.pre_checkout_query
    payload = query.invoice_payload
    if payload.startswith("purchase_"):
        ticket_id = payload.split("_")[1]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if ticket:
            await query.answer(ok=True)
        else:
            await query.answer(ok=False, error_message="Билет не найден.")
    else:
        await query.answer(ok=False, error_message="Неверный запрос оплаты.")

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает успешный платеж."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    if payload.startswith("purchase_"):
        ticket_id = payload.split("_")[1]
        ticket = next((t for t in marketplace_data if t["id"] == ticket_id), None)
        if ticket:
            await update.message.reply_text(f"Вы успешно купили билет на \"{ticket['name']}\"!")
            ticket_file_path = os.path.join(TICKETS_DIR, ticket["id"], "ticket_file")
            if os.path.exists(ticket_file_path):
                with open(ticket_file_path, "rb") as f:
                    await update.message.reply_document(document=f, caption=f"Ваш билет: {ticket['name']}")
            marketplace_data.remove(ticket)
            logger.info(f"Билет {ticket['id']} куплен и удален из marketplace_data пользователем {update.effective_user.id}")
        else:
            await update.message.reply_text("Ошибка: билет не найден.")
