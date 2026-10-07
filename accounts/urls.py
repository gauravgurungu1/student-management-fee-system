from django.urls import path

from . import views


urlpatterns = [

    # =========================
    # ADMINISTRATOR
    # =========================

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


    # =========================
    # TEACHER AUTHENTICATION
    # =========================

    path(
        "teacher/login/",
        views.teacher_login,
        name="teacher_login",
    ),

    path(
        "teacher/check-phone/",
        views.check_teacher_phone,
        name="check_teacher_phone",
    ),

    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),


    # =========================
    # TEACHER SUBJECTS
    # =========================

    path(
        "teacher/subjects/",
        views.teacher_subjects,
        name="teacher_subjects",
    ),


    # =========================
    # TEACHER MANAGEMENT
    # =========================

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


    # =========================
    # TEACHER ASSIGNMENTS
    # =========================

    path(
        "assignments/",
        views.teacher_assignment_list,
        name="teacher_assignment_list",
    ),

    path(
        "assignments/add/",
        views.teacher_assignment_create,
        name="teacher_assignment_create",
    ),

    path(
        "assignments/<int:assignment_id>/delete/",
        views.teacher_assignment_delete,
        name="teacher_assignment_delete",
    ),


    # =========================
    # TEACHER CLASSES
    # =========================

    path(
        "teacher/classes/",
        views.teacher_classes,
        name="teacher_classes",
    ),
]