import stripe
from config.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


def create_stripe_product(name):
    """Создание продукта в страйпе"""
    try:
        product = stripe.Product.create(name=name)
        return product
    except Exception as er:
        raise Exception(f"Ошибка создания продукта:{er}")


def create_stripe_price(product_id, amount):
    """Создание цены продукта в страйп"""
    try:
        price = stripe.Price.create(
            currency="rub",
            unit_amount=amount * 100,
            product=product_id,
        )
        return price
    except Exception as er:
        raise Exception(f"Ошибка создания цены:{er}")


def create_stripe_session(price_id):
    """Создание сессии в страйп"""
    try:
        session = stripe.checkout.Session.create(
            success_url="http://127.0.0.1:8000/api/payments/success",
            line_items=[{"price": "{{price_id}}", "quantity": 1}],
            mode="payment",
        )
        return session
    except Exception as er:
        raise Exception(f"Ошибка создания сессии:{er}")
