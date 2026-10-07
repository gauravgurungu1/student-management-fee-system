from decimal import Decimal

from django.db.models import Case, When, IntegerField, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render

from academics.models import Course
from students.models import Student
from attendance.models import AttendanceRecord
from fees.models import Fee
from payments.models import Payment

from .forms import TeacherAssignmentForm
from .models import Teacher, TeacherAssignment
from .decorators import admin_required, teacher_required


# =========================
# PUBLIC HOME
# =========================

def home(request):
    if request.user.is_authenticated:

        if hasattr(request.user, "teacher_profile"):
            return redirect("teacher_dashboard")

        return redirect("dashboard")

    return render(
        request,
        "accounts/home.html",
    )


# =========================
# ADMINISTRATOR
# =========================

def login_view(request):
    if request.user.is_authenticated:

        if hasattr(request.user, "teacher_profile"):
            return redirect("teacher_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

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


# =========================
# ADMIN DASHBOARD
# =========================

@admin_required
def dashboard(request):

    # =========================
    # STUDENTS
    # =========================

    total_students = Student.objects.count()

    # Show only the latest 15 students.
    # Student model does not have created_at,
    # so ID is used to determine the latest records.
    students = (
        Student.objects
        .select_related("course")
        .order_by("-id")[:15]
    )


    # =========================
    # COURSES
    # =========================

    total_course = Course.objects.count()


    # =========================
    # TEACHERS
    # =========================

    total_teachers = Teacher.objects.count()


    # =========================
    # ATTENDANCE
    # =========================

    total_attendance_records = (
        AttendanceRecord.objects.count()
    )

    total_present_records = (
        AttendanceRecord.objects
        .filter(status="PRESENT")
        .count()
    )

    if total_attendance_records > 0:

        attendance_percentage = round(
            (
                total_present_records
                / total_attendance_records
            ) * 100,
            1,
        )

    else:

        attendance_percentage = 0


    # =========================
    # FEES
    # =========================

    total_fee_amount = (
        Fee.objects
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0")
    )


    # =========================
    # COMPLETED PAYMENTS
    # =========================

    completed_payment_queryset = (
        Payment.objects
        .filter(status="COMPLETED")
    )

    total_paid_amount = (
        completed_payment_queryset
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0")
    )

    completed_payments = (
        completed_payment_queryset.count()
    )


    # =========================
    # OUTSTANDING FEES
    # =========================

    total_due_amount = (
        total_fee_amount
        - total_paid_amount
    )

    if total_due_amount < 0:
        total_due_amount = Decimal("0")


    # =========================
    # DASHBOARD
    # =========================

    return render(
        request,
        "dashboard.html",
        {
            # Students
            "students": students,
            "total_students": total_students,

            # Teachers
            "total_teachers": total_teachers,

            # Courses
            "total_course": total_course,

            # Attendance
            "attendance_percentage": attendance_percentage,

            # Fees
            "total_fee_amount": total_fee_amount,
            "total_paid_amount": total_paid_amount,
            "total_due_amount": total_due_amount,

            # Payments
            "completed_payments": completed_payments,
        },
    )


# =========================
# TEACHER MANAGEMENT
# =========================

@admin_required
def teacher_list(request):

    teachers = (
        Teacher.objects
        .select_related("user")
        .order_by("name")
    )

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

        name = request.POST.get(
            "name",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()


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


        if Teacher.objects.filter(
            phone=phone
        ).exists():

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


        if User.objects.filter(
            username=phone
        ).exists():

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

        return redirect(
            "teacher_list"
        )


    return render(
        request,
        "accounts/teacher_form.html",
    )


# =========================
# TEACHER ASSIGNMENTS
# =========================

@admin_required
def teacher_assignment_list(request):

    assignments = (
        TeacherAssignment.objects
        .select_related(
            "teacher",
            "subject",
            "subject__course",
        )
    )

    return render(
        request,
        "accounts/teacher_assignment_list.html",
        {
            "assignments": assignments,
        },
    )


@admin_required
def teacher_assignment_create(request):

    if request.method == "POST":

        form = TeacherAssignmentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Teacher assignment created successfully.",
            )

            return redirect(
                "teacher_assignment_list"
            )

    else:

        form = TeacherAssignmentForm()


    return render(
        request,
        "accounts/teacher_assignment_form.html",
        {
            "form": form,
        },
    )


@admin_required
def teacher_assignment_delete(
    request,
    assignment_id,
):

    assignment = (
        TeacherAssignment.objects
        .select_related(
            "teacher",
            "subject",
            "subject__course",
        )
        .get(id=assignment_id)
    )


    if request.method == "POST":

        assignment.delete()

        messages.success(
            request,
            "Teacher assignment removed successfully.",
        )

        return redirect(
            "teacher_assignment_list"
        )


    return render(
        request,
        "accounts/teacher_assignment_confirm_delete.html",
        {
            "assignment": assignment,
        },
    )


# =========================
# TEACHER AUTHENTICATION
# =========================

def teacher_login(request):

    # Already logged in as teacher.
    if request.user.is_authenticated:

        if hasattr(
            request.user,
            "teacher_profile",
        ):

            return redirect(
                "teacher_dashboard"
            )


        messages.info(
            request,
            "You are already logged in as an administrator.",
        )

        return redirect(
            "dashboard"
        )


    if request.method == "POST":

        action = request.POST.get(
            "action",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()


        try:

            teacher = (
                Teacher.objects
                .select_related("user")
                .get(phone=phone)
            )

        except Teacher.DoesNotExist:

            messages.error(
                request,
                "No teacher account was found with this phone number.",
            )

            return render(
                request,
                "accounts/teacher_login.html",
                {
                    "phone": phone,
                },
            )


        # =========================
        # CREATE PASSWORD
        # =========================

        if action == "create_password":

            if teacher.password_set:

                messages.error(
                    request,
                    "A password has already been created for this account.",
                )

                return render(
                    request,
                    "accounts/teacher_login.html",
                    {
                        "phone": phone,
                        "password_set": True,
                    },
                )


            password = request.POST.get(
                "new_password",
                "",
            )

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
                    "accounts/teacher_login.html",
                    {
                        "phone": phone,
                        "password_set": False,
                    },
                )


            if password != confirm_password:

                messages.error(
                    request,
                    "Passwords do not match.",
                )

                return render(
                    request,
                    "accounts/teacher_login.html",
                    {
                        "phone": phone,
                        "password_set": False,
                    },
                )


            teacher.user.set_password(
                password
            )

            teacher.user.save()


            teacher.password_set = True

            teacher.save(
                update_fields=[
                    "password_set"
                ]
            )


            login(
                request,
                teacher.user,
            )

            return redirect(
                "teacher_dashboard"
            )


        # =========================
        # PASSWORD LOGIN
        # =========================

        if action == "login":

            password = request.POST.get(
                "password",
                "",
            )


            user = authenticate(
                request,
                username=teacher.user.username,
                password=password,
            )


            if user is not None:

                login(
                    request,
                    user,
                )

                return redirect(
                    "teacher_dashboard"
                )


            messages.error(
                request,
                "Incorrect password.",
            )

            return render(
                request,
                "accounts/teacher_login.html",
                {
                    "phone": phone,
                    "password_set": True,
                },
            )


        # =========================
        # INVALID ACTION
        # =========================

        messages.error(
            request,
            "Invalid login request.",
        )


    return render(
        request,
        "accounts/teacher_login.html",
    )


# =========================
# CHECK TEACHER PHONE
# =========================

def check_teacher_phone(request):

    phone = request.GET.get(
        "phone",
        "",
    ).strip()


    if not phone:

        return JsonResponse({
            "registered": False,
            "empty": True,
        })


    try:

        teacher = Teacher.objects.get(
            phone=phone
        )

    except Teacher.DoesNotExist:

        return JsonResponse({
            "registered": False,
            "empty": False,
        })


    return JsonResponse({
        "registered": True,
        "password_set": teacher.password_set,
        "empty": False,
    })


# =========================
# TEACHER DASHBOARD
# =========================

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
# TEACHER SUBJECTS
# =========================

@teacher_required
def teacher_subjects(request):

    teacher = request.user.teacher_profile


    assignments = (
        TeacherAssignment.objects
        .select_related(
            "subject",
            "subject__course",
        )
        .filter(
            teacher=teacher
        )
        .order_by(
            "subject__course__name",
            "subject__semester",
            "subject__code",
            "batch",
        )
    )


    return render(
        request,
        "accounts/teacher_subjects.html",
        {
            "teacher": teacher,
            "assignments": assignments,
        },
    )


# =========================
# TEACHER CLASSES
# =========================

@teacher_required
def teacher_classes(request):

    teacher = request.user.teacher_profile


    day_order = Case(

        When(
            day="SUNDAY",
            then=0,
        ),

        When(
            day="MONDAY",
            then=1,
        ),

        When(
            day="TUESDAY",
            then=2,
        ),

        When(
            day="WEDNESDAY",
            then=3,
        ),

        When(
            day="THURSDAY",
            then=4,
        ),

        When(
            day="FRIDAY",
            then=5,
        ),

        When(
            day="SATURDAY",
            then=6,
        ),

        output_field=IntegerField(),
    )


    schedules = (
        teacher.class_schedules
        .select_related(
            "subject",
            "subject__course",
            "room",
        )
        .annotate(
            day_order=day_order
        )
        .order_by(
            "day_order",
            "start_time",
        )
    )


    assignments = TeacherAssignment.objects.filter(
        teacher=teacher
    )


    assignment_map = {
        (
            assignment.subject_id,
            assignment.batch,
        ): assignment.id

        for assignment in assignments
    }


    days = [

        {
            "key": "SUNDAY",
            "name": "Sunday",
            "classes": [],
        },

        {
            "key": "MONDAY",
            "name": "Monday",
            "classes": [],
        },

        {
            "key": "TUESDAY",
            "name": "Tuesday",
            "classes": [],
        },

        {
            "key": "WEDNESDAY",
            "name": "Wednesday",
            "classes": [],
        },

        {
            "key": "THURSDAY",
            "name": "Thursday",
            "classes": [],
        },

        {
            "key": "FRIDAY",
            "name": "Friday",
            "classes": [],
        },

        {
            "key": "SATURDAY",
            "name": "Saturday",
            "classes": [],
        },

    ]


    for schedule in schedules:

        schedule.assignment_id = assignment_map.get(
            (
                schedule.subject_id,
                schedule.batch,
            )
        )


        for day in days:

            if day["key"] == schedule.day:

                day["classes"].append(
                    schedule
                )

                break


    return render(
        request,
        "accounts/teacher_classes.html",
        {
            "teacher": teacher,
            "days": days,
        },
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect(
        "home"
    )