from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from orders.sitemaps import StaticViewSitemap
from orders.views import robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"static": StaticViewSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("orders.urls")),
]

handler404 = "orders.views.page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
