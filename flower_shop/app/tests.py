from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Product, Order, Review
from .forms import OrderForm


class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(name="Тестовый продукт", price=100.0)
        self.assertEqual(product.name, "Тестовый продукт")
        self.assertEqual(product.price, 100.0)


class OrderModelTest(TestCase):
    def test_create_order(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        order = Order.objects.create(
            user=user,
            total_price=100.0,
            delivery_address="Тестовый адрес",
            delivery_date="2025-01-01"  # В модели это строка
        )
        self.assertEqual(order.total_price, 100.0)
        self.assertEqual(order.delivery_address, "Тестовый адрес")
        self.assertEqual(order.delivery_date, "2025-01-01")  # Сравниваем как строку


class ReviewModelTest(TestCase):
    def test_create_review(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        review = Review.objects.create(
            user=user,
            rating=5,
            text="Отличный продукт!"
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Отличный продукт!")
        self.assertEqual(review.user.username, "testuser")


class OrderFormTest(TestCase):
    def test_valid_order_form(self):
        data = {
            "delivery_address": "Тестовый адрес",
            "delivery_date": "2025-01-01",
            "phone_number": "1234567890"
        }
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_order_form(self):
        data = {
            "delivery_address": "",
            "delivery_date": "",
            "phone_number": ""
        }
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())


from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase


from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class ViewTests(TestCase):
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_review_view_unauthenticated(self):
        # Проверяем перенаправление для неавторизованного пользователя
        response = self.client.get(reverse('app:reviews'))
        self.assertEqual(response.status_code, 302)  # Перенаправление на страницу входа

    def test_review_view_authenticated(self):
        # Авторизуем пользователя
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse('app:reviews'))
        self.assertEqual(response.status_code, 200)  # Успешный доступ
        self.assertContains(response, "Отзывы")  # Проверяем наличие текста "Отзывы" на странице



class CatalogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("app:catalog")

    def test_catalog_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог")


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("app:home")

    def test_home_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flower Shop")

class OrderFormTest(TestCase):
    def test_valid_order_form(self):
        data = {
            "delivery_address": "Тестовый адрес",
            "delivery_date": "2025-01-01",
            "delivery_time": "12:00",  # Добавлено обязательное поле
            "phone_number": "1234567890",
            "total_price": 150.0  # Убедитесь, что это поле тоже указано, если оно требуется
        }
        form = OrderForm(data=data)
        if not form.is_valid():
            print("Ошибки формы:", form.errors)  # Для диагностики
        self.assertTrue(form.is_valid())

from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')


from .forms import OrderForm

def test_invalid_order_form(self):
    form = OrderForm(data={})
    self.assertFalse(form.is_valid())
    self.assertIn('delivery_date', form.errors)


from .models import Product

def test_product_str(self):
    product = Product.objects.create(name="Тест", price=10.0)
    self.assertEqual(str(product), "Тест")


from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    def test_review_view(self):
        response = self.client.get(reverse('app:reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/reviews.html')


from .forms import ReviewForm

class FormTests(TestCase):
    def test_valid_review_form(self):
        form_data = {'rating': 5, 'text': 'Отлично'}
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_review_form(self):
        form_data = {'rating': None, 'text': ''}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)


from .models import Product

class ModelTests(TestCase):
    def test_product_str(self):
        product = Product.objects.create(name="Тестовый продукт", price=100.0)
        self.assertEqual(str(product), "Тестовый продукт")



