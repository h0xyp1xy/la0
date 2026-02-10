import hashlib

from django.core.cache import cache
from django.http import HttpResponse


class AdminLoginRateLimitMiddleware:
    """Rate limit admin login attempts to mitigate brute force."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/admin/login/" and request.method == "POST":
            ip = self._get_client_ip(request)
            key = f"admin_login_ratelimit:{hashlib.sha256(ip.encode()).hexdigest()}"
            attempts = cache.get(key, 0)
            if attempts >= 10:
                logger = __import__("logging").getLogger(__name__)
                logger.warning("Admin login rate limit exceeded for IP %s", ip)
                return HttpResponse(
                    "<h1>Too Many Attempts</h1><p>Try again in 15 minutes.</p>",
                    status=429,
                    content_type="text/html",
                )
            cache.set(key, attempts + 1, timeout=900)  # 15 min window
        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class SecurityHeadersMiddleware:
    """Add security headers not covered by Django defaults."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = (
                "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
                "magnetometer=(), microphone=(), payment=(), usb=()"
            )
        return response


