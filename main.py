import logging
import sys
import os
import nest_asyncio
import asyncio
from telegram.ext import ApplicationBuilder
from handlers import start, menu_handler, text_handler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "YOUR_TELEGRAM_BOT_API_KEY"

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
