from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ehawp5", views.Ehawp5View.as_view(), name="ehawp5"),
    path("api/order/", views.submit_order, name="submit_order"),
]
