from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import teacher_required
from accounts.models import TeacherAssignment

from students.models import Student

from .models import AttendanceRecord, AttendanceSession

from academics.models import ClassSchedule





@teacher_required
def attendance_list(request):
    teacher = request.user.teacher_profile

    assignments = (
        TeacherAssignment.objects
        .select_related("subject", "subject__course")
        .filter(teacher=teacher)
    )

    sessions = (
        AttendanceSession.objects
        .select_related(
            "subject",
            "course",
        )
        .filter(teacher=request.user)
    )


    context = {
        "assignments": assignments,
        "sessions": sessions,
    }

    return render(
        request,
        "attendance/attendance_list.html",
        context,
    )


@teacher_required
def attendance_create(request):
    teacher = request.user.teacher_profile

    assignments = (
        TeacherAssignment.objects
        .select_related(
            "subject",
            "subject__course",
        )
        .filter(teacher=teacher)
    )

    today = timezone.localdate()

    if request.method == "POST":
        assignment_id = request.POST.get("assignment")
        date_value = request.POST.get("date")

        assignment = get_object_or_404(
            assignments,
            id=assignment_id,
        )

        if not date_value:
            messages.error(
                request,
                "Please select an attendance date.",
            )
            return redirect("attendance_create")

        try:
            attendance_date = timezone.datetime.strptime(
                date_value,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            messages.error(
                request,
                "Invalid attendance date.",
            )
            return redirect("attendance_create")

        # Future dates are never allowed.
        if attendance_date > today:
            messages.error(
                request,
                "You cannot take attendance for a future date.",
            )
            return redirect("attendance_create")

        # The teacher must actually have this class scheduled
        # on the selected date.
        weekday = attendance_date.strftime("%A").upper()

        schedule_exists = ClassSchedule.objects.filter(
            teacher=teacher,
            subject=assignment.subject,
            batch=assignment.batch,
            day=weekday,
        ).exists()

        if not schedule_exists:
            messages.error(
                request,
                f"You are not scheduled to teach "
                f"{assignment.subject.name} for Batch "
                f"{assignment.batch} on {attendance_date.strftime('%A')}.",
            )
            return redirect("attendance_create")

        # Prevent duplicate attendance.
        existing_session = AttendanceSession.objects.filter(
            subject=assignment.subject,
            batch=assignment.batch,
            date=attendance_date,
        ).first()

        if existing_session:
            messages.warning(
                request,
                "Attendance has already been created for this "
                "subject, batch, and date.",
            )
            return redirect(
                "attendance_mark",
                session_id=existing_session.id,
            )

        students = Student.objects.filter(
            course=assignment.subject.course,
            batch=assignment.batch,
        ).order_by("name")

        if not students.exists():
            messages.error(
                request,
                "No students were found for this course and batch.",
            )
            return redirect("attendance_create")

        session = AttendanceSession.objects.create(
            course=assignment.subject.course,
            batch=assignment.batch,
            subject=assignment.subject,
            date=attendance_date,
            teacher=request.user,
        )


        AttendanceRecord.objects.bulk_create(
            [
                AttendanceRecord(
                    session=session,
                    student=student,
                    status="PRESENT",
                )
                for student in students
            ]
        )

        return redirect(
            "attendance_mark",
            session_id=session.id,
        )

    return render(
        request,
        "attendance/attendance_create.html",
        {
            "assignments": assignments,
            "today": today,
        },
    )


@teacher_required
def attendance_mark(request, session_id):
    session = get_object_or_404(
        AttendanceSession.objects.select_related(
            "subject",
            "course",
            "teacher",
        ),
        id=session_id,
        teacher=request.user,
    )

    records = (
        AttendanceRecord.objects
        .select_related("student")
        .filter(session=session)
    )

    if request.method == "POST":

        with transaction.atomic():

            for record in records:
                status = request.POST.get(
                    f"status_{record.id}"
                )

                if status in {"PRESENT", "ABSENT"}:
                    record.status = status
                    record.save(
                        update_fields=[
                            "status",
                            "marked_at",
                        ]
                    )

        messages.success(
            request,
            "Attendance saved successfully.",
        )

        return redirect(
            "attendance_mark",
            session_id=session.id,
        )

    present_count = records.filter(
        status="PRESENT"
    ).count()

    absent_count = records.filter(
        status="ABSENT"
    ).count()

    return render(
        request,
        "attendance/attendance_mark.html",
        {
            "session": session,
            "records": records,
            "present_count": present_count,
            "absent_count": absent_count,
        },
    )


@teacher_required
def attendance_delete(request, session_id):
    session = get_object_or_404(
        AttendanceSession.objects.select_related(
            "subject",
            "course",
        ),
        id=session_id,
        teacher=request.user,
    )

    if request.method == "POST":
        session.delete()

        messages.success(
            request,
            "Attendance deleted successfully.",
        )

        return redirect("attendance_list")

    return render(
        request,
        "attendance/attendance_confirm_delete.html",
        {"session": session},
    )

@teacher_required
def scheduled_attendance_create(request, schedule_id):
    teacher = request.user.teacher_profile

    schedule = get_object_or_404(
        ClassSchedule.objects.select_related(
            "subject",
            "subject__course",
            "room",
        ),
        id=schedule_id,
        teacher=teacher,
    )

    today = timezone.localdate()

    # The scheduled class must be for today.
    if schedule.day != today.strftime("%A").upper():
        messages.error(
            request,
            f"This class is scheduled for {schedule.get_day_display()}, "
            f"not today.",
        )
        return redirect("teacher_classes")

    # Prevent attendance from being created twice.
    existing_session = AttendanceSession.objects.filter(
        subject=schedule.subject,
        batch=schedule.batch,
        date=today,
    ).first()

    if existing_session:
        messages.warning(
            request,
            "Attendance has already been created for this class today.",
        )
        return redirect(
            "attendance_mark",
            session_id=existing_session.id,
        )

    students = Student.objects.filter(
        course=schedule.subject.course,
        batch=schedule.batch,
    ).order_by("name")

    if not students.exists():
        messages.error(
            request,
            "No students were found for this course and batch.",
        )
        return redirect("teacher_classes")

    if request.method == "POST":
        session = AttendanceSession.objects.create(
            course=schedule.subject.course,
            batch=schedule.batch,
            subject=schedule.subject,
            date=today,
            teacher=request.user,
        )

        AttendanceRecord.objects.bulk_create(
            [
                AttendanceRecord(
                    session=session,
                    student=student,
                    status="PRESENT",
                )
                for student in students
            ]
        )

        return redirect(
            "attendance_mark",
            session_id=session.id,
        )

    return render(
        request,
        "attendance/scheduled_attendance_create.html",
        {
            "schedule": schedule,
            "students": students,
            "today": today,
        },
    )