
# StageFlow

StageFlow — это сервис для перепродажи билетов на мероприятия с использованием бота. Бот помогает пользователям покупать и продавать билеты, а также управлять своими покупками.

## Структура проекта

```
StageFlow/
├── bot.py
├── config.py
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py
│   ├── menu_handler.py
│   ├── text_handler.py
│   ├── payment_handler.py
│   ├── marketplace_handler.py
└── storage/
    ├── __init__.py
    ├── user_data.py
    ├── ticket_storage.py
```

## Как работает код?

### `main.py`

Этот файл является основной точкой входа в приложение. Он создаёт объект приложения и регистрирует все обработчики команд:

- `/start` — Приветствие и информация о доступных командах.
- `/marketplace` — Описание торговой площадки, где пользователи могут размещать и искать билеты.
- `/buy_ticket` — Покупка билета, генерация уникального ID билета и его сохранение.
- `/my_tickets` — Отображение списка купленных билетов (в настоящее время заглушка).
- `/settings` — Настройки пользователя.

### `handlers.py`

Файл содержит обработчики для каждой команды, которые выполняются при взаимодействии пользователя с ботом:

- `/start`: Команда для старта работы с ботом. Выводит приветственное сообщение и объяснение доступных команд.
- `/marketplace`: Команда для отображения торговой площадки.
- `/buy_ticket`: Команда для покупки билета, генерации его ID и сохранения.
- `/my_tickets`: Команда для отображения списка купленных билетов (пока реализована как заглушка).
- `/settings`: Команда для настроек пользователя.

### `utils.py`

Утилиты, помогающие в генерации уникальных идентификаторов для билетов, их сохранении и отправке счетов.

## Установка и запуск

1. Клонируйте репозиторий на свой локальный компьютер:
   ```bash
   git clone https://github.com/yourusername/StageFlow.git
   ```

2. Установите все необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите бота:
   ```bash
   python main.py
   ```

4. Откройте бота в Telegram и начните взаимодействовать с ним!

## Конtributing

Если вы хотите внести свой вклад в проект, создайте Pull Request с улучшениями или исправлениями. Все идеи и предложения приветствуются!

## Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для подробностей.
