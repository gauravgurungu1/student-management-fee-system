from django.urls import path

from . import views


app_name = "payments"


urlpatterns = [
    path("", views.payment_list, name="payment_list"),
    path("create/", views.payment_create, name="payment_create"),
    path(
        "<int:payment_id>/",
        views.payment_detail,
        name="payment_detail",
    ),
    path(
        "<int:payment_id>/edit/",
        views.payment_update,
        name="payment_update",
    ),
    path(
        "<int:payment_id>/delete/",
        views.payment_delete,
        name="payment_delete",
    ),
]