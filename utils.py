from telegram import LabeledPrice

async def send_invoice(update, context, ticket):
    """
    Отправляет инвойс пользователю для оплаты.
    """
    prices = [LabeledPrice(label=ticket['name'], amount=ticket['price'] * 100)]  # цена в копейках
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=ticket['name'],
        description=f"Оплата за билет: {ticket['name']}",
        payload=f"ticket_{ticket['id']}",
        provider_token="1744374395:TEST:236438f0df3db3a23dd9",  # Ваш токен
        currency="RUB",
        prices=prices,
        start_parameter="buy-ticket"
    )
