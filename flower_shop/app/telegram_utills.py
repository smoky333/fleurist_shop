import os
import asyncio
import threading
import logging
from aiogram import Bot

logger = logging.getLogger(__name__)

# Настройка токена и chat_id
BOT_TOKEN = os.getenv("BOT_TOKEN", "ваш токен")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "5285694652")

bot = Bot(token=BOT_TOKEN)

# Глобальный цикл событий
loop = asyncio.new_event_loop()

def start_loop(loop):
    """Запуск event loop в отдельном потоке."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

thread = threading.Thread(target=start_loop, args=(loop,), daemon=True)
thread.start()

def run_in_loop(coro):
    """Запуск корутины в фоновом event loop."""
    return asyncio.run_coroutine_threadsafe(coro, loop)

async def send_order_to_telegram_async(order):
    """Отправка нового заказа в Telegram."""
    caption = (
        f"🎉 *Новый заказ!*\n\n"
        f"👤 *Пользователь*: {order.user.username}\n"
        f"💰 *Сумма заказа*: {order.total_price} €\n"
        f"📅 *Дата заказа*: {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )
    try:
        await bot.send_message(ADMIN_CHAT_ID, caption, parse_mode="Markdown")
        logger.info("Уведомление о заказе отправлено.")
    except Exception as e:
        logger.error(f"Ошибка отправки заказа в Telegram: {e}")

async def send_status_change_to_telegram_async(order):
    """Уведомление об изменении статуса заказа."""
    caption = (
        f"📢 *Изменение статуса заказа!*\n\n"
        f"🛒 Заказ №{order.id}\n"
        f"👤 Пользователь: {order.user.username}\n"
        f"💰 Сумма: {order.total_price} €\n"
        f"➡️ Новый статус: {order.status}"
    )
    try:
        await bot.send_message(ADMIN_CHAT_ID, caption, parse_mode="Markdown")
        logger.info("Статус заказа отправлен.")
    except Exception as e:
        logger.error(f"Ошибка отправки статуса заказа: {e}")
