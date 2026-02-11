#!/usr/bin/env python3
"""Run from project root: python3 setup_yookassa.py"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
ORDERS = BACKEND / "orders"
TEMPLATES = ORDERS / "templates" / "orders"

# 1. requirements.txt
req = ROOT / "requirements.txt"
if req.exists():
    t = req.read_text()
    if "yookassa" not in t:
        t = t.replace("django-ratelimit>=4.1\n", "django-ratelimit>=4.1\nyookassa>=3.0\n", 1)
        req.write_text(t)
        print("Updated requirements.txt")

# 2. backend/orders/yookassa_payment.py
yp = ORDERS / "yookassa_payment.py"
yp.write_text('''# YooKassa: set YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY in .env
import logging, os, uuid
logger = logging.getLogger(__name__)
ORDER_AMOUNT_RUB = "300000.00"

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
''')
print("Created backend/orders/yookassa_payment.py")

# 3. .env.example
env_ex = BACKEND / ".env.example"
env_content = env_ex.read_text() if env_ex.exists() else ""
if "YOOKASSA" not in env_content:
    (env_ex.write_text(env_content.rstrip() + "\n\n# YooKassa\nYOOKASSA_SHOP_ID=\nYOOKASSA_SECRET_KEY=\n"))
    print("Updated .env.example")

# 4. views.py
vp = ORDERS / "views.py"
t = vp.read_text()
if "create_payment" not in t:
    t = t.replace("from .telegram_notify import format_order_message, send_telegram_message",
        "from .telegram_notify import format_order_message, send_telegram_message\nfrom .yookassa_payment import create_payment", 1)
if "payment_success" not in t:
    t = t.replace(
        'class HomeView(TemplateView):\n    template_name = "orders/index.html"\n\n\nclass Ehawp5View',
        'class HomeView(TemplateView):\n    template_name = "orders/index.html"\n\n    def get_context_data(self, **kwargs):\n        context = super().get_context_data(**kwargs)\n        p = self.request.GET.get("payment")\n        context["payment_success"] = p == "success"\n        context["payment_failed"] = p == "failed"\n        return context\n\n\nclass Ehawp5View', 1)
if "confirmation_url" not in t:
    old = '    except Exception as e:\n        logger.warning("Order form: Telegram send failed: %s", e)\n\n    return JsonResponse({"ok": True})'
    new = '''    except Exception as e:
        logger.warning("Order form: Telegram send failed: %s", e)

    base = request.build_absolute_uri("/")
    return_url = f"{base}?payment=success"
    cancel_url = f"{base}?payment=failed"
    confirmation_url, err = create_payment(return_url, cancel_url, "Мечты воплощаемые с нуля — Лёвушкин", {"submission_uid": str(submission.uid)})
    if err:
        return JsonResponse({"ok": False, "error": err}, status=502)
    return JsonResponse({"ok": True, "confirmation_url": confirmation_url})'''
    t = t.replace(old, new, 1)
vp.write_text(t)
print("Updated views.py")

# 5. template
idx = TEMPLATES / "index.html"
t = idx.read_text()
if "payment-toast" not in t:
    t = t.replace('<main id="main" class="main">\n      <section class="product"',
        '<!-- Payment toast -->\n    <div id="payment-toast" class="order-success-toast" role="alert" aria-hidden="true"></div>\n\n    <main id="main" class="main">\n      <section class="product"', 1)
if "confirmation_url" not in t:
    t = t.replace("Promise.all([sendRequest, minWait])\n            .then(() => {",
        "Promise.all([sendRequest, minWait])\n            .then(([data]) => {\n              if (data && data.confirmation_url) { window.location.href = data.confirmation_url; return; }\n              ", 1)
if 'payment === "success"' not in t:
    t = t.replace("      })();\n    </script>\n  </body>\n</html>",
        """      })();
      (function(){
        var p = new URLSearchParams(location.search).get("payment"), toast = document.getElementById("payment-toast");
        if (!toast || !p) return;
        toast.textContent = p === "success" ? "Оплата прошла успешно. Спасибо за заказ!" : "Оплата не выполнена. Вы можете попробовать снова.";
        toast.classList.add("order-success-toast--visible"); toast.setAttribute("aria-hidden", "false");
        history.replaceState({}, "", location.pathname);
        setTimeout(function(){ toast.classList.remove("order-success-toast--visible"); toast.setAttribute("aria-hidden", "true"); }, 6000);
      })();
    </script>
  </body>
</html>""", 1)
idx.write_text(t)
print("Updated index.html")
print("\nDone. pip install yookassa; set YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY in backend/.env")
