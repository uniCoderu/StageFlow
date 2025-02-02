import os

TICKETS_DIR = "tickets"
if not os.path.exists(TICKETS_DIR):
    os.makedirs(TICKETS_DIR)

# Генерация ID билета
def generate_ticket_id():
    return f"ticket_{len(os.listdir(TICKETS_DIR)) + 1}"

# Сохранение информации о билете и файла
def save_ticket(ticket_id, name, price, file_id, file_binary):
    ticket_folder = os.path.join(TICKETS_DIR, ticket_id)
    if not os.path.exists(ticket_folder):
        os.makedirs(ticket_folder)

    # Сохраняем информацию о билете
    info_path = os.path.join(ticket_folder, "info.txt")
    with open(info_path, "w") as f:
        f.write(f"Название: {name}\n")
        f.write(f"Цена: {price}\n")
        f.write(f"ID файла: {file_id}\n")

    # Сохраняем файл билета
    file_path = os.path.join(ticket_folder, "ticket_file")
    with open(file_path, "wb") as f:
        f.write(file_binary)
    return file_path

# Отправка инвойса пользователю
async def send_invoice(update, context, ticket):
    from telegram import LabeledPrice
    
    prices = [LabeledPrice(label=ticket['name'], amount=ticket['price'] * 100)]  # цена в копейках
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=ticket['name'],
        description=f"Оплата за билет: {ticket['name']}",
        payload=f"ticket_{ticket['id']}",
        provider_token="1744374395:TEST:236438f0df3db3a23dd9",  # тестовый токен
        currency="RUB",
        prices=prices,
        start_parameter="buy-ticket"
    )
