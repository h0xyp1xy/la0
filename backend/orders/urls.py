from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("api/order/", views.submit_order, name="submit_order"),
]
