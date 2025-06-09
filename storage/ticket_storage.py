# storage/ticket_storage.py
import json
import uuid
from pathlib import Path

# файл, где хранятся билеты
TICKETS_FILE = Path(__file__).parent / "tickets.json"

def load_marketplace_data() -> list[dict]:
    """Считывает все билеты из JSON (или возвращает пустой список)."""
    if TICKETS_FILE.exists():
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_marketplace_data(data: list[dict]) -> None:
    """Сохраняет список билетов в JSON."""
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_ticket(name: str, price: int, seller_id: int) -> dict:
    """Добавляет новый билет и возвращает его."""
    tickets = load_marketplace_data()
    ticket = {
        "id": str(uuid.uuid4()),
        "name": name,
        "price": price,
        "seller_id": seller_id
    }
    tickets.append(ticket)
    save_marketplace_data(tickets)
    return ticket
