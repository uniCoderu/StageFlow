import random
import string

# Генерация уникального ID билета
def generate_ticket_id() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Сохранение информации о билете (простой пример)
def save_ticket(ticket_id: str, user_id: str, event: str) -> None:
    # Тут логика сохранения в базу данных, например, в файл или базу данных.
    print(f"Сохранение билета: {ticket_id} для пользователя {user_id} на событие {event}")

# Отправка счета на оплату (например, с использованием API)
def send_invoice(user_id: str, ticket_id: str) -> None:
    # Тут логика отправки счета на оплату
    print(f"Отправка счета на оплату для билета {ticket_id} пользователю {user_id}")
