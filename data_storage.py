# Хранилище данных пользователей и билетов
user_data = {}
marketplace_data = []  # Глобальное хранилище для выставленных билетов

# Генерация ID билета
def generate_ticket_id():
    return f"ticket_{len(marketplace_data) + 1}"

# Сохранение информации о билете и файл
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
