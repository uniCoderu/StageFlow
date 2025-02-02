import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import API_KEY
from handlers import start, menu_handler
from utils import send_invoice

logging.basicConfig(level=logging.INFO)

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    # Прочие обработчики...

    logging.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
