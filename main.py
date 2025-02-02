import logging
import nest_asyncio  # Подключаем nest_asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, marketplace_handler, buy_ticket_handler, my_tickets_handler
from config import API_TOKEN

# Для работы с event loop в Colab
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Создаем приложение
    application = Application.builder().token(API_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("marketplace", marketplace_handler))
    application.add_handler(CommandHandler("buy_ticket", buy_ticket_handler))
    application.add_handler(CommandHandler("my_tickets", my_tickets_handler))

    # Запускаем бота
    await application.run_polling()

if __name__ == "__main__":
    logging.info("Бот запущен и готов к работе.")
    # Запускаем main() с учетом event loop в Google Colab
    asyncio.run(main())
