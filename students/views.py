from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from academics.models import Course
from .models import Student
from .forms import StudentForm
from accounts.decorators import admin_required


# READ - Show all students (with optional search + course filter)
@admin_required
def student_list(request):
    students = Student.objects.select_related('course').all()

    search_query = request.GET.get('search', '').strip()
    course_id = request.GET.get('course', '').strip()

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) | Q(email__icontains=search_query)
        )

    if course_id.isdigit():
        students = students.filter(course_id=course_id)
    elif course_id:
        # Non-numeric/garbage course value in the query string: ignore it
        # rather than letting the ORM raise, and drop it from the sticky UI.
        course_id = ''

    students = students.order_by('name')

    context = {
        'students': students,
        'courses': Course.objects.order_by('name'),
        'search_query': search_query,
        'selected_course': course_id,
        'filters_applied': bool(search_query or course_id),
    }
    return render(request, 'students/student_list.html', context)


# CREATE - Add a new student
@admin_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("student_list")
    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {
        "form": form
    })


# UPDATE - Edit an existing student
@admin_required
def student_update(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {'form': form})


# DELETE - Delete a student
@admin_required
def student_delete(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()
        return redirect('student_list')

    return render(
        request,
        'students/student_confirm_delete.html',
        {'student': student}
    )