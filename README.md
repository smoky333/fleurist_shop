# Flower Shop

**Flower Shop** is a Django-based e-commerce application designed for selling flowers. It features an interactive product catalog, shopping cart, order management, user authentication, and Telegram bot integration to send order notifications. This project is fully covered by automated tests and includes instructions for measuring code coverage.

## Features

- **Product Catalog:** Browse available products with detailed views.
- **Shopping Cart:** Add products to a cart, adjust quantities, and view the total cost.
- **Order Processing:** Checkout to create orders with delivery details.
- **User Management:** Registration, login, and logout functionalities.
- **Reviews:** Customers can leave reviews and ratings for products.
- **Order History & Analytics:** View past orders and see sales analytics for admin users.
- **Telegram Bot Integration:** The bot sends notifications for new orders and provides administrative commands (e.g., `/order_status`, `/analytics`).
- **Password Reset:** Secure password reset via email.

## Technologies Used

- **Backend:** Django, aiogram (for Telegram bot)
- **Frontend:** HTML, CSS (Bootstrap 5)
- **Asynchronous Tasks:** Python’s `asyncio`
- **Testing:** Django TestCase, unittest, and coverage
- **Bot Integration:** aiogram

