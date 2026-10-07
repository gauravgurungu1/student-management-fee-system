import json

from django.db.models import Count, Q
from django.shortcuts import render

from accounts.decorators import admin_required
from accounts.models import Teacher
from academics.models import Course, Subject
from attendance.models import AttendanceRecord, AttendanceSession
from students.models import Student


@admin_required
def report_dashboard(request):
    """
    Admin reports dashboard.

    Includes:
    - Overall system statistics
    - Students by course
    - Attendance overview
    - Student search and course filtering
    - Recent attendance sessions
    """

    # =========================================================
    # STUDENT FILTERS
    # =========================================================

    search_query = request.GET.get("search", "").strip()
    course_id = request.GET.get("course", "").strip()

    students = (
        Student.objects
        .select_related("course")
        .all()
    )

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    if course_id.isdigit():
        students = students.filter(course_id=course_id)
    else:
        course_id = ""

    students = students.order_by("name")

    # =========================================================
    # SUMMARY STATISTICS
    # =========================================================

    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()
    total_subjects = Subject.objects.count()

    # =========================================================
    # STUDENTS BY COURSE
    # =========================================================

    course_summary = (
        Course.objects
        .annotate(student_count=Count("students"))
        .order_by("name")
    )

    course_chart_labels = [
        course.name
        for course in course_summary
    ]

    course_chart_data = [
        course.student_count
        for course in course_summary
    ]

    # =========================================================
    # ATTENDANCE OVERVIEW
    # =========================================================

    total_present = AttendanceRecord.objects.filter(
        status="PRESENT"
    ).count()

    total_absent = AttendanceRecord.objects.filter(
        status="ABSENT"
    ).count()

    total_attendance_records = (
        total_present + total_absent
    )

    if total_attendance_records:
        attendance_percentage = round(
            (total_present / total_attendance_records) * 100,
            1,
        )
    else:
        attendance_percentage = 0

    # =========================================================
    # RECENT ATTENDANCE SESSIONS
    # =========================================================

    recent_sessions = (
        AttendanceSession.objects
        .select_related(
            "subject",
            "course",
            "teacher",
        )
        .order_by("-date", "-created_at")[:10]
    )

    # Add attendance statistics to each session.
    for session in recent_sessions:
        session.present_count = session.records.filter(
            status="PRESENT"
        ).count()

        session.absent_count = session.records.filter(
            status="ABSENT"
        ).count()

        session.total_count = (
            session.present_count
            + session.absent_count
        )

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        # Students
        "students": students,
        "courses": Course.objects.order_by("name"),
        "course_summary": course_summary,

        # Summary cards
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_courses": total_courses,
        "total_subjects": total_subjects,

        # Student filters
        "search_query": search_query,
        "selected_course": course_id,
        "filters_applied": bool(
            search_query or course_id
        ),

        # Course chart
        "course_chart_labels": json.dumps(
            course_chart_labels
        ),
        "course_chart_data": json.dumps(
            course_chart_data
        ),

        # Attendance chart
        "total_present": total_present,
        "total_absent": total_absent,
        "attendance_percentage": attendance_percentage,

        "attendance_chart_data": json.dumps([
            total_present,
            total_absent,
        ]),

        # Attendance sessions
        "recent_sessions": recent_sessions,
    }

    return render(
        request,
        "reports/report_dashboard.html",
        context,
    )