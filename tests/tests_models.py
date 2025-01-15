from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.models import Product, CartItem, Order, OrderItem, Review

User = get_user_model()


class ProductModelTest(TestCase):
    def test_is_in_stock_true(self):
        """Проверяем, что метод is_in_stock возвращает True, если stock > 0."""
        product = Product.objects.create(
            name="Rose",
            price=Decimal("10.00"),
            stock=5,
            available=True
        )
        self.assertTrue(product.is_in_stock(), "Product with stock > 0 should be in stock.")

    def test_is_in_stock_false(self):
        """Проверяем, что метод is_in_stock возвращает False, если stock == 0."""
        product = Product.objects.create(
            name="Lily",
            price=Decimal("12.50"),
            stock=0,
            available=True
        )
        self.assertFalse(product.is_in_stock(), "Product with stock == 0 should not be in stock.")

    def test_str_method(self):
        """Проверяем, что метод __str__ возвращает имя продукта."""
        product = Product.objects.create(
            name="Orchid",
            price=Decimal("20.00"),
            stock=3
        )
        self.assertEqual(str(product), "Orchid", "The __str__ method should return the product name.")


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.product = Product.objects.create(
            name="Sunflower",
            price=Decimal("5.00"),
            stock=10
        )

    def test_subtotal(self):
        """Проверяем, что метод subtotal возвращает произведение цены на количество."""
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=3,
            price=self.product.price  # Цена копируется из продукта
        )
        expected_subtotal = self.product.price * cart_item.quantity
        self.assertEqual(cart_item.subtotal(), expected_subtotal,
                         "Subtotal should equal price multiplied by quantity.")


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="testpass")
        self.product1 = Product.objects.create(
            name="Tulip",
            price=Decimal("3.50"),
            stock=20
        )
        self.product2 = Product.objects.create(
            name="Daffodil",
            price=Decimal("4.00"),
            stock=15
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal("0.00"),  # Будет пересчитана
            delivery_address="123 Test Street",
            phone_number="1234567890",
            delivery_time="12:00",
            delivery_date="2025-01-20",
            status="NEW"
        )
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1,
            price=self.product2.price
        )
        # Обновляем итоговую стоимость заказа, используя метод total_cost
        self.order.total_price = self.order.total_cost()
        self.order.save()

    def test_total_cost(self):
        """Проверяем, что метод total_cost возвращает сумму стоимости всех позиций заказа."""
        expected_total = (self.order_item1.quantity * self.order_item1.price +
                          self.order_item2.quantity * self.order_item2.price)
        self.assertEqual(self.order.total_cost(), expected_total,
                         "Total cost should be the sum of all order items.")

    def test_get_status_display(self):
        """Проверяем, что get_status_display возвращает корректное строковое представление статуса."""
        # Статус "NEW" в вашем случае должен отображаться как "Новый"
        self.assertEqual(self.order.get_status_display(), "Новый",
                         "get_status_display should return 'Новый' for status 'NEW'.")

    def test_str_method(self):
        """Проверяем, что метод __str__ возвращает ожидаемую строку для заказа."""
        expected_str = f"Заказ #{self.order.id} от {self.user.username} (Статус: {self.order.get_status_display()})"
        self.assertEqual(str(self.order), expected_str,
                         "The __str__ method of Order does not return the expected string.")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewuser", password="testpass")

    def test_str_method(self):
        """Проверяем, что метод __str__ модели Review возвращает корректное строковое представление."""
        review = Review.objects.create(
            user=self.user,
            text="Amazing product!",
            rating=5,
            comment="Really enjoyed the quality!"
        )
        expected_str = f"Review by {self.user.username} - Rating: {review.rating}"
        self.assertEqual(str(review), expected_str,
                         "The __str__ method of Review does not return the expected string.")
