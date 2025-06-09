# bot.py
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
)
from handlers.start_handler import start
from handlers.menu_handler import menu_handler
from handlers.text_handler import text_handler
from handlers.payment_handler import pre_checkout_handler, successful_payment_handler
from handlers.marketplace_handler import marketplace_handler
from config import API_KEY, logger

async def main():
    application = ApplicationBuilder().token(API_KEY).build()

    # /start
    application.add_handler(CommandHandler("start", start))

    # команда /marketplace
    application.add_handler(CommandHandler("marketplace", marketplace_handler))

    # колбэки главного меню и настроек
    application.add_handler(
        CallbackQueryHandler(
            menu_handler,
            pattern=r"^(settings|payment_details|sbp|card|edit_payment_details|bank_|select_city|main_menu)$",
        )
    )

    # колбэки маркетплейса (главное меню, детали, покупка/продажа)
    application.add_handler(
        CallbackQueryHandler(
            marketplace_handler,
            pattern=r"^(marketplace|sell_ticket|market_details_.*|buy_ticket_.*)$",
        )
    )

    # всё остальное: ввод текста, документы/фото, платежи
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, text_handler))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    logger.info("Бот запущен и готов к работе.")
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"Ошибка запуска: {e}")
