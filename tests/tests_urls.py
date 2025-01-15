from django.test import SimpleTestCase
from django.urls import reverse, resolve
from app import views

class URLTests(SimpleTestCase):

    def test_home_url(self):
        url = reverse("app:home")
        self.assertEqual(resolve(url).func, views.home)

    def test_catalog_url(self):
        url = reverse("app:catalog")
        self.assertEqual(resolve(url).func, views.catalog)

    def test_product_detail_url(self):
        url = reverse("app:product_detail", args=[1])
        self.assertEqual(resolve(url).func, views.product_detail)

    def test_cart_view_url(self):
        url = reverse("app:cart")
        self.assertEqual(resolve(url).func, views.cart_view)

    def test_add_to_cart_url(self):
        url = reverse("app:add_to_cart", args=[1])
        self.assertEqual(resolve(url).func, views.add_to_cart)

    def test_remove_from_cart_url(self):
        url = reverse("app:remove_from_cart", args=[1])
        self.assertEqual(resolve(url).func, views.remove_from_cart)

    def test_checkout_url(self):
        url = reverse("app:checkout")
        self.assertEqual(resolve(url).func, views.checkout)

    def test_order_success_url(self):
        url = reverse("app:order_success")
        self.assertEqual(resolve(url).func, views.order_success)

    def test_order_status_url(self):
        url = reverse("app:order_status", args=[1])
        self.assertEqual(resolve(url).func, views.order_status)

    def test_repeat_order_url(self):
        url = reverse("app:repeat_order", args=[1])
        self.assertEqual(resolve(url).func, views.repeat_order)

    def test_order_history_url(self):
        url = reverse("app:order_history")
        self.assertEqual(resolve(url).func, views.order_history)

    def test_analytics_url(self):
        url = reverse("app:analytics")
        self.assertEqual(resolve(url).func, views.analytics_view)

    def test_contacts_url(self):
        url = reverse("app:contacts")
        self.assertEqual(resolve(url).func, views.contacts)

    def test_login_url(self):
        url = reverse("app:login")
        self.assertEqual(resolve(url).func, views.login_view)

    def test_logout_url(self):
        url = reverse("app:logout")
        self.assertEqual(resolve(url).func, views.logout_view)

    def test_logout_success_url(self):
        url = reverse("app:logout_success")
        self.assertEqual(resolve(url).func, views.logout_success)

    def test_register_url(self):
        url = reverse("app:register")
        self.assertEqual(resolve(url).func, views.register)

    def test_password_reset_url(self):
        url = reverse("app:password_reset")
        self.assertEqual(resolve(url).func, views.password_reset)

    def test_password_reset_done_url(self):
        url = reverse("app:password_reset_done")
        self.assertEqual(resolve(url).func, views.password_reset_done)

    def test_password_reset_confirm_url(self):
        # Здесь передаём примеры аргументов: uidb64 и token.
        url = reverse("app:password_reset_confirm", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func, views.password_reset_confirm)

    def test_password_reset_complete_url(self):
        url = reverse("app:password_reset_complete")
        self.assertEqual(resolve(url).func, views.password_reset_complete)

    def test_reviews_url(self):
        url = reverse("app:reviews")
        self.assertEqual(resolve(url).func, views.leave_review)

    def test_send_order_to_bot_url(self):
        url = reverse("app:send_order_to_bot")
        self.assertEqual(resolve(url).func, views.send_order_to_bot)
