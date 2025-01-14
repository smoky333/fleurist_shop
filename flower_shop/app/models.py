from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)

    def is_in_stock(self):
        return self.stock > 0

    # Другие поля, например, описание, изображение и т.д.

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity



class Order(models.Model):
    STATUS_CHOICES = (
        ('NEW', 'Новый'),
        ('PROCESSING', 'В обработке'),
        ('COMPLETED', 'Завершён'),
        ('CANCELLED', 'Отменён'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    delivery_time = models.CharField(max_length=50)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username} (Статус: {self.get_status_display()})"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, "Неизвестно")

    def total_cost(self):
        return sum(item.price * item.quantity for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)








