# main.py
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers import start, marketplace, buy_ticket, my_tickets
from config import API_KEY

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Основная функция для запуска бота
async def main():
    # Создание экземпляра приложения
    application = Application.builder().token(API_KEY).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("marketplace", marketplace))
    application.add_handler(CommandHandler("buy_ticket", buy_ticket))
    application.add_handler(CommandHandler("my_tickets", my_tickets))

    # Запуск бота
    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

# Запуск основного цикла
if __name__ == "__main__":
    asyncio.run(main())
