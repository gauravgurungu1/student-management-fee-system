from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.attendance_list,
        name="attendance_list",
    ),

    path(
        "create/",
        views.attendance_create,
        name="attendance_create",
    ),

    path(
        "<int:session_id>/mark/",
        views.attendance_mark,
        name="attendance_mark",
    ),

    path(
        "<int:session_id>/delete/",
        views.attendance_delete,
        name="attendance_delete",
    ),

    path(
        "scheduled/<int:schedule_id>/", 
        views.scheduled_attendance_create,
        name="scheduled_attendance_create",
    ),

    path(
        "<int:session_id>/delete/",
        views.attendance_delete,
        name="attendance_delete",
    ),
]