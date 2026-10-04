from django.urls import path

from . import views


urlpatterns = [
    # Administrator
    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # Teacher authentication
    path(
        "teacher/login/",
        views.teacher_login,
        name="teacher_login",
    ),

    path(
        "teacher/set-password/",
        views.teacher_set_password,
        name="teacher_set_password",
    ),

    path(
        "teacher/password-login/",
        views.teacher_password_login,
        name="teacher_password_login",
    ),

    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),

    # Teacher management
    path(
        "teachers/",
        views.teacher_list,
        name="teacher_list",
    ),

    path(
        "teachers/add/",
        views.teacher_create,
        name="teacher_create",
    ),
]