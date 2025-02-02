import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler
from handlers import start, marketplace_handler, buy_ticket_handler, my_tickets_handler, settings_handler

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
API_KEY = '8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU'

async def main() -> None:
    # Создание объекта приложения
    application = Application.builder().token(API_KEY).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("marketplace", marketplace_handler))
    application.add_handler(CommandHandler("buy_ticket", buy_ticket_handler))
    application.add_handler(CommandHandler("my_tickets", my_tickets_handler))
    application.add_handler(CommandHandler("settings", settings_handler))

    # Запуск бота
    await application.run_polling()

# Запуск асинхронной функции с использованием стандартного цикла событий
if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
        loop.run_until_complete(main())  # Запускаем основную асинхронную функцию
    except RuntimeError as e:
        if str(e) == 'This event loop is already running':
            loop = asyncio.get_event_loop()
            loop.create_task(main())  # Для среды с уже работающим циклом событий
            loop.run_forever()  # Переходим к бесконечному ожиданию задач
