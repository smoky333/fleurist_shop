import asyncio
import threading
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from app.models import Product, CartItem, Order, OrderItem, Review

User = get_user_model()

# --- Обновлённая заглушка для run_in_loop ---

def dummy_run_in_loop(coro):
    """
    Возвращает уже завершённый Future,
    чтобы подавить предупреждения о неожиданном не await'ed coroutine.
    """
    fut = asyncio.Future()
    fut.set_result(None)
    return fut

# Путь до функции run_in_loop, используемой в ваших вьюхах (например, в app/views.py)
RUN_IN_LOOP_PATH = "app.views.run_in_loop"

# --- Тесты для HomeView ---

class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_status_code(self):
        response = self.client.get(reverse("app:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_contains_expected_text(self):
        # Предполагаем, что шаблон главной страницы содержит слово "Главная"
        response = self.client.get(reverse("app:home"))
        self.assertContains(response, "Главная")


# --- Тесты для CatalogView ---

class CatalogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = Product.objects.create(
            name="Catalog Product 1",
            price=Decimal("10.00"),
            stock=5,
            available=True
        )
        self.product2 = Product.objects.create(
            name="Catalog Product 2",
            price=Decimal("20.00"),
            stock=5,
            available=False
        )

    def test_catalog_view_status_code(self):
        response = self.client.get(reverse("app:catalog"))
        self.assertEqual(response.status_code, 200)

    def test_catalog_view_only_shows_available_products(self):
        response = self.client.get(reverse("app:catalog"))
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)


# --- Тесты для ProductDetailView ---

class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Detail Product",
            price=Decimal("15.00"),
            stock=10,
            available=True
        )

    def test_product_detail_view_status(self):
        response = self.client.get(reverse("app:product_detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)


# --- Тесты для AddToCartView ---

class AddToCartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cartuser", password="pass123")
        self.product = Product.objects.create(
            name="Cart Product",
            price=Decimal("30.00"),
            stock=5,
            available=True
        )

    def test_add_to_cart_redirects_for_anonymous(self):
        response = self.client.get(reverse("app:add_to_cart", args=[self.product.id]))
        # Неавторизованный пользователь обычно перенаправляется на страницу логина
        self.assertNotEqual(response.status_code, 200)

    def test_add_to_cart_for_authenticated_user(self):
        self.client.login(username="cartuser", password="pass123")
        response = self.client.get(reverse("app:add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CartItem.objects.filter(user=self.user, product=self.product).exists())


# --- Тесты для CartView ---

class CartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cartviewer", password="pass123")
        self.product = Product.objects.create(
            name="CartView Product",
            price=Decimal("50.00"),
            stock=10,
            available=True
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_cart_view_requires_login(self):
        response = self.client.get(reverse("app:cart"))
        self.assertNotEqual(response.status_code, 200)

    def test_cart_view_for_logged_in_user(self):
        self.client.login(username="cartviewer", password="pass123")
        response = self.client.get(reverse("app:cart"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        total = self.cart_item.subtotal()
        self.assertContains(response, str(total))


# --- Тесты для CheckoutView ---

class CheckoutViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Патчим run_in_loop, чтобы не выполнялась реальная отправка сообщения
        cls.run_in_loop_patcher = patch(RUN_IN_LOOP_PATH, new=dummy_run_in_loop)
        cls.run_in_loop_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.run_in_loop_patcher.stop()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="checkoutuser", password="pass123")
        self.product = Product.objects.create(
            name="Checkout Product",
            price=Decimal("25.00"),
            stock=10,
            available=True
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_checkout_view_get(self):
        self.client.login(username="checkoutuser", password="pass123")
        response = self.client.get(reverse("app:checkout"))
        self.assertEqual(response.status_code, 200)
        # На странице оформления заказа ожидается наличие кнопки с текстом "Оформить Заказ"
        self.assertContains(response, "Оформить Заказ")

    def test_checkout_view_post_creates_order_and_clears_cart(self):
        self.client.login(username="checkoutuser", password="pass123")
        post_data = {
            "delivery_address": "123 Main St",
            "phone_number": "111222333",
            "delivery_time": "12:00",
            "delivery_date": "2025-01-30",
        }
        response = self.client.post(reverse("app:checkout"), post_data)
        self.assertIn(response.status_code, [302, 303])
        orders = Order.objects.filter(user=self.user)
        self.assertTrue(orders.exists())
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())


# --- Тесты для LoginView ---

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="loginuser", password="pass123")

    def test_login_view_get(self):
        response = self.client.get(reverse("app:login"))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что страница входа содержит слово "Вход"
        self.assertContains(response, "Вход")

    def test_login_view_post_success(self):
        post_data = {"username": "loginuser", "password": "pass123"}
        response = self.client.post(reverse("app:login"), post_data)
        self.assertIn(response.status_code, [302, 303])
        # Проверяем, что пользователь успешно аутентифицирован
        self.assertTrue("_auth_user_id" in self.client.session)


# --- Функция для корректного закрытия клиентской сессии бота после завершения всех тестов ---
def tearDownModule():
    import asyncio
    from app.views import bot
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.session.close())
