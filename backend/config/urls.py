from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from orders.views import redirect_404_to_home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("orders.urls")),
    path("<path:path>", redirect_404_to_home),
]

handler404 = "orders.views.redirect_404_to_home"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
