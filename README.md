# 🌸 Fleurist Shop

**Fleurist Shop** is a Django-based e-commerce platform for selling flowers. It features a user-friendly catalog, shopping cart, order management system, and a Telegram bot for order notifications.

## 🚀 Features

### 🌐 Web Application
- **Product Catalog** – Browse available flowers with detailed descriptions and pricing.
- **Shopping Cart** – Add and manage items before checkout.
- **Order Management** – Secure order processing with user authentication.
- **User Accounts** – Registration, login, and profile management.
- **Reviews & Ratings** – Customers can leave feedback on products.
- **Password Reset** – Secure password recovery via email.

### 🤖 Telegram Bot
- **Order Notifications** – Sends new order alerts to admins.
- **Order Status Updates** – Customers can check order status.
- **Admin Commands** – `/order_status`, `/analytics`, etc.

## 🛠 Tech Stack
- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL / SQLite
- **Frontend**: Bootstrap + Django Templates
- **Bot**: aiogram 3.x (Python)
- **Caching**: Redis (optional for performance optimization)

## 🏗 Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/smoky333/fleurist_shop.git
cd fleurist_shop
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations & Create Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5️⃣ Run Development Server
```bash
python manage.py runserver
```

### 6️⃣ Start Telegram Bot (if configured)
```bash
python bot.py
```

## 🔥 Deployment
### Using Docker
```bash
docker-compose up --build -d
```

## 📌 TODO
- [ ] Integrate Payment Gateway (Stripe/PayPal)
- [ ] Improve UI with React/Vue (optional)
- [ ] Add Celery for background tasks
- [ ] Enhance Order Analytics for Admins

## 📫 Contact & Contributions
Contributions are welcome! Feel free to fork this repository and submit pull requests.

📩 **Contact**: [@YourTelegramUsername](#) | [yourwebsite.com](#)

---
💐 *Fleurist Shop – Bringing fresh flowers to your doorstep!*

