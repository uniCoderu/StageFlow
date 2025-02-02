# handlers.py
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from utils import save_ticket, generate_ticket_id, send_invoice

# Начальная команда, когда пользователь нажимает /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Добро пожаловать в бота для покупки билетов!")

# Команда для отображения торговой площадки
async def marketplace(update: Update, context: CallbackContext):
    buttons = [
        ("Купить билет", "buy_ticket"),
        ("Мои билеты", "my_tickets"),
    ]
    keyboard = [[(text, callback_data) for text, callback_data in buttons]]
    await update.message.reply_text("Выберите действие:", reply_markup=keyboard)

# Обработчик для покупки билета
async def buy_ticket(update: Update, context: CallbackContext):
    # Логика создания билета
    ticket_id = generate_ticket_id()
    ticket_data = {
        "ticket_id": ticket_id,
        "price": 500,  # Примерная цена
        "user_id": update.message.from_user.id,
    }
    save_ticket(ticket_data)
    await send_invoice(update.message.chat.id, ticket_data)
    await update.message.reply_text(f"Ваш билет с ID {ticket_id} готов!")

# Команда для вывода "Моих билетов"
async def my_tickets(update: Update, context: CallbackContext):
    # Логика получения информации о билетах
    # (здесь будет проверка сохраненных билетов)
    await update.message.reply_text("Ваши билеты:\n- Билет ID12345")
