import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch
from datetime import datetime

# Импортируем необходимые объекты aiogram
from aiogram.types import BotCommand

# Импортируем тестируемые функции из вашего модуля (замените путь при необходимости)
from app.views import (
    start_command,
    help_command,
    order_status_command,
    analytics_command,
    repeat_order_callback,
    send_order,
    test_order_command
)

# Константа из вашего модуля
ADMIN_CHAT_ID = "5285694652"


# Фиктивные классы для имитации объектов aiogram

class FakeChat:
    def __init__(self, id):
        self.id = id

class FakeMessage:
    def __init__(self, chat_id, text=""):
        self.chat = FakeChat(chat_id)
        self.text = text
        self.answers = []
        # Используем AsyncMock для метода answer, чтобы можно было проверять вызовы
        self.answer = AsyncMock(side_effect=self._fake_answer)

    async def _fake_answer(self, text, **kwargs):
        self.answers.append((text, kwargs))

class FakeCallbackQuery:
    def __init__(self, data, chat_id):
        self.data = data
        # CallbackQuery содержит вложенное message
        self.message = FakeMessage(chat_id)
        self.answer = AsyncMock()


# Теперь создадим тестовый класс с асинхронными тестами
class TelegramBotTests(unittest.IsolatedAsyncioTestCase):

    async def test_start_command(self):
        """Тест команды /start – проверяем, что вызывается ответ с приветствием."""
        msg = FakeMessage(chat_id=12345)
        await start_command(msg)
        msg.answer.assert_called_once()
        sent_text = msg.answers[0][0]
        self.assertTrue(sent_text.startswith("Привет! 👋"), "Сообщение должно начинаться с 'Привет! 👋'")

    async def test_help_command(self):
        """Тест команды /help – проверяем, что в ответе содержится справочная информация."""
        msg = FakeMessage(chat_id=12345)
        await help_command(msg)
        msg.answer.assert_called_once()
        sent_text = msg.answers[0][0]
        self.assertIn("Доступные команды", sent_text, "Ответ должен содержать 'Доступные команды:'")

    async def test_order_status_command_non_admin(self):
        """Тест команды /order_status для не администратора – ожидаем сообщение об отсутствии доступа."""
        msg = FakeMessage(chat_id=11111)  # не админ
        await order_status_command(msg)
        msg.answer.assert_called_once_with("У вас нет доступа к этому функционалу.")

    @patch("app.views.Order")
    async def test_order_status_command_no_orders(self, mock_order):
        """
        Тест команды /order_status для администратора, если заказов нет.
        Патчим Order.objects.select_related().order_by() так, чтобы возвращался пустой список.
        """
        # Настраиваем mock, чтобы при вызове order_by() возвращался пустой список
        mock_order.objects.select_related.return_value.order_by.return_value = []
        msg = FakeMessage(chat_id=int(ADMIN_CHAT_ID))
        await order_status_command(msg)
        # Ожидаем, что если заказов нет, будет отправлено сообщение "Нет заказов."
        msg.answer.assert_called_with("Нет заказов.")

    async def test_analytics_command_non_admin(self):
        """Проверяем, что для не администратора аналитика не доступна."""
        msg = FakeMessage(chat_id=11111)
        await analytics_command(msg)
        msg.answer.assert_called_once_with("У вас нет доступа к этому функционалу.")

    @patch("app.views.Order")
    async def test_analytics_command_admin(self, mock_order):
        """
        Тест команды /analytics для администратора.
        Патчим агрегатные вызовы и фильтрацию, чтобы вернуть тестовые значения.
        """
        msg = FakeMessage(chat_id=int(ADMIN_CHAT_ID))
        # Настраиваем возвращаемые значения для агрегатов и количества заказов
        mock_order.objects.aggregate.return_value = {"total_price__sum": 1000}
        mock_order.objects.count.return_value = 5
        # Для orders_today — вернем пустой список или список заказов с нужными total_price
        mock_order.objects.filter.return_value = []

        await analytics_command(msg)
        msg.answer.assert_called_once()
        sent_text = msg.answers[0][0]
        self.assertIn("1000", sent_text)
        self.assertIn("5", sent_text)

    async def test_repeat_order_callback_order_not_found(self):
        """Тест callback для повторения заказа, если заказ не найден."""
        callback = FakeCallbackQuery(data="repeat_order:999", chat_id=int(ADMIN_CHAT_ID))
        with patch("app.views.Order.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = None
            await repeat_order_callback(callback)
            callback.answer.assert_called_once_with("Заказ не найден.", show_alert=True)

    @patch("app.views.os.path.exists", return_value=True)
    @patch("app.views.bot.send_photo", new_callable=AsyncMock)
    async def test_send_order_with_photo(self, mock_send_photo, mock_path_exists):
        """Тест функции send_order: если указан image_path и файл существует – вызывается send_photo."""
        await send_order(
            chat_id=int(ADMIN_CHAT_ID),
            bouquet_name="Test Bouquet",
            price=123.45,
            delivery_date="01.01.2025",
            image_path="dummy/path.jpg"
        )
        mock_send_photo.assert_called_once()

    @patch("app.views.bot.send_message", new_callable=AsyncMock)
    async def test_send_order_without_photo(self, mock_send_message):
        """Тест функции send_order: если image_path не указан – вызывается send_message."""
        await send_order(
            chat_id=int(ADMIN_CHAT_ID),
            bouquet_name="Test Bouquet",
            price=123.45,
            delivery_date="01.01.2025",
            image_path=None
        )
        mock_send_message.assert_called_once()

    async def test_test_order_command(self):
        """
        Тест команды /test_order:
        Патчим функцию send_order, чтобы удостовериться, что вызывается с нужными параметрами.
        """
        msg = FakeMessage(chat_id=int(ADMIN_CHAT_ID))
        with patch("app.views.send_order", new_callable=AsyncMock) as mock_send_order:
            await test_order_command(msg)
            mock_send_order.assert_called_once_with(
                msg.chat.id,
                "Розы в корзине",
                35.0,
                "30.12.2025",
                "media/products/test_bouquet.jpg"
            )


if __name__ == "__main__":
    unittest.main()
