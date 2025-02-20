from telegram import Update
from telegram.ext import ContextTypes
import logging

# Логгер для этого модуля
logger = logging.getLogger(__name__)

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает успешный платеж.
    :param update: Объект Update от Telegram.
    :param context: Контекст выполнения.
    """
    # Получаем информацию о платеже
    payment_info = update.message.successful_payment

    # Логируем информацию о платеже
    logger.info(f"Успешный платеж: {payment_info}")

    # Отправляем сообщение пользователю
    await update.message.reply_text(
        f"Спасибо за покупку! Ваш платеж на сумму {payment_info.total_amount / 100:.2f} {payment_info.currency} был успешно обработан."
    )

    # Здесь можно добавить логику для выдачи билета пользователю
    # Например, отправить файл с билетом или обновить статус в базе данных