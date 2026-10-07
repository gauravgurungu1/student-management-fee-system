from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Course, Subject, Room, ClassSchedule
from .forms import CourseForm, SubjectForm, RoomForm, ClassScheduleForm

from accounts.decorators import admin_required


# =========================
# COURSE CRUD
# =========================

# READ - Show all courses
@admin_required
def course_list(request):
    courses = Course.objects.all()
    return render(
        request,
        'academics/course_list.html',
        {'courses': courses}
    )


# CREATE - Add a new course
@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(
        request,
        'academics/course_form.html',
        {'form': form}
    )


# UPDATE - Edit an existing course
@admin_required
def course_update(request, id):
    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)

        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)

    return render(
        request,
        'academics/course_form.html',
        {'form': form}
    )


# DELETE - Delete an existing course
@admin_required
def course_delete(request, id):
    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        course.delete()
        return redirect('course_list')

    return render(
        request,
        'academics/course_confirm_delete.html',
        {'course': course}
    )


# =========================
# SUBJECT CRUD
# =========================

# READ - Show all subjects
@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related('course').all()

    return render(
        request,
        'academics/subject_list.html',
        {'subjects': subjects}
    )


# CREATE - Add a new subject
@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()

    return render(
        request,
        'academics/subject_form.html',
        {'form': form}
    )


# UPDATE - Edit an existing subject
@admin_required
def subject_update(request, id):
    subject = get_object_or_404(Subject, id=id)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)

    return render(
        request,
        'academics/subject_form.html',
        {'form': form}
    )


# DELETE - Delete an existing subject
@admin_required
def subject_delete(request, id):
    subject = get_object_or_404(Subject, id=id)

    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')

    return render(
        request,
        'academics/subject_confirm_delete.html',
        {'subject': subject}
    )

def room_list(request):
    rooms = Room.objects.all()

    return render(
        request,
        "academics/room_list.html",
        {
            "rooms": rooms,
        },
    )


def room_create(request):
    if request.method == "POST":
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Room added successfully.",
            )

            return redirect("room_list")

    else:
        form = RoomForm()

    return render(
        request,
        "academics/room_form.html",
        {
            "form": form,
        },
    )


def room_update(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Room updated successfully.",
            )

            return redirect("room_list")

    else:
        form = RoomForm(instance=room)

    return render(
        request,
        "academics/room_form.html",
        {
            "form": form,
            "room": room,
        },
    )


def room_delete(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        room.delete()

        messages.success(
            request,
            "Room deleted successfully.",
        )

        return redirect("room_list")

    return render(
        request,
        "academics/room_confirm_delete.html",
        {
            "room": room,
        },
    )

def class_schedule_list(request):
    schedules = ClassSchedule.objects.select_related(
        "teacher",
        "subject",
        "subject__course",
        "room",
    )

    return render(
        request,
        "academics/class_schedule_list.html",
        {
            "schedules": schedules,
        },
    )


def class_schedule_create(request):
    if request.method == "POST":
        form = ClassScheduleForm(request.POST)

        if form.is_valid():
            schedule = form.save()

            messages.success(
                request,
                "Class schedule created successfully.",
            )

            return redirect("class_schedule_list")

    else:
        form = ClassScheduleForm()

    return render(
        request,
        "academics/class_schedule_form.html",
        {
            "form": form,
        },
    )


def class_schedule_update(request, schedule_id):
    schedule = get_object_or_404(
        ClassSchedule,
        id=schedule_id,
    )

    if request.method == "POST":
        form = ClassScheduleForm(
            request.POST,
            instance=schedule,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Class schedule updated successfully.",
            )

            return redirect("class_schedule_list")

    else:
        form = ClassScheduleForm(
            instance=schedule,
        )

    return render(
        request,
        "academics/class_schedule_form.html",
        {
            "form": form,
            "schedule": schedule,
        },
    )


def class_schedule_delete(request, schedule_id):
    schedule = get_object_or_404(
        ClassSchedule,
        id=schedule_id,
    )

    if request.method == "POST":
        schedule.delete()

        messages.success(
            request,
            "Class schedule deleted successfully.",
        )

        return redirect("class_schedule_list")

    return render(
        request,
        "academics/class_schedule_confirm_delete.html",
        {
            "schedule": schedule,
        },
    )