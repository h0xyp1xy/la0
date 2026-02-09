import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from .models import ContactSubmission


@method_decorator(ensure_csrf_cookie, name="get")
class HomeView(TemplateView):
    template_name = "orders/index.html"


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
        telegram=(body.get("telegram") or "").strip(),
        region=(body.get("region") or "").strip(),
        city=(body.get("city") or "").strip(),
        address=(body.get("address") or "").strip(),
        comment=(body.get("comment") or "").strip(),
    )
    submission.save()

    return JsonResponse({"ok": True})
