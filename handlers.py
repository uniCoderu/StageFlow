from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PROVIDER_TOKEN
from utils import send_invoice, save_ticket, generate_ticket_id

# Основная команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("💳 Продать билет", callback_data="sell_ticket")],
        [InlineKeyboardButton("📜 Полит. соглашение", callback_data="policy")],
        [InlineKeyboardButton("🏷️ Торговая площадка", callback_data="marketplace")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Я бот для безопасной перепродажи билетов на мероприятия.", reply_markup=reply_markup)

# Обработчик кнопок меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "marketplace":
        if marketplace_data:
            ticket_buttons = [
                [InlineKeyboardButton(f"{ticket['name']} - {ticket['price']} руб.", callback_data=f"market_details_{i}")]
                for i, ticket in enumerate(marketplace_data)
            ]
            ticket_buttons.append([InlineKeyboardButton("Назад", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(ticket_buttons)
            await query.edit_message_text("Список доступных билетов:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("На торговой площадке пока нет билетов.", reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("Назад", callback_data="main_menu")]]))
