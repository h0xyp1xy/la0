import json
import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit

from .models import ContactSubmission
from .telegram_notify import format_order_message, send_telegram_message

logger = logging.getLogger(__name__)


def robots_txt(request):
    """Serve robots.txt with sitemap reference."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {sitemap_url}\n"
    return HttpResponse(content, content_type="text/plain")


def page_not_found(request, exception=None):
    """Return 404 for unknown paths (no redirect — clearer for security scanners)."""
    from django.http import HttpResponseNotFound
    return HttpResponseNotFound("<h1>404 Not Found</h1>")


@method_decorator(ensure_csrf_cookie, name="get")
class HomeView(TemplateView):
    template_name = "orders/index.html"


class Ehawp5View(TemplateView):
    template_name = "orders/ehawp5.html"


class OfferView(TemplateView):
    template_name = "orders/dogovor-oferta.html"


class PrivacyView(TemplateView):
    template_name = "orders/politika-konfidencialnosti.html"


# Max length for text fields (must match or be stricter than model)
_MAX_FIRSTNAME = 100
_MAX_LASTNAME = 100
_MAX_PHONE = 20
_MAX_EMAIL = 254
_MAX_TELEGRAM = 100
_MAX_REGION = 200
_MAX_CITY = 100
_MAX_ADDRESS = 300
_MAX_COMMENT = 2000


@ratelimit(key="header:x-real-ip", rate="5/m", method="POST", block=False)
@require_http_methods(["POST"])
def submit_order(request):
    """Accept order/contact form data and save to database."""
    if getattr(request, "limited", False):
        return JsonResponse(
            {"ok": False, "error": "Слишком много запросов. Попробуйте позже."},
            status=429,
        )
    try:
        body = json.loads(request.body) if request.content_type == "application/json" else request.POST.dict()
    except (json.JSONDecodeError, ValueError):
        body = request.POST.dict()

    required = ["firstname", "lastname", "phone", "email", "region", "city", "address"]
    missing = [f for f in required if not (body.get(f) or "").strip()]
    if missing:
        return JsonResponse(
            {"ok": False, "error": f"Обязательные поля: {', '.join(missing)}"},
            status=400,
        )

    # Enforce max lengths to prevent overflow/abuse
    limits = {
        "firstname": _MAX_FIRSTNAME,
        "lastname": _MAX_LASTNAME,
        "phone": _MAX_PHONE,
        "email": _MAX_EMAIL,
        "telegram": _MAX_TELEGRAM,
        "region": _MAX_REGION,
        "city": _MAX_CITY,
        "address": _MAX_ADDRESS,
        "comment": _MAX_COMMENT,
    }
    vals = {}
    for k, lim in limits.items():
        raw = (body.get(k) or "").strip()
        if k == "telegram" and raw == "@":
            raw = ""
        if len(raw) > lim:
            return JsonResponse(
                {"ok": False, "error": f"Поле «{k}» слишком длинное (макс. {lim} символов)."},
                status=400,
            )
        vals[k] = raw[:lim] if raw else raw

    try:
        validate_email(vals["email"])
    except ValidationError:
        return JsonResponse({"ok": False, "error": "Некорректный email."}, status=400)

    submission = ContactSubmission(
        firstname=vals["firstname"],
        lastname=vals["lastname"],
        phone=vals["phone"],
        email=vals["email"],
        telegram=vals["telegram"],
        region=vals["region"],
        city=vals["city"],
        address=vals["address"],
        comment=vals["comment"],
    )
    try:
        submission.save()
    except Exception as e:
        logger.exception("Order form: failed to save submission")
        return JsonResponse(
            {"ok": False, "error": "Ошибка сохранения. Проверьте права на сервере (файл базы данных)."},
            status=500,
        )

    try:
        send_telegram_message(format_order_message(submission))
    except Exception as e:
        logger.warning("Order form: Telegram send failed: %s", e)

    return JsonResponse({"ok": True})
