from django.urls import path

from . import views


app_name = "notices"


urlpatterns = [
    path(
        "",
        views.notice_list,
        name="notice_list",
    ),

    path(
        "create/",
        views.notice_create,
        name="notice_create",
    ),

    path(
        "<int:notice_id>/",
        views.notice_detail,
        name="notice_detail",
    ),

    path(
        "<int:notice_id>/edit/",
        views.notice_update,
        name="notice_update",
    ),

    path(
        "<int:notice_id>/delete/",
        views.notice_delete,
        name="notice_delete",
    ),

    path(
        "notifications/read/",
        views.mark_notifications_read,
        name="mark_notifications_read",
    ),
]