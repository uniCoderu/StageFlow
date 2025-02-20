import sys
sys.path.insert(0, '/content/drive/My Drive/StageFlow')

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.start_handler import start
from handlers.menu_handler import menu_handler
from handlers.text_handler import text_handler
from handlers.payment_handler import successful_payment_handler
from config import API_KEY, logger

# Запуск бота
async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    try:
        import asyncio
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")