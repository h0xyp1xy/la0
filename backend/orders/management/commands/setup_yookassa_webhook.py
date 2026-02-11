"""
Register YooKassa webhook and test payment Telegram. Run: python manage.py setup_yookassa_webhook --url https://levushkin.art
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Test payment Telegram and show webhook URL for YooKassa."
    def add_arguments(self, parser):
        parser.add_argument("--url", type=str, default=os.environ.get("YOOKASSA_WEBHOOK_BASE_URL", "").strip())
        parser.add_argument("--test-only", action="store_true")
    def handle(self, *args, **options):
        base_url = (options["url"] or "").strip().rstrip("/")
        test_only = options["test_only"]
        from orders.telegram_payment_notify import send_payment_success_message
        token = (getattr(settings, "TELEGRAM_PAYMENT_BOT_TOKEN", None) or "").strip()
        chat_id = (getattr(settings, "TELEGRAM_PAYMENT_CHAT_ID", None) or "").strip()
        if not token: token = (getattr(settings, "TELEGRAM_BOT_TOKEN", None) or "").strip()
        if not chat_id: chat_id = (getattr(settings, "TELEGRAM_CHAT_ID", None) or "").strip()
        if not token or not chat_id:
            self.stderr.write(self.style.ERROR("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in backend/.env"))
        else:
            if send_payment_success_message("🧪 Тест уведомления об оплате — бот настроен."):
                self.stdout.write(self.style.SUCCESS("Payment Telegram test: message sent."))
            else:
                self.stderr.write(self.style.ERROR("Payment Telegram test: send failed."))
        if test_only: return
        if not base_url:
            self.stderr.write(self.style.ERROR("Provide --url https://levushkin.art"))
            return
        self.stdout.write(self.style.WARNING("In YooKassa set URL: %s  event: payment.succeeded" % (base_url + "/api/yookassa-webhook/",)))
