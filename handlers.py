from telegram import Update
from telegram.ext import ContextTypes
from utils import generate_ticket_id, save_ticket, send_invoice

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply("Привет! Я бот для продажи билетов.\nИспользуй команды:\n/marketplace — Торговая площадка\n/buy_ticket — Купить билет\n/my_tickets — Мои билеты\n/settings — Настройки")

# Обработчик команды /marketplace (торговая площадка)
async def marketplace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply("Это торговая площадка. Вы можете купить или продать билеты.")

# Обработчик команды /buy_ticket (покупка билета)
async def buy_ticket_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ticket_id = generate_ticket_id()  # Генерация уникального билета
    save_ticket(ticket_id, update.message.from_user.id, "Концерт A")  # Сохранение билета
    await update.message.reply(f"Ваш билет на 'Концерт A' был успешно куплен! ID билета: {ticket_id}. Для оплаты, свяжитесь с администрацией.")

# Обработчик команды /my_tickets (мои билеты)
async def my_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Здесь может быть логика, чтобы показать список всех билетов пользователя.
    # Пока что просто отправляем тестовое сообщение.
    await update.message.reply("Вот ваши билеты: 1. Концерт A, 2. Концерт B.")

# Обработчик команды /settings (настройки)
async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply("В этих настройках вы можете изменить уведомления или изменить способ оплаты.")
