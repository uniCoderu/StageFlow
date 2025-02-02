import logging
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, menu_handler  # Импортируем функции-обработчики

# Устанавливаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = 'YOUR_API_KEY'  # Замените на ваш токен

# Главная асинхронная функция для запуска бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start
    application.add_handler(CallbackQueryHandler(menu_handler))  # Обработчик callback'ов

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

# Важно для запуска бота в Google Colab
if __name__ == "__main__":
    nest_asyncio.apply()  # Разрешаем asyncio работать в Google Colab
    try:
        asyncio.get_event_loop().run_until_complete(main())  # Запускаем основную функцию
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")
