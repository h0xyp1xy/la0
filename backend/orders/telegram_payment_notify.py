"""
Send a Telegram notification when a payment succeeds (YooKassa webhook).
Uses TELEGRAM_PAYMENT_BOT_TOKEN and TELEGRAM_PAYMENT_CHAT_ID.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def send_payment_success_message(text: str) -> bool:
    token = (getattr(settings, "TELEGRAM_PAYMENT_BOT_TOKEN", None) or "").strip()
    chat_id = (getattr(settings, "TELEGRAM_PAYMENT_CHAT_ID", None) or "").strip()
    if not token:
        token = (getattr(settings, "TELEGRAM_BOT_TOKEN", None) or "").strip()
    if not chat_id:
        chat_id = (getattr(settings, "TELEGRAM_CHAT_ID", None) or "").strip()
    if not token or not chat_id:
        logger.warning("Telegram payment: no bot token or chat_id (set TELEGRAM_PAYMENT_* or TELEGRAM_*)")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": text, "disable_web_page_preview": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True
            logger.warning("Telegram payment: status %s", resp.status)
            return False
    except Exception as e:
        logger.warning("Telegram payment: %s", e)
        return False


def format_payment_success_message(payment_id: str, amount: str, currency: str, submission=None) -> str:
    lines = ["✅ Оплата прошла", "", f"💰 {amount} {currency}", f"ID платежа: {payment_id}"]
    if submission:
        lines.extend([
            "", f"👤 {submission.lastname} {submission.firstname}",
            f"📞 {submission.phone}", f"✉️ {submission.email}",
            f"📍 {submission.region}, {submission.city}", "", f"Заявка: {submission.uid}"
        ])
    return "\n".join(lines)
