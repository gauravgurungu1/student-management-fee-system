from django.contrib import admin
from django.urls import path, include

from accounts import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    # =========================
    # DJANGO ADMIN
    # =========================

    path(
        "admin/",
        admin.site.urls,
    ),


    # =========================
    # ACCOUNTS
    # =========================

    path(
        "accounts/",
        include("accounts.urls"),
    ),


    # =========================
    # STUDENTS
    # =========================

    path(
        "students/",
        include("students.urls"),
    ),


    # =========================
    # ACADEMICS
    # =========================

    path(
        "academics/",
        include("academics.urls"),
    ),


    # =========================
    # REPORTS
    # =========================

    path(
        "reports/",
        include("reports.urls"),
    ),


    # =========================
    # HOME
    # =========================

    path(
        "",
        views.home,
        name="home",
    ),

    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),


    # =========================
    # FEES
    # =========================

    path(
        "fees/",
        include("fees.urls"),
    ),


    # =========================
    # PAYMENTS
    # =========================

    path(
        "payments/",
        include("payments.urls"),
    ),


    # =========================
    # ATTENDANCE
    # =========================

    path(
        "attendance/",
        include("attendance.urls"),
    ),


    # =========================
    # NOTICES
    # =========================

    path(
        "notices/",
        include("notices.urls"),
    ),


    # =========================
    # PASSWORD CHANGE
    # =========================

    path(
        "account/password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/account/password/done/",
        ),
        name="password_change",
    ),

    path(
        "account/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
]