import os
import json
import logging
import asyncio
import threading

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.views.decorators import staff_member_required

from aiogram import Bot
from aiogram.types import FSInputFile

# Импорт форм и моделей

from .forms import RegistrationForm, OrderForm, ReviewForm
from .models import Product, CartItem, Order, OrderItem, Review

logger = logging.getLogger(__name__)

# -------------------------------------------
# 1. Получаем токен бота из settings.py
# -------------------------------------------
BOT_TOKEN = getattr(settings, "BOT_TOKEN")
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    # Если токен пустой или явно не соответствует формату,
    # вызываем исключение, чтобы не получить TokenValidationError
    raise ValueError("BOT_TOKEN is invalid or missing in settings.py!")

bot = Bot(token=BOT_TOKEN)

# Создаём глобальный event loop
loop = asyncio.new_event_loop()

def _start_loop(loop):
    """Запускаем event loop в отдельном потоке, чтобы он жил всё время работы приложения."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Запускаем поток с event loop (daemon=True, чтобы поток завершался вместе с основным процессом)
thread = threading.Thread(target=_start_loop, args=(loop,), daemon=True)
thread.start()

def run_in_loop(coro):
    """
    Запускает корутину в уже работающем (глобальном) event loop.
    Возвращает объект Future (при необходимости можно получить результат).
    """
    return asyncio.run_coroutine_threadsafe(coro, loop)

async def send_order_to_telegram_async(order):
    """Асинхронная функция для отправки информации о заказе в Telegram."""
    try:
        # Замените на нужный chat_id (например, чат администратора)
        chat_id = "5285694652"
        caption = (
            f"🎉 *Новый заказ!*\n\n"
            f"👤 *Пользователь*: {order.user.username}\n"
            f"💰 *Сумма заказа*: {order.total_price} руб.\n"
            f"📅 *Дата заказа*: {order.created_at.strftime('%d.%m.%Y %H:%M')}"
            f"📍 *Адрес*: {order.delivery_address}"
            f"📞 *Телефон*: {order.phone_number}"
            f"⏰ *Время доставки*: {order.delivery_time}"
            f"Дата доставки: {order.delivery_date}"


        )
        await bot.send_message(chat_id, caption, parse_mode="Markdown")
        logger.info("Сообщение успешно отправлено в Telegram.")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram: {e}")


def home(request):
    return render(request, 'app/home.html')


def catalog(request):
    products = Product.objects.filter(available=True)
    return render(request, 'app/catalog.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    recommended_products = Product.objects.filter(available=True).exclude(pk=pk)[:4]
    return render(request, 'app/product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
    })


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Войдите, чтобы добавить товар в корзину.")
        return redirect(f"{reverse('app:login')}?next={request.path}")

    product = get_object_or_404(Product, id=product_id, available=True)

    try:
        product_stock = int(product.stock)
    except ValueError:
        messages.error(request, f"Ошибка: количество товара '{product.name}' некорректно.")
        return redirect('app:catalog')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'price': product.price, 'quantity': 0}
    )

    if product_stock >= cart_item.quantity + 1:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Товар "{product.name}" добавлен в корзину.')
    else:
        messages.warning(request, f'Недостаточно товара "{product.name}" на складе.')

    return redirect('app:cart')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total_price = sum(item.subtotal() for item in cart_items)
    return render(request, 'shop/add_product.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

# Предполагаем, что переменная ADMIN_CHAT_ID определена, например:
ADMIN_CHAT_ID = "5285694652"

# Функция для отправки сообщения в Telegram
async def send_message_to_admin(message):
    await bot.send_message(ADMIN_CHAT_ID, message)

async def order_status_command(message: Message):
    orders = await sync_to_async(lambda: list(Order.objects.select_related('user').order_by("-created_at")))()
    if not orders:
        await message.answer("Нет заказов на данный момент.")
        return

    status_map = {
        'NEW': "🟡 Новый",
        'PROCESSING': "🔵 В обработке",
        'COMPLETED': "✅ Завершён",
        'CANCELLED': "❌ Отменён",
    }

    for order in orders:
        text = (
            f"🛒 *Заказ №{order.id}* от {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"👤 Пользователь: {order.user.username}\n"
            f"💰 Сумма: {order.total_price} ₽\n"
            f"📍 Адрес: {order.delivery_address}\n"
            f"📊 Статус: {status_map.get(order.status, 'Неизвестно')}"
        )
        await message.answer(text, parse_mode="Markdown")





@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, f'Товар “{cart_item.product.name}” удалён из корзины.')
    return redirect('app:cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('app:catalog')

    total_price = sum(item.subtotal() for item in cart_items)
    logger.debug("Начало оформления заказа. Пользователь: %s, Всего товаров: %d, Общая сумма: %s",
                 request.user.username, cart_items.count(), total_price)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            logger.debug("Форма заказа валидна.")
            try:
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = total_price
                order.save()
                logger.debug("Заказ сохранён. Заказ id: %s", order.id)
            except Exception as e:
                logger.error("Ошибка при сохранении заказа: %s", e)
                messages.error(request, "Ошибка при сохранении заказа. Попробуйте ещё раз.")
                return redirect('app:checkout')

            # Создание OrderItem для каждого товара в корзине
            for item in cart_items:
                try:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price
                    )
                    logger.debug("OrderItem создан для товара: %s (кол-во: %s)", item.product.name, item.quantity)
                except Exception as e:
                    logger.error("Ошибка при создании OrderItem для товара %s: %s", item.product.name, e)
                    messages.error(request, "Ошибка при добавлении товара в заказ.")
                    return redirect('app:checkout')

            try:
                cart_items.delete()
                logger.debug("Корзина очищена.")
            except Exception as e:
                logger.error("Ошибка при очистке корзины: %s", e)
                messages.error(request, "Ошибка при очистке корзины.")
                return redirect('app:checkout')

            # Отправляем сообщение в Telegram только после успешного сохранения заказа
            try:
                run_in_loop(send_order_to_telegram_async(order))
                logger.debug("Сообщение о новом заказе отправлено в Telegram.")
            except Exception as e:
                logger.error("Ошибка отправки заказа в Telegram: %s", e)

            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect('app:order_success')
        else:
            logger.warning("Форма заказа невалидна: %s", form.errors)
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()

    return render(request, 'app/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form
    })



@login_required
def order_success(request):
    return render(request, 'app/order_success.html')


def contacts(request):
    return render(request, 'app/contacts.html')


def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm

    if request.user.is_authenticated:
        return redirect('app:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or 'app:home'
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect('app:logout_success')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Аккаунт успешно создан для пользователя {username}!')
                return redirect('shop:home')
    else:
        form = RegistrationForm()
    return render(request, 'app/register.html', {'form': form})


def password_reset(request):
    from django.contrib.auth.forms import PasswordResetForm
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Сброс пароля на сайте Flower Shop"
                    email_template_name = "shop/password_reset_email.html"
                    c = {
                        "email": user.email,
                        "domain": request.META['HTTP_HOST'],
                        "site_name": "Flower Shop",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    send_mail(subject, email, "admin@flowershop.com", [user.email], fail_silently=False)
                messages.success(request, 'Письмо для сброса пароля отправлено на ваш email.')
                return redirect('app:password_reset_done')
            else:
                messages.error(request, 'Нет пользователя с таким email.')
    else:
        form = PasswordResetForm()
    return render(request, 'app/password_reset.html', {'form': form})


def password_reset_done(request):
    return render(request, 'app/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    from django.contrib.auth.forms import SetPasswordForm
    from django.contrib.auth import get_user_model
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш пароль был успешно изменён.')
                return redirect('app:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'app/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Ссылка для сброса пароля недействительна.')
        return redirect('app:password_reset')


def password_reset_complete(request):
    return render(request, 'app/password_reset_complete.html')


def logout_success(request):
    return render(request, 'app/logout_success.html')


def leave_review(request):
    reviews = Review.objects.all().order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Только авторизованные пользователи могут оставлять отзывы.")
            return redirect('app:reviews')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Ваш отзыв успешно добавлен.")
            return redirect('app:reviews')
    else:
        form = ReviewForm()

    return render(request, 'app/reviews.html', {'form': form, 'reviews': reviews})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/order_history.html', {'orders': orders})


@staff_member_required
def analytics_view(request):
    from django.db.models import Sum
    from django.utils.timezone import now

    today = now().date()
    orders_today = Order.objects.filter(created_at__date=today)
    total_revenue_today = orders_today.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders_today = orders_today.count()

    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.count()

    return render(request, 'app/analytics.html', {
        'orders_today': orders_today,
        'total_revenue_today': total_revenue_today,
        'total_orders_today': total_orders_today,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
    })


@csrf_exempt
def send_order_to_bot(request):
    """
    Пример ручного отправления данных по API (внешний запрос).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            bouquet_name = data.get("bouquet_name")
            price = data.get("price")
            delivery_date = data.get("delivery_date")
            image_path = data.get("image_path")

            logger.info(
                f"Отправка данных в Telegram: chat_id=5285694652, "
                f"bouquet_name={bouquet_name}, price={price}, "
                f"delivery_date={delivery_date}, image_path={image_path}"
            )

            async def _send_order():
                try:
                    if image_path:
                        photo = FSInputFile(image_path)
                        await bot.send_photo(
                            chat_id="5285694652",
                            photo=photo,
                            caption=(
                                f"🎉 *Новый заказ!*\n\n"
                                f"💐 *Букет*: {bouquet_name}\n"
                                f"💰 *Цена*: {price} руб.\n"
                                f"📅 *Дата доставки*: {delivery_date}"
                            ),
                            parse_mode="Markdown"
                        )
                    else:
                        await bot.send_message(
                            chat_id="5285694652",
                            text=(
                                f"🎉 *Новый заказ!*\n\n"
                                f"💐 *Букет*: {bouquet_name}\n"
                                f"💰 *Цена*: {price} руб.\n"
                                f"📅 *Дата доставки*: {delivery_date}"
                            ),
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения: {e}")

            run_in_loop(_send_order())
            return JsonResponse({"status": "success", "message": "Заказ отправлен в Telegram."})
        except Exception as e:
            logger.error(f"Ошибка обработки запроса: {e}")
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Только POST-запросы разрешены."})


@login_required
def repeat_order(request, order_id):
    """
    Копирует товары из выбранного заказа в корзину текущего пользователя.
    """
    # Получаем оригинальный заказ; убедитесь, что пользователь — владелец заказа
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    # Копируем каждый товар из оригинального заказа в корзину
    for item in original_order.order_items.all():
        # Если товар уже есть в корзине, увеличиваем количество,
        # иначе создаём новую запись
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=item.product,
            defaults={'price': item.price, 'quantity': 0}
        )
        if not created:
            cart_item.quantity += item.quantity
        else:
            cart_item.quantity = item.quantity
        cart_item.save()

    messages.success(request, "Товары из выбранного заказа добавлены в корзину.")
    return redirect('app:cart')


@login_required
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_status.html', {'order': order})


