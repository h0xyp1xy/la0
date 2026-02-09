"""
Test Telegram notification: sends a test message if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set.
Run: python manage.py send_telegram_test
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from orders.telegram_notify import send_telegram_message


class Command(BaseCommand):
    help = "Send a test message to Telegram (checks TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)."

    def handle(self, *args, **options):
        token = (getattr(settings, "TELEGRAM_BOT_TOKEN", None) or "").strip()
        chat_id = (getattr(settings, "TELEGRAM_CHAT_ID", None) or "").strip()
        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set. Add it to backend/.env"))
            return
        if not chat_id:
            self.stderr.write(self.style.ERROR("TELEGRAM_CHAT_ID is not set. Add it to backend/.env"))
            return
        msg = "🧪 Тест уведомлений Левушкин — если вы видите это сообщение, бот настроен."
        if send_telegram_message(msg):
            self.stdout.write(self.style.SUCCESS("Message sent. Check your Telegram."))
        else:
            self.stderr.write(
                self.style.ERROR("Send failed. Check the server console for 'Telegram:' log messages.")
            )
