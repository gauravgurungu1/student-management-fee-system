from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from academics.models import Course
from students.models import Student

from .decorators import admin_required, teacher_required
from .models import Teacher


# =========================
# ADMINISTRATOR
# =========================

def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "teacher_profile"):
            return redirect("teacher_dashboard")

        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            if hasattr(user, "teacher_profile"):
                return redirect("teacher_dashboard")

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(
        request,
        "accounts/login.html",
    )


@admin_required
def dashboard(request):
    students = Student.objects.all()

    total_students = Student.objects.count()
    total_course = Course.objects.count()

    return render(
        request,
        "dashboard.html",
        {
            "students": students,
            "total_students": total_students,
            "total_course": total_course,
        },
    )


@admin_required
def teacher_list(request):
    teachers = Teacher.objects.select_related(
        "user"
    ).order_by("name")

    return render(
        request,
        "accounts/teacher_list.html",
        {
            "teachers": teachers,
        },
    )


@admin_required
def teacher_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not name or not phone:
            messages.error(
                request,
                "Teacher name and phone number are required.",
            )

            return render(
                request,
                "accounts/teacher_form.html",
                {
                    "name": name,
                    "phone": phone,
                },
            )

        if Teacher.objects.filter(phone=phone).exists():
            messages.error(
                request,
                "A teacher with this phone number already exists.",
            )

            return render(
                request,
                "accounts/teacher_form.html",
                {
                    "name": name,
                    "phone": phone,
                },
            )

        if User.objects.filter(username=phone).exists():
            messages.error(
                request,
                "This phone number is already being used.",
            )

            return render(
                request,
                "accounts/teacher_form.html",
                {
                    "name": name,
                    "phone": phone,
                },
            )

        user = User.objects.create_user(
            username=phone,
        )

        user.first_name = name
        user.set_unusable_password()
        user.save()

        Teacher.objects.create(
            user=user,
            name=name,
            phone=phone,
        )

        messages.success(
            request,
            "Teacher added successfully.",
        )

        return redirect("teacher_list")

    return render(
        request,
        "accounts/teacher_form.html",
    )


# =========================
# TEACHER AUTHENTICATION
# =========================

def teacher_login(request):
    # Already logged in as teacher.
    if request.user.is_authenticated:
        if hasattr(request.user, "teacher_profile"):
            return redirect("teacher_dashboard")

        # Admin should not be able to enter teacher area.
        messages.info(
            request,
            "You are already logged in as an administrator.",
        )

        return redirect("dashboard")

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()

        try:
            teacher = Teacher.objects.select_related(
                "user"
            ).get(phone=phone)

        except Teacher.DoesNotExist:
            messages.error(
                request,
                "No teacher account was found with this phone number.",
            )

            return render(
                request,
                "accounts/teacher_login.html",
            )

        if not teacher.password_set:
            request.session["teacher_setup_id"] = teacher.id

            return redirect("teacher_set_password")

        return render(
            request,
            "accounts/teacher_password_login.html",
            {
                "phone": phone,
            },
        )

    return render(
        request,
        "accounts/teacher_login.html",
    )


def teacher_set_password(request):
    teacher_id = request.session.get("teacher_setup_id")

    if not teacher_id:
        return redirect("teacher_login")

    try:
        teacher = Teacher.objects.select_related(
            "user"
        ).get(id=teacher_id)

    except Teacher.DoesNotExist:
        request.session.pop("teacher_setup_id", None)

        return redirect("teacher_login")

    if teacher.password_set:
        request.session.pop("teacher_setup_id", None)

        return redirect("teacher_login")

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        if len(password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters.",
            )

            return render(
                request,
                "accounts/teacher_set_password.html",
                {
                    "teacher": teacher,
                },
            )

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match.",
            )

            return render(
                request,
                "accounts/teacher_set_password.html",
                {
                    "teacher": teacher,
                },
            )

        teacher.user.set_password(password)
        teacher.user.save()

        teacher.password_set = True
        teacher.save(
            update_fields=["password_set"]
        )

        request.session.pop(
            "teacher_setup_id",
            None,
        )

        login(
            request,
            teacher.user,
        )

        return redirect("teacher_dashboard")

    return render(
        request,
        "accounts/teacher_set_password.html",
        {
            "teacher": teacher,
        },
    )


def teacher_password_login(request):
    if request.method != "POST":
        return redirect("teacher_login")

    phone = request.POST.get("phone", "").strip()
    password = request.POST.get("password", "")

    try:
        teacher = Teacher.objects.select_related(
            "user"
        ).get(phone=phone)

    except Teacher.DoesNotExist:
        messages.error(
            request,
            "Invalid phone number or password.",
        )

        return redirect("teacher_login")

    user = authenticate(
        request,
        username=teacher.user.username,
        password=password,
    )

    if user is not None:
        login(request, user)

        return redirect("teacher_dashboard")

    messages.error(
        request,
        "Invalid phone number or password.",
    )

    return render(
        request,
        "accounts/teacher_password_login.html",
        {
            "phone": phone,
        },
    )


@teacher_required
def teacher_dashboard(request):
    teacher = request.user.teacher_profile

    return render(
        request,
        "accounts/teacher_dashboard.html",
        {
            "teacher": teacher,
        },
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):
    logout(request)

    return redirect("login")