import logging
import sys
import os
import asyncio
import nest_asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")
