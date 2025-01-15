from django.test import TestCase
from django import forms
from datetime import date

from app.forms import RegistrationForm, OrderForm, ReviewForm
from django.contrib.auth.models import User
from app.models import Order, Review

class RegistrationFormTests(TestCase):
    def test_registration_form_valid(self):
        """Проверяем, что форма регистрации валидна, если пароли совпадают."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid(), f"Ошибки формы: {form.errors}")
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        # Проверяем, что пароль корректно установлен (то есть преобразован через set_password)
        self.assertTrue(user.check_password('complex_password123'))

    def test_registration_form_passwords_not_matching(self):
        """Проверяем, что форма регистрации не валидна, если пароли не совпадают."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complex_password123',
            'password2': 'different_password',
        }
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        # Проверяем, что сообщение об ошибке связано с несовпадением паролей
        self.assertIn("Пароли не совпадают!", form.errors.as_text())


class OrderFormTests(TestCase):
    def test_order_form_valid_data(self):
        """
        Проверяем, что форма заказа валидна при корректных данных.
        Передаём данные в ожидаемом формате ('YYYY-MM-DD') для даты.
        """
        data = {
            'delivery_address': 'Тестовый адрес',
            'phone_number': '1234567890',
            'delivery_time': '12:00',
            'delivery_date': '2025-01-01',
        }
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid(), f"Ошибки формы: {form.errors}")
        # Сохраним объект без commit=True, чтобы проверить его поля
        order = form.save(commit=False)
        self.assertEqual(order.delivery_address, 'Тестовый адрес')
        # При сохранении формы поле delivery_date преобразуется в объект date
        self.assertEqual(order.delivery_date, date(2025, 1, 1))

    def test_order_form_invalid_date_format(self):
        """
        Проверяем, что форма заказа не валидна, если дата имеет неверный формат.
        Допустимый формат – 'YYYY-MM-DD', а мы передадим 'DD-MM-YYYY'.
        """
        data = {
            'delivery_address': 'Тестовый адрес',
            'phone_number': '1234567890',
            'delivery_time': '12:00',
            'delivery_date': '01-01-2025',  # неверный формат
        }
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)


class ReviewFormTests(TestCase):
    def test_review_form_valid(self):
        """Проверяем, что форма отзыва валидна при корректных данных."""
        data = {
            'text': 'Отличный продукт!',
            'rating': 5,
        }
        form = ReviewForm(data=data)
        self.assertTrue(form.is_valid(), f"Ошибки формы: {form.errors}")

    def test_review_form_missing_fields(self):
        """Проверяем, что форма отзыва не валидна, если обязательные поля не заполнены."""
        data = {
            'text': '',  # пустой отзыв
            'rating': '',  # не выбрана оценка
        }
        form = ReviewForm(data=data)
        self.assertFalse(form.is_valid())
        # Можно проверить, что ошибок несколько и они связаны с обоими полями
        self.assertIn('text', form.errors)
        self.assertIn('rating', form.errors)
