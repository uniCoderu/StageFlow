# utils.py
import json
import os

# Функция для сохранения данных о билете
def save_ticket(ticket_data):
    with open("tickets.json", "a") as file:
        json.dump(ticket_data, file)
        file.write("\n")  # Для разделения записей

# Функция для генерации ID билета
def generate_ticket_id():
    return str(os.urandom(8).hex())

# Функция для отправки счета пользователю
import httpx

async def send_invoice(chat_id, ticket_data):
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{API_KEY}/sendInvoice"
        payload = {
            "chat_id": chat_id,
            "title": "Билет на мероприятие",
            "description": "Описание мероприятия",
            "payload": ticket_data["ticket_id"],
            "provider_token": "YOUR_PROVIDER_TOKEN",  # Подставьте свой токен
            "currency": "RUB",
            "prices": [{"label": "Билет", "amount": ticket_data["price"]}],
        }
        await client.post(url, json=payload)
