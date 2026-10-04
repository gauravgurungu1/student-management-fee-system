from django.urls import path
from . import views

app_name = "fees"

urlpatterns = [
    path("", views.fee_list, name="fee_list"),
    path("create/", views.fee_create, name="fee_create"),
    path("<int:fee_id>/", views.fee_detail, name="fee_detail"),
    path("<int:fee_id>/edit/", views.fee_update, name="fee_update"),
    path("<int:fee_id>/delete/", views.fee_delete, name="fee_delete"),
]