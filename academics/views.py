from django.shortcuts import render, redirect, get_object_or_404

from .models import Course, Subject
from .forms import CourseForm, SubjectForm
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
