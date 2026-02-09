"""
Send a Telegram notification when an order form is submitted.
Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment/settings.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(text: str) -> bool:
    """Send a text message to the configured Telegram chat. Returns True on success."""
    token = (getattr(settings, "TELEGRAM_BOT_TOKEN", None) or "").strip()
    chat_id = (getattr(settings, "TELEGRAM_CHAT_ID", None) or "").strip()
    if not token:
        logger.warning("Telegram: not sending — TELEGRAM_BOT_TOKEN is not set")
        return False
    if not chat_id:
        logger.warning("Telegram: not sending — TELEGRAM_CHAT_ID is not set")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": text, "disable_web_page_preview": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                logger.info("Telegram: message sent successfully")
                return True
            logger.warning("Telegram: unexpected status %s", resp.status)
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        logger.warning("Telegram: HTTP %s — %s", e.code, body)
        return False
    except (urllib.error.URLError, OSError) as e:
        logger.warning("Telegram: request failed — %s", e)
        return False


def format_order_message(submission) -> str:
    """Format a ContactSubmission as a short Telegram message."""
    lines = [
        "🆕 Новая заявка",
        "",
        f"👤 {submission.lastname} {submission.firstname}",
        f"📞 {submission.phone}",
        f"✉️ {submission.email}",
    ]
    if submission.telegram:
        lines.append(f"💬 Telegram: {submission.telegram}")
    lines.extend([
        f"📍 {submission.region}, {submission.city}",
        f"🏠 {submission.address}",
    ])
    if submission.comment:
        lines.append("")
        lines.append(f"💬 Комментарий: {submission.comment}")
    lines.append("")
    lines.append(f"ID: {submission.uid}")
    return "\n".join(lines)
