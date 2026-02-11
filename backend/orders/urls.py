from django.http import HttpResponseRedirect
from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ehawp5", views.Ehawp5View.as_view(), name="ehawp5"),
    path("dogovor-oferta/", views.OfferView.as_view(), name="offer"),
    path("politika-konfidencialnosti/", views.PrivacyView.as_view(), name="privacy"),
    path("api/order/", views.submit_order, name="submit_order"),
    path("api/yookassa-webhook/", views.yookassa_webhook, name="yookassa_webhook"),
    path("<path:path>", lambda request, path: HttpResponseRedirect("/")),
]
