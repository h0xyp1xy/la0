# YooKassa: set YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY in .env
import logging, os, uuid
logger = logging.getLogger(__name__)
ORDER_AMOUNT_RUB = "700000.00"  # 10 RUB for testing

def create_payment(return_url, cancel_url, description, metadata=None):
    shop_id = os.environ.get("YOOKASSA_SHOP_ID", "").strip()
    secret_key = os.environ.get("YOOKASSA_SECRET_KEY", "").strip()
    if not shop_id or not secret_key:
        return None, "Оплата не настроена. Свяжитесь с нами."
    try:
        from yookassa import Configuration, Payment
    except ImportError:
        return None, "Ошибка сервера оплаты. Попробуйте позже."
    Configuration.configure(shop_id, secret_key)
    payload = {"amount": {"value": ORDER_AMOUNT_RUB, "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url, "cancel_url": cancel_url},
        "description": description, "capture": True}
    if metadata:
        payload["metadata"] = metadata
    try:
        payment = Payment.create(payload, str(uuid.uuid4()))
        url = getattr(getattr(payment, "confirmation", None) or {}, "confirmation_url", None)
        return (url, None) if url else (None, "Не удалось получить ссылку на оплату.")
    except Exception as e:
        logger.exception("YooKassa failed: %s", e)
        return None, "Ошибка создания оплаты. Попробуйте позже."
