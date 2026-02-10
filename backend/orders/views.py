import json
import logging

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from .models import ContactSubmission
from .telegram_notify import format_order_message, send_telegram_message

logger = logging.getLogger(__name__)


def robots_txt(request):
    """Serve robots.txt with sitemap reference."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {sitemap_url}\n"
    return HttpResponse(content, content_type="text/plain")


def redirect_404_to_home(request, exception=None, path=None):
    """Redirect all 404 / unknown paths to the home page."""
    return HttpResponseRedirect("/")


@method_decorator(ensure_csrf_cookie, name="get")
class HomeView(TemplateView):
    template_name = "orders/index.html"


class Ehawp5View(TemplateView):
    template_name = "orders/ehawp5.html"


class OfferView(TemplateView):
    template_name = "orders/dogovor-oferta.html"


class PrivacyView(TemplateView):
    template_name = "orders/politika-konfidencialnosti.html"


@require_http_methods(["POST"])
def submit_order(request):
    """Accept order/contact form data and save to database."""
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

    submission = ContactSubmission(
        firstname=(body.get("firstname") or "").strip(),
        lastname=(body.get("lastname") or "").strip(),
        phone=(body.get("phone") or "").strip(),
        email=(body.get("email") or "").strip(),
        telegram="" if (body.get("telegram") or "").strip() == "@" else (body.get("telegram") or "").strip(),
        region=(body.get("region") or "").strip(),
        city=(body.get("city") or "").strip(),
        address=(body.get("address") or "").strip(),
        comment=(body.get("comment") or "").strip(),
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
