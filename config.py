import os

# Ваш Telegram API ключ
API_KEY = "8018543300:AAFgcrM7-n7d1kkiO35M96PHp-UCHtVagrU"

# Директория для хранения данных билетов
TICKETS_DIR = "tickets"
if not os.path.exists(TICKETS_DIR):
    os.makedirs(TICKETS_DIR)

# Токен для платежной системы
PROVIDER_TOKEN = "1744374395:TEST:236438f0df3db3a23dd9"
