import os
import sys
import logging
import asyncio
import django
from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile,
)
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop.settings")
django.setup()

from .models import Order, CartItem
from django.db.models import Sum, Count

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7871114248:AAHpOr0l7R53OPjhYmvrXFa4xuUdnlsE7rQ"
ADMIN_CHAT_ID = "5285694652"

# Инициализация бота и диспетчера
from aiogram import Bot, Dispatcher

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Команда /start
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Я бот для уведомлений о заказах. Оформи заказ на сайте, а я пришлю информацию сюда.\n\n"
        "Для справки используйте /help."
    )

# Команда /help
@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/order_status — Статусы заказов (админ)\n"
        "/analytics — Аналитика заказов (админ)\n"
        "/test_order — Тестовый заказ (для проверки)"
    )

# Команда /order_status
@router.message(Command("order_status"))
async def order_status_command(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("У вас нет доступа к этому функционалу.")
        return

    orders = await sync_to_async(list)(
        Order.objects.select_related("user").order_by("-created_at")
    )
    if not orders:
        await message.answer("Нет заказов.")
        return

    status_map = {
        "NEW": "🟡 Новый",
        "PROCESSING": "🔵 В обработке",
        "COMPLETED": "✅ Завершён",
        "CANCELLED": "❌ Отменён",
    }

    for order in orders:
        text = (
            f"🛒 Заказ №{order.id}\n"
            f"👤 Пользователь: {order.user.username}\n"
            f"💰 Сумма: {order.total_price} €\n"
            f"📍 Адрес: {order.delivery_address}\n"
            f"📊 Статус: {status_map.get(order.status, 'Неизвестно')}"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Повторить заказ", callback_data=f"repeat_order:{order.id}")]
            ]
        )
        await message.answer(text, reply_markup=keyboard)

# Команда /analytics
@router.message(Command("analytics"))
async def analytics_command(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("У вас нет доступа к этому функционалу.")
        return

    today = datetime.now().date()
    total_revenue = await sync_to_async(lambda: Order.objects.aggregate(Sum("total_price"))["total_price__sum"] or 0)()
    total_orders = await sync_to_async(lambda: Order.objects.count())()
    orders_today = await sync_to_async(lambda: list(Order.objects.filter(created_at__date=today)))()

    total_revenue_today = sum(order.total_price for order in orders_today)
    total_orders_today = len(orders_today)

    response = (
        f"📊 Аналитика:\n"
        f"💰 Общий доход: {total_revenue} €\n"
        f"🛍 Всего заказов: {total_orders}\n"
        f"📅 Сегодня доход: {total_revenue_today} €\n"
        f"📦 Сегодня заказов: {total_orders_today}\n"
    )
    await message.answer(response)

# Callback для кнопки "Повторить заказ"
@router.callback_query(lambda callback: callback.data and callback.data.startswith("repeat_order:"))
async def repeat_order_callback(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split(":")[1])
        order = await sync_to_async(lambda: Order.objects.filter(id=order_id).first())()
        if not order:
            await callback.answer("Заказ не найден.", show_alert=True)
            return

        async def copy_order_to_cart():
            for item in order.order_items.all():
                cart_item, _ = CartItem.objects.get_or_create(
                    user=order.user,
                    product=item.product,
                    defaults={"price": item.price, "quantity": item.quantity},
                )
                cart_item.quantity += item.quantity
                cart_item.save()

        await sync_to_async(copy_order_to_cart)()
        await callback.answer("Товары добавлены в корзину.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)

# Команда /test_order
@router.message(Command("test_order"))
async def test_order_command(message: Message):
    bouquet_name = "Розы в корзине"
    price = 35.00
    delivery_date = "30.12.2025"
    image_path = "media/products/test_bouquet.jpg"
    await send_order(message.chat.id, bouquet_name, price, delivery_date, image_path)

# Функция отправки заказа
async def send_order(chat_id: int, bouquet_name: str, price: float, delivery_date: str, image_path: str = None):
    try:
        if image_path and os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🎉 Новый заказ:\n💐 {bouquet_name}\n💰 {price} €\n📅 {delivery_date}",
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=f"🎉 Новый заказ:\n💐 {bouquet_name}\n💰 {price} €\n📅 {delivery_date}",
            )
    except Exception as e:
        logger.error(f"Ошибка отправки заказа: {e}")

# Запуск бота
async def main():
    await bot.set_my_commands([
        BotCommand(command="/order_status", description="Статусы заказов"),
        BotCommand(command="/analytics", description="Аналитика"),
        BotCommand(command="/test_order", description="Тестовый заказ"),
    ])
    logger.info("Бот запущен. Ожидаю сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
